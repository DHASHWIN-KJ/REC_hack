"""
Sanity check: does our preprocessing feed the model exactly what it expects?

ASVspoof files are already 16 kHz mono FLAC, i.e. the model's native input.
For a few real and fake files this script scores each one twice:
  A) loaded directly with soundfile (no processing at all, the "ground truth")
  B) through our full pipeline (hash -> ffmpeg -> FLAC archive -> load)
If preprocessing is correct, A and B give (almost) identical audio and scores.

    python -m src.audio.check_preprocessing --protocol data\\keys\\DF\\CM\\trial_metadata.txt ^
           --audio-dir data\\ASVspoof2021_DF_eval\\flac --n 10
"""
import argparse
import random

import numpy as np
import soundfile as sf

from .config import get_config
from .detector import score_waveform, to_probability
from .evaluate import read_protocol
from .preprocess import prepare_audio


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--audio-dir", required=True)
    ap.add_argument("--n", type=int, default=10, help="number of files (half real, half fake)")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args(argv)

    cfg = get_config()
    items = [it for it in read_protocol(args.protocol, args.audio_dir, subset="eval") if it[0].exists()]
    random.seed(args.seed)
    real = [i for i in items if i[1] == 0]
    fake = [i for i in items if i[1] == 1]
    picked = random.sample(real, min(args.n // 2, len(real))) + random.sample(fake, min(args.n // 2, len(fake)))
    if not picked:
        raise SystemExit("No files found. Check --protocol and --audio-dir.")

    print(f"Settings: sample_rate={cfg.sample_rate}, trim_silence={cfg.trim_silence}, "
          f"calibrated={cfg.calibrated}\n")
    print(f"{'file':20s} {'truth':5s} {'sr':>6s} {'len_A':>7s} {'len_B':>7s} {'max_diff':>9s} "
          f"{'score_A':>8s} {'score_B':>8s} {'p_fake':>7s} {'ok':>3s}")

    problems, score_diffs, correct, unreadable = [], [], 0, []
    for path, label, _ in picked:
        try:
            wav_a, sr = sf.read(str(path), dtype="float32")
            if wav_a.ndim > 1:
                wav_a = wav_a.mean(axis=1)
            prep = prepare_audio(path, cfg)
        except Exception as exc:
            # A broken source file is a dataset problem, not a preprocessing problem.
            unreadable.append(f"{path.name}: {exc}")
            print(f"{path.stem:20s} {'fake' if label else 'real':5s}  UNREADABLE (corrupt or incomplete file)")
            continue
        wav_b = prep.waveform

        n = min(len(wav_a), len(wav_b))
        max_diff = float(np.max(np.abs(wav_a[:n] - wav_b[:n]))) if n else float("nan")
        s_a = score_waveform(wav_a, cfg)["overall_score"]
        s_b = score_waveform(wav_b, cfg)["overall_score"]
        p = float(to_probability(s_b, cfg, prep.is_trimmed))
        predicted_fake = p >= 0.5
        is_correct = predicted_fake == bool(label)
        correct += is_correct
        score_diffs.append(abs(s_a - s_b))

        if sr != cfg.sample_rate:
            problems.append(f"{path.name}: source sample rate {sr}, expected {cfg.sample_rate}")
        if not cfg.trim_silence and len(wav_a) != len(wav_b):
            problems.append(f"{path.name}: length changed {len(wav_a)} -> {len(wav_b)}")
        if max_diff > 1e-3:
            problems.append(f"{path.name}: audio changed by preprocessing (max diff {max_diff:.4f})")

        print(f"{path.stem:20s} {'fake' if label else 'real':5s} {sr:6d} {len(wav_a):7d} {len(wav_b):7d} "
              f"{max_diff:9.5f} {s_a:8.3f} {s_b:8.3f} {p:7.3f} {'yes' if is_correct else 'NO':>3s}")

    if unreadable:
        print(f"\n{len(unreadable)} unreadable source file(s) skipped (dataset problem, see notes):")
        for u in unreadable:
            print("  - " + u)
    if not score_diffs:
        raise SystemExit("No readable files to compare.")
    print(f"\nLargest score difference A vs B: {max(score_diffs):.4f}")
    print(f"Correct (at p=0.5): {correct}/{len(score_diffs)}")
    if problems:
        print("\nPROBLEMS FOUND:")
        for p in problems:
            print("  - " + p)
    elif max(score_diffs) < 0.05:
        print("\nPASS: preprocessing gives the model the same input as the original files.")
    else:
        print("\nWARNING: audio matches but scores differ; check the model is in eval mode.")


if __name__ == "__main__":
    main()