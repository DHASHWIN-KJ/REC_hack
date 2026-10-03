#!/usr/bin/env python3
"""
scripts/video_extract_embeddings.py
Pre-computes embeddings for all videos in the dataset and saves them to disk as .pt files.
This caching step is CRITICAL for rapid iteration on the fusion network later.
Supports resuming from crashes/interruptions.
"""

import sys
import os
import torch
from pathlib import Path
from tqdm import tqdm

# Add src to python path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from video.config_video import cfg, DATA_ROOT
from video.data.splits import generate_splits
from video.frames import extract_faces_from_video
from video.data.augmentation import get_val_transforms
from video.branches import FeatureExtractorManager

def extract_and_save_embeddings(dataset_dir: Path, output_dir: Path, device: str = "cuda"):
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading feature extractors to {device}...")
    manager = FeatureExtractorManager().to(device)
    
    # We use val transforms (deterministic normalization, no random augmentation) for caching
    transform = get_val_transforms(target_size=224)
    
    splits = generate_splits(dataset_dir / "csv")
    
    # Flatten all records to process them sequentially
    all_records = []
    for split_name, records in splits.items():
        all_records.extend(records)
        
    print(f"Found {len(all_records)} total videos across all splits.")
    
    # Track stats
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for record in tqdm(all_records, desc="Extracting Embeddings"):
        video_rel_path = Path(record["video_path"])
        video_full_path = dataset_dir / video_rel_path
        
        # Output structure mirrors the dataset structure
        # e.g., data/embeddings/Face2Face/000_003.pt
        embed_path = output_dir / video_rel_path.parent / f"{video_rel_path.stem}.pt"
        
        # Resume logic: skip if already processed
        if embed_path.exists():
            skip_count += 1
            continue
            
        try:
            # 1. Extract raw face tensors
            ext_result = extract_faces_from_video(
                video_full_path, 
                sample_rate=cfg.model.frame_sample_rate,
                device=device
            )
            
            faces_tensor = ext_result["faces_tensor"] # [N, 3, 224, 224]
            frame_indices = ext_result["frame_indices"]
            
            if len(faces_tensor) == 0:
                print(f"Warning: No faces found in {video_rel_path}")
                error_count += 1
                continue
                
            # 2. Normalize and move to device
            # Note: We batch process all frames for the video at once if VRAM allows,
            # otherwise we would need a mini-batch loop here. For N~30 frames, 
            # 224x224 usually fits on 8GB+ GPUs easily.
            batch = transform(faces_tensor).to(device)
            
            # 3. Extract features
            with torch.amp.autocast(device_type="cuda" if "cuda" in device else "cpu"): # Mixed precision speedup
                embeddings = manager(batch)
            
            # 4. Move back to CPU and save
            save_dict = {
                "rgb": embeddings["rgb"].cpu(),
                "vit": embeddings["vit"].cpu(),
                "freq": embeddings["freq"].cpu(),
                "concat": embeddings["concat"].cpu(),
                "frame_indices": frame_indices,
                "label": 1.0 if record["label"] == "FAKE" else 0.0,
                "method": record["method"]
            }
            
            embed_path.parent.mkdir(parents=True, exist_ok=True)
            torch.save(save_dict, embed_path)
            success_count += 1
            
        except Exception as e:
            print(f"Error processing {video_rel_path}: {e}")
            error_count += 1
            
    print("\n--- Extraction Complete ---")
    print(f"Successfully processed: {success_count}")
    print(f"Skipped (already exists): {skip_count}")
    print(f"Errors: {error_count}")

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dataset_dir = DATA_ROOT
    output_dir = PROJECT_ROOT / "data" / "embeddings"
    
    extract_and_save_embeddings(dataset_dir, output_dir, device)

if __name__ == "__main__":
    main()
