"""
Turn raw model scores into trustworthy probabilities.

Fits  P(fake) = sigmoid(a * score + b)  on scores CSVs from evaluate.py and
writes src/audio/calibration.json, which config.py loads automatically.

Two separate calibrations are kept:
  default : normal audio            python -m src.audio.calibrate scores_df.csv
  trimmed : edge-to-edge speech      python -m src.audio.calibrate scores_hidden.csv --condition trimmed

By default each condition is fitted only on the files evaluate.py detected as
that condition (column trimmed_detected). Use --use-all to fit on every row.
"""
import argparse
import csv
import json
from datetime import datetime

import numpy as np

from .config import CALIBRATION_FILE


def load_scores(paths, condition=None):
    """condition: None (all rows), 'default' (untrimmed rows) or 'trimmed'."""
    labels, scores = [], []
    for p in paths:
        with open(p) as f:
            for row in csv.DictReader(f):
                if condition and row.get("trimmed_detected", "") != "":
                    is_trim = row["trimmed_detected"] == "1"
                    if is_trim != (condition == "trimmed"):
                        continue
                labels.append(1 if row["label"] == "fake" else 0)
                scores.append(float(row["score"]))
    return np.array(labels), np.array(scores)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_files", nargs="+")
    ap.add_argument("--genuine-below", type=float, default=0.30)
    ap.add_argument("--fake-above", type=float, default=0.70)
    ap.add_argument("--condition", choices=["default", "trimmed"], default="default")
    ap.add_argument("--use-all", action="store_true",
                    help="fit on every row instead of only rows detected as this condition")
    args = ap.parse_args(argv)

    from sklearn.linear_model import LogisticRegression

    y, s = load_scores(args.csv_files, None if args.use_all else args.condition)
    if len(set(y)) < 2:
        raise SystemExit(f"Need both real and fake examples for condition '{args.condition}'. "
                         "Try --use-all, or check the trimmed_detected column.")

    # class_weight balances real/fake so the probabilities aren't skewed by
    # ASVspoof's ~9:1 fake-to-real ratio.
    lr = LogisticRegression(class_weight="balanced")
    lr.fit(s.reshape(-1, 1), y)
    a, b = float(lr.coef_[0][0]), float(lr.intercept_[0])
    p = 1 / (1 + np.exp(-(a * s + b)))

    fake_band = p >= args.fake_above
    real_band = p <= args.genuine_below
    unsure = ~(fake_band | real_band)
    decided = ~unsure
    correct = (fake_band & (y == 1)) | (real_band & (y == 0))

    print(f"[{args.condition}] Fitted on {len(y)} files ({(y == 0).sum()} real / {(y == 1).sum()} fake)")
    print(f"  a = {a:.4f}, b = {b:.4f}")
    print(f"  'uncertain' band holds {unsure.mean() * 100:.1f}% of files")
    if decided.any():
        print(f"  accuracy on confident decisions: {correct[decided].mean() * 100:.1f}%")
    print("  Tip: if too many files land in 'uncertain', narrow the band with "
          "--genuine-below / --fake-above.")

    data = {}
    if CALIBRATION_FILE.exists():
        try:
            data = json.loads(CALIBRATION_FILE.read_text())
        except json.JSONDecodeError:
            data = {}
        if "a" in data and "default" not in data:   # migrate old format
            data = {"default": data}
    data[args.condition] = {
        "a": a, "b": b,
        "threshold_genuine": args.genuine_below,
        "threshold_fake": args.fake_above,
        "fitted_on": args.csv_files,
        "n_files": int(len(y)),
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    CALIBRATION_FILE.write_text(json.dumps(data, indent=2))
    print(f"Saved '{args.condition}' calibration to {CALIBRATION_FILE}")


if __name__ == "__main__":
    main()