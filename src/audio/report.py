"""
Capability report from evaluate.py score files.

    python -m src.audio.report scores_eval.csv scores_opus.csv scores_noise10.csv --md capability_report.md

For every CSV it prints:
  * EER (ranking quality, independent of thresholds)
  * What a user would actually see with the current calibration and thresholds:
      correct, uncertain, false alarms (real called fake), misses (fake called real)
  * Breakdowns by codec, vocoder type, clip duration and trimmed/normal audio
A summary table across all CSVs is printed at the end (ready for slides).
"""
import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

from .config import get_config
from .detector import to_probability
from .evaluate import compute_eer

MIN_GROUP = 10  # groups smaller than this are marked as unreliable


def load_csv(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["y"] = 1 if r["label"] == "fake" else 0
        r["score"] = float(r["score"])
        r["trimmed"] = r.get("trimmed_detected", "0") == "1"
        r["duration"] = float(r["duration"]) if r.get("duration") else None
    return rows


def operational(rows, cfg):
    """Fractions of correct / uncertain / false alarm / miss using calibrated verdicts."""
    if not rows:
        return None
    counts = defaultdict(int)
    for r in rows:
        p = float(to_probability(r["score"], cfg, r["trimmed"]))
        too_short = r["duration"] is not None and r["duration"] < cfg.min_speech_seconds
        if too_short:
            verdict = "uncertain"            # same minimum-length rule as detector.py
        elif r["trimmed"] and not cfg.trim_calibrated and p >= cfg.threshold_fake:
            verdict = "uncertain"            # same safety rule as detector.py
        elif p >= cfg.threshold_fake:
            verdict = "fake"
        elif p <= cfg.threshold_genuine:
            verdict = "real"
        else:
            verdict = "uncertain"
        truth = "fake" if r["y"] else "real"
        if verdict == "uncertain":
            counts["uncertain"] += 1
        elif verdict == truth:
            counts["correct"] += 1
        elif truth == "real":
            counts["false_alarm"] += 1
        else:
            counts["miss"] += 1
    n_real = sum(1 for r in rows if r["y"] == 0)
    n_fake = len(rows) - n_real
    return {
        "correct": counts["correct"] / len(rows),
        "uncertain": counts["uncertain"] / len(rows),
        # rates relative to their own class, which is what matters to users
        "false_alarm": counts["false_alarm"] / n_real if n_real else float("nan"),
        "miss": counts["miss"] / n_fake if n_fake else float("nan"),
    }


def eer_of(rows):
    y = np.array([r["y"] for r in rows])
    if len(set(y)) < 2:
        return None
    return compute_eer(y, np.array([r["score"] for r in rows]))[0]


def pct(x):
    return "n/a" if x is None or x != x else f"{x * 100:.1f}%"


def group_table(rows, key_fn, title, spoof_vs_all_real=False):
    """
    spoof_vs_all_real: for attributes only fakes have (vocoder type), compare
    each group's fakes against ALL real clips.
    """
    groups = defaultdict(list)
    for r in rows:
        k = key_fn(r)
        if k:
            groups[k].append(r)
    if spoof_vs_all_real:
        reals = [r for r in rows if r["y"] == 0]
        groups = {k: v + reals for k, v in groups.items() if k != "bonafide" and any(x["y"] for x in v)}
    if len(groups) < 2:
        return []
    lines = [f"\n  By {title}:"]
    out = []
    for k in sorted(groups):
        g = groups[k]
        e = eer_of(g)
        n = len(g) if not spoof_vs_all_real else sum(1 for r in g if r["y"] == 1)
        flag = "  (few files)" if n < MIN_GROUP else ""
        lines.append(f"    {k:32s} n={n:5d}  EER {pct(e)}{flag}")
        out.append((k, n, e))
    print("\n".join(lines))
    return out


def duration_bucket(r):
    d = r["duration"]
    if d is None:
        return None
    if d < 2:
        return "a) under 2 s"
    if d < 4:
        return "b) 2-4 s"
    if d < 8:
        return "c) 4-8 s"
    return "d) over 8 s"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_files", nargs="+")
    ap.add_argument("--md", help="also write a Markdown report to this file")
    args = ap.parse_args(argv)

    cfg = get_config()
    print(f"Calibration: default={'yes' if cfg.calibrated else 'NO'}, "
          f"trimmed={'yes' if cfg.trim_calibrated else 'NO'} | thresholds "
          f"real<={cfg.threshold_genuine} fake>={cfg.threshold_fake} | "
          f"min clip length {cfg.min_speech_seconds}s")

    summary = []
    md = ["# Audio deepfake detector: capability report\n"]
    for path in args.csv_files:
        rows = load_csv(path)
        name = Path(path).stem
        n_real = sum(1 for r in rows if r["y"] == 0)
        e = eer_of(rows)
        op = operational(rows, cfg)
        print(f"\n=== {name}  ({len(rows)} files: {n_real} real / {len(rows) - n_real} fake) ===")
        print(f"  EER {pct(e)} | correct {pct(op['correct'])} | uncertain {pct(op['uncertain'])} | "
              f"false alarms {pct(op['false_alarm'])} | misses {pct(op['miss'])}")
        summary.append((name, len(rows), e, op))

        md.append(f"\n## {name}\n\n{len(rows)} files ({n_real} real / {len(rows) - n_real} fake). "
                  f"EER **{pct(e)}**, correct {pct(op['correct'])}, uncertain {pct(op['uncertain'])}, "
                  f"false alarms {pct(op['false_alarm'])}, misses {pct(op['miss'])}.\n")
        for title, fn, svr in (
            ("codec", lambda r: r.get("codec") or None, False),
            ("vocoder type (fakes vs all real)", lambda r: r.get("vocoder") or None, True),
            ("clip duration", duration_bucket, False),
            ("audio condition", lambda r: "trimmed" if r["trimmed"] else "normal", False),
        ):
            res = group_table(rows, fn, title, svr)
            if res:
                md.append(f"\n**By {title}**\n\n| Group | Files | EER |\n|---|---|---|")
                md += [f"| {k} | {n}{' (few)' if n < MIN_GROUP else ''} | {pct(x)} |" for k, n, x in res]
                md.append("")

    header = f"\n{'Test':28s} {'Files':>6s} {'EER':>7s} {'Correct':>8s} {'Unsure':>7s} {'FalseAl':>8s} {'Miss':>7s}"
    print("\n=== SUMMARY ===" + header)
    md.append("\n## Summary\n\n| Test | Files | EER | Correct | Uncertain | False alarms | Misses |\n"
              "|---|---|---|---|---|---|---|")
    for name, n, e, op in summary:
        print(f"{name:28s} {n:6d} {pct(e):>7s} {pct(op['correct']):>8s} {pct(op['uncertain']):>7s} "
              f"{pct(op['false_alarm']):>8s} {pct(op['miss']):>7s}")
        md.append(f"| {name} | {n} | {pct(e)} | {pct(op['correct'])} | {pct(op['uncertain'])} | "
                  f"{pct(op['false_alarm'])} | {pct(op['miss'])} |")

    if args.md:
        Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"\nMarkdown report written to {args.md}")


if __name__ == "__main__":
    main()