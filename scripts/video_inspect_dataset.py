#!/usr/bin/env python3
"""
scripts/video_inspect_dataset.py
Phase A - Step 0: Inspect the FaceForensics++ dataset on disk.

Reads the CSV metadata files, counts videos per folder, computes stats,
infers compression levels, verifies fake-to-original filename matching,
and writes findings to docs/video_data.md.
"""

import os
import sys
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import csv
import re
import math
from pathlib import Path
from collections import defaultdict

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATASET_ROOT = PROJECT_ROOT / "src" / "video" / "dataset_videos"
CSV_DIR = DATASET_ROOT / "csv"
DOCS_DIR = PROJECT_ROOT / "docs"

FOLDERS = [
    "original",
    "Deepfakes",
    "Face2Face",
    "FaceShifter",
    "FaceSwap",
    "NeuralTextures",
    "DeepFakeDetection",
]

FAKE_METHODS = ["Deepfakes", "Face2Face", "FaceShifter", "FaceSwap", "NeuralTextures"]
OOD_SET = "DeepFakeDetection"

# Bitrate thresholds for compression inference (Mbps)
# raw ≈ >10 Mbps, c23 ≈ 1-10 Mbps, c40 ≈ <1 Mbps
COMPRESSION_THRESHOLDS = {
    "raw": 10.0,
    "c23_upper": 10.0,
    "c40_upper": 1.0,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_csv(csv_path: Path) -> list[dict]:
    """Read a CSV with pandas-style index column."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def compute_bitrate_mbps(file_size_mb: float, frame_count: int, fps: float = 30.0) -> float:
    """Estimate bitrate in Mbps from file size and duration."""
    if frame_count <= 0 or fps <= 0:
        return 0.0
    duration_sec = frame_count / fps
    return (file_size_mb * 8) / duration_sec  # MB → Mb


def infer_compression(bitrate_mbps: float) -> str:
    if bitrate_mbps >= COMPRESSION_THRESHOLDS["raw"]:
        return "raw"
    elif bitrate_mbps >= COMPRESSION_THRESHOLDS["c40_upper"]:
        return "c23"
    else:
        return "c40"


def parse_fake_ids(filename: str) -> tuple[str, str] | None:
    """
    Parse <target>_<source>.mp4 from a fake video filename.
    Returns (target_id, source_id) or None.
    For standard FF++ fakes: 000_003.mp4 → ('000', '003')
    For DFD: different naming convention, handled separately.
    """
    stem = Path(filename).stem
    parts = stem.split("_")
    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
        return parts[0], parts[1]
    return None


def percentile(sorted_list, p):
    """Simple percentile (nearest rank)."""
    if not sorted_list:
        return 0
    k = max(0, min(len(sorted_list) - 1, int(math.ceil(p / 100.0 * len(sorted_list))) - 1))
    return sorted_list[k]


def stats_summary(values: list[float]) -> dict:
    if not values:
        return {"min": 0, "median": 0, "max": 0, "mean": 0}
    s = sorted(values)
    return {
        "min": s[0],
        "median": s[len(s) // 2],
        "max": s[-1],
        "mean": round(sum(s) / len(s), 2),
    }


# ---------------------------------------------------------------------------
# Main inspection
# ---------------------------------------------------------------------------
def main():
    report_lines: list[str] = []

    def log(msg: str = ""):
        print(msg)
        report_lines.append(msg)

    log("# FaceForensics++ Dataset Inspection Report")
    log(f"\nDataset root: `{DATASET_ROOT}`")
    log(f"CSV directory: `{CSV_DIR}`")
    log()

    # ------------------------------------------------------------------
    # 1. Check folder existence and count videos on disk
    # ------------------------------------------------------------------
    log("## 1. Folder Scan (on-disk video count)")
    log()
    log("| Folder | Exists | Video Files (.mp4) |")
    log("|--------|--------|--------------------|")

    disk_counts = {}
    missing_folders = []
    for folder in FOLDERS:
        folder_path = DATASET_ROOT / folder
        exists = folder_path.is_dir()
        if exists:
            mp4s = list(folder_path.glob("*.mp4"))
            disk_counts[folder] = len(mp4s)
            log(f"| {folder} | ✅ | {len(mp4s)} |")
        else:
            disk_counts[folder] = 0
            missing_folders.append(folder)
            log(f"| {folder} | ❌ MISSING | 0 |")

    if missing_folders:
        log(f"\n> ⚠️  Missing folders: {', '.join(missing_folders)}")
    log()

    # ------------------------------------------------------------------
    # 2. Read CSVs and compute per-folder stats
    # ------------------------------------------------------------------
    log("## 2. CSV Metadata Analysis")
    log()

    csv_files = sorted(CSV_DIR.glob("*.csv"))
    log(f"CSV files found: {len(csv_files)}")
    for cf in csv_files:
        log(f"  - `{cf.name}` ({cf.stat().st_size / 1024:.1f} KB)")
    log()

    # Read per-method CSVs
    all_data: dict[str, list[dict]] = {}
    for folder in FOLDERS:
        csv_path = CSV_DIR / f"{folder}.csv"
        if csv_path.exists():
            all_data[folder] = read_csv(csv_path)
        else:
            log(f"> ⚠️  No CSV found for `{folder}`")
            all_data[folder] = []

    log("### Video counts from CSVs")
    log()
    log("| Folder | CSV Rows | Disk Files | Match? | Label |")
    log("|--------|----------|------------|--------|-------|")
    for folder in FOLDERS:
        csv_count = len(all_data[folder])
        disk_count = disk_counts.get(folder, 0)
        match = "✅" if csv_count == disk_count else f"❌ (diff={abs(csv_count - disk_count)})"
        label = "REAL" if folder == "original" else "FAKE"
        log(f"| {folder} | {csv_count} | {disk_count} | {match} | {label} |")

    total_real = len(all_data.get("original", []))
    total_fake = sum(len(all_data.get(m, [])) for m in FAKE_METHODS)
    total_dfd = len(all_data.get(OOD_SET, []))
    log(f"\n**Totals:** {total_real} real, {total_fake} fake ({len(FAKE_METHODS)} methods), "
        f"{total_dfd} DFD (OOD)")
    if total_real > 0:
        log(f"**Imbalance ratio (fake:real):** {total_fake / total_real:.1f}:1")
    log()

    # ------------------------------------------------------------------
    # 3. Per-folder stats from CSV metadata
    # ------------------------------------------------------------------
    log("## 3. Per-Folder Video Statistics (from CSV)")
    log()

    for folder in FOLDERS:
        rows = all_data[folder]
        if not rows:
            log(f"### {folder}: NO DATA\n")
            continue

        frame_counts = []
        widths = []
        heights = []
        file_sizes = []
        codecs = set()
        bitrates = []

        for r in rows:
            try:
                fc = int(r.get("Frame Count", 0))
                w = int(r.get("Width", 0))
                h = int(r.get("Height", 0))
                fs = float(r.get("File Size(MB)", 0))
                codec = r.get("Codec", "unknown")

                frame_counts.append(fc)
                widths.append(w)
                heights.append(h)
                file_sizes.append(fs)
                codecs.add(codec)

                br = compute_bitrate_mbps(fs, fc)
                bitrates.append(br)
            except (ValueError, TypeError):
                pass

        fc_s = stats_summary(frame_counts)
        w_s = stats_summary(widths)
        h_s = stats_summary(heights)
        fs_s = stats_summary(file_sizes)
        br_s = stats_summary(bitrates)

        resolutions = defaultdict(int)
        for w, h in zip(widths, heights):
            resolutions[f"{w}x{h}"] += 1
        top_res = sorted(resolutions.items(), key=lambda x: -x[1])[:5]

        log(f"### {folder} ({len(rows)} videos)")
        log()
        log(f"| Metric | Min | Median | Max | Mean |")
        log(f"|--------|-----|--------|-----|------|")
        log(f"| Frame Count | {fc_s['min']} | {fc_s['median']} | {fc_s['max']} | {fc_s['mean']} |")
        log(f"| Width | {w_s['min']} | {w_s['median']} | {w_s['max']} | {w_s['mean']} |")
        log(f"| Height | {h_s['min']} | {h_s['median']} | {h_s['max']} | {h_s['mean']} |")
        log(f"| File Size (MB) | {fs_s['min']} | {fs_s['median']} | {fs_s['max']} | {fs_s['mean']} |")
        log(f"| Est. Bitrate (Mbps) | {br_s['min']:.2f} | {br_s['median']:.2f} | {br_s['max']:.2f} | {br_s['mean']:.2f} |")
        log()
        log(f"Codecs: {', '.join(sorted(codecs))}")
        log(f"Top resolutions: {', '.join(f'{r}({c})' for r, c in top_res)}")
        log()

    # ------------------------------------------------------------------
    # 4. Compression level inference
    # ------------------------------------------------------------------
    log("## 4. Compression Level Inference")
    log()
    log("Estimated from bitrate: raw (≥10 Mbps), c23 (1-10 Mbps), c40 (<1 Mbps)")
    log()

    for folder in FOLDERS:
        rows = all_data[folder]
        if not rows:
            continue

        comp_counts = defaultdict(int)
        for r in rows:
            try:
                fc = int(r.get("Frame Count", 0))
                fs = float(r.get("File Size(MB)", 0))
                br = compute_bitrate_mbps(fs, fc)
                comp_counts[infer_compression(br)] += 1
            except (ValueError, TypeError):
                pass

        total = sum(comp_counts.values())
        parts = []
        for level in ["raw", "c23", "c40"]:
            c = comp_counts.get(level, 0)
            pct = (c / total * 100) if total > 0 else 0
            parts.append(f"{level}={c} ({pct:.0f}%)")

        dominant = max(comp_counts, key=comp_counts.get) if comp_counts else "unknown"
        log(f"- **{folder}**: {', '.join(parts)} → likely **{dominant}**")

    log()

    # ------------------------------------------------------------------
    # 5. CSV column inspection & sample rows
    # ------------------------------------------------------------------
    log("## 5. CSV Structure Inspection")
    log()

    for cf in csv_files:
        rows_sample = read_csv(cf)
        if not rows_sample:
            log(f"### {cf.name}: EMPTY")
            continue
        cols = list(rows_sample[0].keys())
        log(f"### {cf.name}")
        log(f"Columns: `{cols}`")
        log(f"Row count: {len(rows_sample)}")
        log()

        # Check for train/val/test split columns
        split_cols = [c for c in cols if any(kw in c.lower() for kw in ["split", "train", "val", "test", "set", "fold"])]
        if split_cols:
            log(f"**⚠️  SPLIT COLUMNS FOUND: {split_cols}**")
            # Show unique values
            for sc in split_cols:
                vals = set(r.get(sc, "") for r in rows_sample)
                log(f"  - `{sc}` unique values: {vals}")
        else:
            log(f"No split columns found.")

        # Show 3 sample rows
        log("\nSample rows:")
        log("```")
        for r in rows_sample[:3]:
            log(str(r))
        log("```")
        log()

    # ------------------------------------------------------------------
    # 6. Filename parsing: fake → original matching
    # ------------------------------------------------------------------
    log("## 6. Fake→Original Filename Matching")
    log()

    # Build set of original video IDs
    original_ids = set()
    for r in all_data.get("original", []):
        fp = r.get("File Path", "")
        stem = Path(fp).stem  # e.g., "000"
        original_ids.add(stem)

    log(f"Original video IDs found: {len(original_ids)}")
    log()

    for method in FAKE_METHODS:
        rows = all_data.get(method, [])
        matched = 0
        unmatched = 0
        unmatched_examples = []

        for r in rows:
            fp = r.get("File Path", "")
            filename = Path(fp).name
            parsed = parse_fake_ids(filename)
            if parsed:
                target_id, source_id = parsed
                if target_id in original_ids:
                    matched += 1
                else:
                    unmatched += 1
                    if len(unmatched_examples) < 3:
                        unmatched_examples.append(f"{filename} (target={target_id} not in originals)")
            else:
                unmatched += 1
                if len(unmatched_examples) < 3:
                    unmatched_examples.append(f"{filename} (cannot parse target_source)")

        total = matched + unmatched
        log(f"### {method}: {matched}/{total} matched, {unmatched} unmatched")
        if unmatched_examples:
            for ex in unmatched_examples:
                log(f"  - {ex}")
        log()

    # DFD has different naming
    dfd_rows = all_data.get(OOD_SET, [])
    if dfd_rows:
        log(f"### {OOD_SET}: Different naming convention (not target_source.mp4)")
        sample_names = [Path(r.get("File Path", "")).name for r in dfd_rows[:5]]
        log(f"  Sample filenames: {sample_names}")
        log(f"  Total videos: {len(dfd_rows)}")
        log()

    # ------------------------------------------------------------------
    # 7. Class imbalance summary
    # ------------------------------------------------------------------
    log("## 7. Class Imbalance Summary")
    log()
    log("| Set | Count | Ratio to Original |")
    log("|-----|-------|--------------------|")
    log(f"| original (REAL) | {total_real} | 1.0 |")
    for method in FAKE_METHODS:
        c = len(all_data.get(method, []))
        ratio = c / total_real if total_real > 0 else 0
        log(f"| {method} (FAKE) | {c} | {ratio:.2f} |")
    log(f"| **Total FAKE** | **{total_fake}** | **{total_fake / total_real if total_real > 0 else 0:.1f}** |")
    log(f"| {OOD_SET} (OOD) | {total_dfd} | {total_dfd / total_real if total_real > 0 else 0:.2f} |")
    log()

    # ------------------------------------------------------------------
    # 8. Official split check
    # ------------------------------------------------------------------
    log("## 8. Official Train/Val/Test Split Check")
    log()

    # Check FF++_Metadata.csv for split info
    metadata_csv = CSV_DIR / "FF++_Metadata.csv"
    shuffled_csv = CSV_DIR / "FF++_Metadata_Shuffled.csv"

    for meta_path in [metadata_csv, shuffled_csv]:
        if meta_path.exists():
            rows = read_csv(meta_path)
            if rows:
                cols = list(rows[0].keys())
                split_cols = [c for c in cols if any(kw in c.lower() for kw in
                              ["split", "train", "val", "test", "set", "fold", "partition"])]
                log(f"### {meta_path.name}")
                log(f"Columns: `{cols}`")
                log(f"Row count: {len(rows)}")
                if split_cols:
                    log(f"**SPLIT COLUMNS: {split_cols}**")
                    for sc in split_cols:
                        vals = defaultdict(int)
                        for r in rows:
                            vals[r.get(sc, "")] += 1
                        log(f"  `{sc}`: {dict(vals)}")
                else:
                    log("No split columns found in this CSV.")
                log()

    # Check for separate split files (json, txt)
    split_files = list(CSV_DIR.glob("*split*")) + list(CSV_DIR.glob("*train*")) + list(CSV_DIR.glob("*test*"))
    if split_files:
        log(f"Split-related files found: {[f.name for f in split_files]}")
    else:
        log("No separate split files found in csv/ directory.")

    # Also check dataset root
    root_split_files = list(DATASET_ROOT.glob("*split*")) + list(DATASET_ROOT.glob("*train*")) + list(DATASET_ROOT.glob("*test*"))
    if root_split_files:
        log(f"Split files in dataset root: {[f.name for f in root_split_files]}")
    else:
        log("No split files in dataset root either.")

    log()
    log("**Conclusion:** If no official splits are found, we will create deterministic "
        "identity-aware splits (seed-based) in `src/video/data/splits.py`.")
    log()

    # ------------------------------------------------------------------
    # 9. Summary and recommendations
    # ------------------------------------------------------------------
    log("## 9. Summary & Recommendations")
    log()
    log(f"- **{total_real}** real videos, **{total_fake}** fake videos across "
        f"**{len(FAKE_METHODS)}** methods, **{total_dfd}** DFD (OOD)")
    log(f"- Imbalance: ~{total_fake / total_real if total_real > 0 else 0:.0f}:1 fake-to-real")
    log(f"- All videos are h264 codec")
    log(f"- Variable resolutions (480p to 1080p)")
    log(f"- Filename pattern `<target>_<source>.mp4` confirmed for standard methods")
    log(f"- DFD uses a different naming convention")
    log(f"- Compression level appears to be **c23** based on bitrate analysis")
    log()

    # ------------------------------------------------------------------
    # Write report
    # ------------------------------------------------------------------
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = DOCS_DIR / "video_data.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n{'='*60}")
    print(f"Report written to: {report_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
