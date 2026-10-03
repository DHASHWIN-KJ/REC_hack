"""
Try different settings on existing score files (no re-scoring needed) to pick
the best minimum clip length and 'likely fake' threshold.

    python -m src.audio.sweep v_baseline.csv v_whatsapp.csv v_hidden.csv t4_crop1s.csv

For each combination it shows, per file: correct / uncertain / false alarms / misses.
Good settings keep false alarms low without making too many results 'uncertain'.
"""
import argparse
from pathlib import Path

from .config import get_config
from .report import load_csv, operational, pct


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_files", nargs="+")
    ap.add_argument("--min-lengths", default="0,1.0,1.2,1.5")
    ap.add_argument("--fake-thresholds", default="0.7,0.8,0.9")
    args = ap.parse_args(argv)

    cfg = get_config()
    data = {Path(p).stem: load_csv(p) for p in args.csv_files}
    mins = [float(x) for x in args.min_lengths.split(",")]
    thrs = [float(x) for x in args.fake_thresholds.split(",")]
    orig = (cfg.min_speech_seconds, cfg.threshold_fake)

    for name, rows in data.items():
        print(f"\n=== {name} ===")
        print(f"{'min_len':>7s} {'fake>=':>6s} {'Correct':>8s} {'Unsure':>7s} {'FalseAl':>8s} {'Miss':>7s}")
        for m in mins:
            for t in thrs:
                cfg.min_speech_seconds, cfg.threshold_fake = m, t
                op = operational(rows, cfg)
                mark = "  <- current" if (m, t) == orig else ""
                print(f"{m:7.1f} {t:6.2f} {pct(op['correct']):>8s} {pct(op['uncertain']):>7s} "
                      f"{pct(op['false_alarm']):>8s} {pct(op['miss']):>7s}{mark}")
    cfg.min_speech_seconds, cfg.threshold_fake = orig
    print("\nTo apply a choice: set min_speech_seconds in config.py, and the fake threshold with\n"
          "  python -m src.audio.calibrate <csvs> --condition default --fake-above <value>  (and the same for trimmed)")


if __name__ == "__main__":
    main()
