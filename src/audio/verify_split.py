"""
Verify the real/fake split made by split_asvspoof.py.

For N random files from every folder (eval/real, eval/fake, hidden/real, ...):
  1. the original file exists in --audio-dir
  2. the split file is byte-for-byte identical to the original (SHA-256)
  3. the label in the key file matches the folder it was put in
  4. (optional, --with-model) what the detector predicts for it

    python -m src.audio.verify_split --protocol data\\keys\\DF\\CM\\trial_metadata.txt ^
           --audio-dir data\\ASVspoof2021_DF_eval\\flac --split-dir data\\asvspoof_split --n 5 --with-model
"""
import argparse
import random
from pathlib import Path

from .preprocess import sha256_file
from .split_asvspoof import parse_key_line


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--audio-dir", required=True, help="original extracted folder")
    ap.add_argument("--split-dir", required=True, help="output folder of split_asvspoof")
    ap.add_argument("--n", type=int, default=5, help="samples per folder")
    ap.add_argument("--with-model", action="store_true", help="also run the detector on each sample")
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args(argv)

    keys = {}
    with open(args.protocol, encoding="utf-8") as f:
        for line in f:
            m = parse_key_line(line)
            if m:
                keys[m["file_id"]] = m

    split_dir, audio_dir = Path(args.split_dir), Path(args.audio_dir)
    folders = sorted({p.parent for p in split_dir.rglob("*.flac")})
    if not folders:
        raise SystemExit(f"No .flac files found under {split_dir}")

    analyze = None
    if args.with_model:
        from .detector import analyze_audio
        analyze = lambda p: analyze_audio(p, include_plot=False, include_saliency=False)

    random.seed(args.seed)
    checked, problems = 0, []
    for folder in folders:
        rel = folder.relative_to(split_dir)
        parts = rel.parts                      # e.g. ('eval', 'fake', 'traditional_vocoder')
        folder_subset, folder_label = parts[0], parts[1] if len(parts) > 1 else "?"
        files = sorted(folder.glob("*.flac"))
        sample = random.sample(files, min(args.n, len(files)))

        print(f"\n=== {rel}  ({len(files)} files, checking {len(sample)}) ===")
        header = f"{'file':16s} {'original':8s} {'same_bytes':10s} {'key_label':9s} {'key_subset':10s} {'match':5s}"
        if analyze:
            header += f" {'verdict':15s} {'p_fake':>6s}"
        print(header)

        for p in sample:
            fid = p.stem
            orig = audio_dir / p.name
            key = keys.get(fid)
            has_orig = orig.exists()
            same = has_orig and sha256_file(orig) == sha256_file(p)
            key_label = key["label"] if key else "MISSING"
            key_subset = key["subset"] if key else "MISSING"
            match = key is not None and key_label == folder_label and key_subset == folder_subset
            line = (f"{fid:16s} {'yes' if has_orig else 'NO':8s} {'yes' if same else 'NO':10s} "
                    f"{key_label:9s} {key_subset:10s} {'OK' if match and same else 'FAIL':5s}")
            if analyze:
                try:
                    r = analyze(p)
                    line += f" {r['verdict']:15s} {r['fake_probability']:6.3f}"
                except Exception as exc:
                    line += f" error: {exc}"
            print(line)

            checked += 1
            if not has_orig:
                problems.append(f"{rel}/{p.name}: original not found in --audio-dir")
            elif not same:
                problems.append(f"{rel}/{p.name}: content differs from original")
            if not match:
                problems.append(f"{rel}/{p.name}: key says {key_label}/{key_subset}, folder says "
                                f"{folder_label}/{folder_subset}")

    print(f"\nChecked {checked} files in {len(folders)} folders.")
    if problems:
        print("PROBLEMS:")
        for pr in problems:
            print("  - " + pr)
    else:
        print("PASS: every sampled file is identical to its original and sits in the folder its key label says.")


if __name__ == "__main__":
    main()
