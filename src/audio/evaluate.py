"""
Evaluate the detector and compute EER (Equal Error Rate).

Two modes:

1) ASVspoof protocol (sample a subset, the full DF eval set is huge):
   python -m src.audio.evaluate --protocol keys/DF/CM/trial_metadata.txt \
          --audio-dir data/ASVspoof2021_DF_eval/flac --limit 2000 --out scores_df.csv

2) Simple folders (e.g. your Tamil test set):
   python -m src.audio.evaluate --real-dir data/tamil/real --fake-dir data/tamil/fake \
          --out scores_tamil.csv

Stress tests (combine freely):
   --codec opus --bitrate 16k     simulate WhatsApp / social-media compression
   --noise-snr 10                 add background noise at 10 dB SNR (lower = noisier)
   --crop-seconds 2               keep only the middle 2 s (short-clip test)

Break the results down afterwards with:  python -m src.audio.report scores.csv
"""
import argparse
import csv
import os
import random
import sys
import time
from pathlib import Path

import numpy as np

from .config import get_config
from .detector import score_waveform
from .preprocess import (decode_to_array, find_speech_bounds, is_trimmed_audio,
                         measure_edge_silence, simulate_codec)

AUDIO_EXTS = {".flac", ".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac", ".mp4", ".webm"}


def compute_eer(labels, scores):
    """labels: 1 = fake, 0 = real. scores: higher = more fake. Returns (eer, threshold)."""
    from sklearn.metrics import roc_curve
    fpr, tpr, thr = roc_curve(labels, scores, pos_label=1)
    fnr = 1 - tpr
    idx = np.nanargmin(np.abs(fnr - fpr))
    return float((fpr[idx] + fnr[idx]) / 2), float(thr[idx])


def read_protocol(protocol_path, audio_dir, ext=".flac", subset=None):
    """
    Works with ASVspoof 2019/2021 key files: finds the file id and bonafide/spoof label.
    subset: keep only rows tagged 'eval', 'progress' or 'hidden' (ASVspoof 2021 keys).
    The 'hidden' rows have silence trimmed and are a deliberately hard special case.
    """
    items = []
    with open(protocol_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            label = 1 if "spoof" in parts else 0 if "bonafide" in parts else None
            if label is None:
                continue
            if subset and subset not in parts:
                continue
            file_id = parts[1]
            meta = {
                "key_trim": True if "trim" in parts else False if "notrim" in parts else None,
                # ASVspoof 2021 DF/LA key columns: speaker file codec source attack label trim subset vocoder ...
                "codec": parts[2] if len(parts) > 2 else "",
                "source": parts[3] if len(parts) > 3 else "",
                "attack": parts[4] if len(parts) > 4 else "",
                "vocoder": parts[8] if len(parts) > 8 else "",
            }
            items.append((Path(audio_dir) / f"{file_id}{ext}", label, meta))
    return items


def read_folders(real_dir, fake_dir):
    items = []
    for d, label in ((real_dir, 0), (fake_dir, 1)):
        for p in sorted(Path(d).rglob("*")):
            if p.suffix.lower() in AUDIO_EXTS:
                items.append((p, label, {"key_trim": None, "codec": "", "source": Path(d).name,
                                         "attack": "", "vocoder": ""}))
    return items


def add_noise(wav, snr_db, seed=0):
    """White noise at the given signal-to-noise ratio (dB)."""
    rng = np.random.default_rng(seed)
    sig_power = np.mean(wav ** 2) + 1e-12
    noise = rng.standard_normal(len(wav)).astype(np.float32)
    noise *= np.sqrt(sig_power / (10 ** (snr_db / 10)) / (np.mean(noise ** 2) + 1e-12))
    return np.clip(wav + noise, -1.0, 1.0).astype(np.float32)


def center_crop(wav, seconds, sr):
    n = int(seconds * sr)
    if len(wav) <= n:
        return wav
    start = (len(wav) - n) // 2
    return wav[start:start + n]


def load_for_eval(path, cfg, codec=None, bitrate="16k", trim=True,
                  noise_snr=None, crop_seconds=None, seed=0):
    tmp = None
    try:
        if codec:
            tmp = simulate_codec(path, codec, bitrate)
            path = tmp
        wav = decode_to_array(path, cfg.sample_rate)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    if crop_seconds:
        wav = center_crop(wav, crop_seconds, cfg.sample_rate)
    if noise_snr is not None:
        wav = add_noise(wav, noise_snr, seed)
    lead, trail = measure_edge_silence(wav, cfg.sample_rate)
    if trim:
        s, e, _ = find_speech_bounds(wav, cfg.sample_rate, cfg.vad_threshold)
        if e > s:
            wav = wav[s:e]
    return wav, lead, trail


def main(argv=None):
    ap = argparse.ArgumentParser(description="Evaluate the audio deepfake detector (EER).")
    ap.add_argument("--protocol")
    ap.add_argument("--audio-dir")
    ap.add_argument("--real-dir")
    ap.add_argument("--fake-dir")
    ap.add_argument("--subset", choices=["eval", "progress", "hidden"],
                    help="ASVspoof 2021 only: evaluate one subset (use 'eval' for the main result)")
    ap.add_argument("--limit", type=int, default=0, help="random subset size (0 = all)")
    ap.add_argument("--balanced", action="store_true", help="sample equal real/fake counts")
    ap.add_argument("--codec", choices=["opus", "mp3", "aac"])
    ap.add_argument("--bitrate", default="16k")
    ap.add_argument("--noise-snr", type=float, help="add white noise at this SNR in dB")
    ap.add_argument("--crop-seconds", type=float, help="keep only the middle N seconds")
    ap.add_argument("--no-trim", action="store_true")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="scores.csv")
    args = ap.parse_args(argv)

    cfg = get_config()
    if args.protocol and args.audio_dir:
        items = read_protocol(args.protocol, args.audio_dir, subset=args.subset)
    elif args.real_dir and args.fake_dir:
        items = read_folders(args.real_dir, args.fake_dir)
    else:
        ap.error("Use --protocol + --audio-dir, or --real-dir + --fake-dir")

    items = [it for it in items if it[0].exists()]
    random.seed(args.seed)
    if args.limit and len(items) > args.limit:
        if args.balanced:
            real = [i for i in items if i[1] == 0]
            fake = [i for i in items if i[1] == 1]
            half = args.limit // 2
            items = random.sample(real, min(half, len(real))) + random.sample(fake, min(half, len(fake)))
        else:
            items = random.sample(items, args.limit)
    if not items:
        sys.exit("No audio files found. Check the paths.")

    print(f"Scoring {len(items)} files "
          f"({sum(1 for i in items if i[1] == 0)} real / {sum(1 for i in items if i[1] == 1)} fake)"
          f"{' | codec ' + args.codec + ' @ ' + args.bitrate if args.codec else ''}"
          f"{' | noise ' + str(args.noise_snr) + ' dB SNR' if args.noise_snr is not None else ''}"
          f"{' | crop ' + str(args.crop_seconds) + ' s' if args.crop_seconds else ''}")

    labels, scores, trims, key_trims, rows = [], [], [], [], []
    t0 = time.time()
    for n, (path, label, meta) in enumerate(items, 1):
        key_trim = meta["key_trim"]
        try:
            wav, lead, trail = load_for_eval(path, cfg, args.codec, args.bitrate,
                                             trim=cfg.trim_silence and not args.no_trim,
                                             noise_snr=args.noise_snr, crop_seconds=args.crop_seconds,
                                             seed=n)
            s = score_waveform(wav, cfg)["overall_score"]
        except Exception as exc:
            print(f"  skip {path.name}: {exc}")
            continue
        detected = is_trimmed_audio(lead, trail, len(wav) / cfg.sample_rate, cfg.trimmed_max_silence)
        labels.append(label)
        scores.append(s)
        trims.append(detected)
        key_trims.append(key_trim)
        rows.append((path.name, "fake" if label else "real", f"{s:.6f}",
                     f"{len(wav) / cfg.sample_rate:.2f}", f"{lead + trail:.3f}", int(detected),
                     "" if key_trim is None else int(key_trim),
                     meta["codec"], meta["source"], meta["attack"], meta["vocoder"]))
        if n % 50 == 0 or n == len(items):
            print(f"  {n}/{len(items)}  ({(time.time() - t0) / n:.2f}s per file)")

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "label", "score", "duration", "edge_silence", "trimmed_detected",
                    "key_trim", "codec", "source", "attack", "vocoder"])
        w.writerows(rows)

    if len(set(labels)) < 2:
        print("Need both real and fake files to compute EER.")
        return
    y, sc, tr = np.array(labels), np.array(scores), np.array(trims)
    eer, thr = compute_eer(y, sc)
    print(f"\nEER (all files): {eer * 100:.2f}%   (raw score threshold at EER: {thr:.3f})")

    # Breakdown by detected condition
    for name, mask in (("normal", ~tr), ("trimmed", tr)):
        if mask.sum() and len(set(y[mask])) == 2:
            e, t = compute_eer(y[mask], sc[mask])
            print(f"  {name:8s} audio: {mask.sum():5d} files, EER {e * 100:.2f}% (threshold {t:.3f})")
        elif mask.sum():
            print(f"  {name:8s} audio: {mask.sum():5d} files (one class only, no EER)")

    # How well does our trimmed-audio detector agree with the ASVspoof key?
    known = [(d, k) for d, k in zip(trims, key_trims) if k is not None]
    if known:
        agree = sum(d == k for d, k in known) / len(known)
        print(f"  trimmed-audio detector agrees with key on {agree * 100:.1f}% of files")
    print(f"Scores saved to {args.out}")


if __name__ == "__main__":
    main()