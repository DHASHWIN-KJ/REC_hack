"""
Split ASVspoof 2021 (DF or LA) audio into real/ and fake/ folders using the key file.

    python -m src.audio.split_asvspoof --protocol data\\keys\\DF\\CM\\trial_metadata.txt ^
           --audio-dir data\\ASVspoof2021_DF_eval\\flac --out data\\asvspoof_split

Result:
    data\\asvspoof_split\\eval\\real\\*.flac
    data\\asvspoof_split\\eval\\fake\\*.flac
    data\\asvspoof_split\\hidden\\real\\...   (silence-trimmed subset, kept separate)
    data\\asvspoof_split\\progress\\...
    data\\asvspoof_split\\labels.csv          (file, label, subset, codec, vocoder, ...)

Modes:
    link (default) : hard links, no extra disk space, originals untouched
    copy           : real copies (uses as much space again)
    move           : moves files (originals disappear from --audio-dir)
"""
import argparse
import csv
import os
import shutil
from collections import Counter
from pathlib import Path


def parse_key_line(line):
    parts = line.split()
    if len(parts) < 8:
        return None
    label = "fake" if "spoof" in parts else "real" if "bonafide" in parts else None
    if label is None:
        return None
    # speaker file codec source attack label trim subset vocoder ...
    return {
        "file_id": parts[1],
        "label": label,
        "speaker": parts[0],
        "codec": parts[2],
        "source": parts[3],
        "attack": parts[4],
        "trim": parts[6],
        "subset": parts[7],
        "vocoder": parts[8] if len(parts) > 8 else "",
    }


def place(src, dst, mode):
    if dst.exists():
        return "exists"
    if mode == "move":
        shutil.move(str(src), str(dst))
    elif mode == "copy":
        shutil.copy2(src, dst)
    else:
        try:
            os.link(src, dst)
        except OSError:
            shutil.copy2(src, dst)   # different drive / unsupported: fall back to copy
            return "copied"
    return "ok"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Split ASVspoof 2021 audio into real/fake folders.")
    ap.add_argument("--protocol", required=True, help="trial_metadata.txt from the keys archive")
    ap.add_argument("--audio-dir", required=True, help="folder with the extracted .flac files")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--subsets", default="eval,hidden,progress",
                    help="comma-separated subsets to include (default: all)")
    ap.add_argument("--mode", choices=["link", "copy", "move"], default="link")
    ap.add_argument("--by-vocoder", action="store_true",
                    help="put fakes in fake/<vocoder_type>/ subfolders")
    ap.add_argument("--ext", default=".flac")
    args = ap.parse_args(argv)

    audio_dir, out = Path(args.audio_dir), Path(args.out)
    wanted = {s.strip() for s in args.subsets.split(",") if s.strip()}
    counts, missing, fallback_copies = Counter(), 0, 0
    rows = []

    with open(args.protocol, encoding="utf-8") as f:
        for line in f:
            meta = parse_key_line(line)
            if meta is None or meta["subset"] not in wanted:
                continue
            src = audio_dir / f"{meta['file_id']}{args.ext}"
            if not src.exists():
                missing += 1          # file belongs to a part you didn't download
                continue
            folder = out / meta["subset"] / meta["label"]
            if args.by_vocoder and meta["label"] == "fake" and meta["vocoder"]:
                folder = folder / meta["vocoder"]
            folder.mkdir(parents=True, exist_ok=True)
            status = place(src, folder / src.name, args.mode)
            fallback_copies += status == "copied"
            counts[(meta["subset"], meta["label"])] += 1
            rows.append({**meta, "path": str((folder / src.name).relative_to(out))})

    with open(out / "labels.csv", "w", newline="", encoding="utf-8") as f:
        fields = ["file_id", "label", "subset", "codec", "vocoder", "source", "attack",
                  "trim", "speaker", "path"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    print(f"\nDone ({args.mode}). Files per folder:")
    for (subset, label), n in sorted(counts.items()):
        print(f"  {subset:9s} {label:5s} {n:7d}   -> {out / subset / label}")
    print(f"Total placed: {sum(counts.values())}")
    print(f"Listed in key but not in --audio-dir (other download parts): {missing}")
    if fallback_copies:
        print(f"Note: {fallback_copies} files were copied because hard links weren't possible.")
    print(f"Metadata table: {out / 'labels.csv'}")


if __name__ == "__main__":
    main()
