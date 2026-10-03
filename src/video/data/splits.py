"""
src/video/data/splits.py
Generates deterministic, identity-aware train/val/test splits for FaceForensics++.
Ensures that if an identity (e.g., '000') is in train, neither their real video 
nor ANY of their deepfakes appear in val or test.
"""
import os
import random
import csv
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple

from video.config_video import cfg, DATA_ROOT

# All possible source methods
METHODS = ["original", "Deepfakes", "Face2Face", "FaceShifter", "FaceSwap", "NeuralTextures"]
OOD_METHOD = "DeepFakeDetection"

def _parse_id(filename: str) -> str:
    """Extracts target ID from filename (e.g., '000_003.mp4' -> '000')."""
    stem = Path(filename).stem
    parts = stem.split("_")
    return parts[0]

def load_all_video_records(csv_dir: Path) -> Dict[str, List[dict]]:
    """Loads all metadata CSVs into a dictionary by method."""
    records = defaultdict(list)
    
    for method in METHODS + [OOD_METHOD]:
        csv_path = csv_dir / f"{method}.csv"
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                records[method] = list(reader)
    return records

def generate_splits(csv_dir: Path | str = None) -> Dict[str, List[dict]]:
    """
    Generates identity-aware splits.
    Returns: Dict with keys 'train', 'val', 'test', 'ood_test'.
    Each contains a list of dictionary records with at least:
      - 'video_path': str
      - 'label': 'REAL' | 'FAKE'
      - 'method': str
    """
    if csv_dir is None:
        csv_dir = DATA_ROOT / "csv"
    else:
        csv_dir = Path(csv_dir)
        
    records = load_all_video_records(csv_dir)
    
    # 1. Identify all unique target identities from the 'original' folder
    # e.g., '000.mp4' -> '000'
    unique_ids = set()
    for r in records.get("original", []):
        vid_id = _parse_id(r.get("File Path", ""))
        if vid_id:
            unique_ids.add(vid_id)
            
    # 2. Shuffle deterministically
    sorted_ids = sorted(list(unique_ids))
    random.seed(cfg.data.seed)
    random.shuffle(sorted_ids)
    
    # 3. Calculate split indices
    total = len(sorted_ids)
    train_end = int(total * cfg.data.split_ratios[0])
    val_end = train_end + int(total * cfg.data.split_ratios[1])
    
    train_ids = set(sorted_ids[:train_end])
    val_ids = set(sorted_ids[train_end:val_end])
    test_ids = set(sorted_ids[val_end:])
    
    splits = {
        "train": [],
        "val": [],
        "test": [],
        "ood_test": []
    }
    
    # 4. Map videos to their assigned split based on target ID
    for method in METHODS:
        for r in records.get(method, []):
            vid_id = _parse_id(r.get("File Path", ""))
            
            # Reformat record for dataset loader
            clean_record = {
                "video_path": r.get("File Path", ""),
                "label": r.get("Label", ""),
                "method": method
            }
            
            if vid_id in train_ids:
                splits["train"].append(clean_record)
            elif vid_id in val_ids:
                splits["val"].append(clean_record)
            elif vid_id in test_ids:
                splits["test"].append(clean_record)
                
    # 5. Add all DFD videos to ood_test
    for r in records.get(OOD_METHOD, []):
        splits["ood_test"].append({
            "video_path": r.get("File Path", ""),
            "label": r.get("Label", ""),
            "method": OOD_METHOD
        })
        
    return splits
