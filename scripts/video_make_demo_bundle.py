#!/usr/bin/env python3
"""
scripts/video_make_demo_bundle.py
Generates a mock EvidenceBundle JSON file to serve as an API contract
for the frontend and core teams before the actual models are finished.
"""

import sys
import os
from pathlib import Path

# Add src to python path so we can import video
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from video.schemas import EvidenceBundle, FrameEvidence, VideoSegment
from video.config_video import cfg

def main():
    output_dir = PROJECT_ROOT / "docs"
    output_dir.mkdir(exist_ok=True)
    out_path = output_dir / "demo_evidence_bundle.json"
    
    print("Generating demo EvidenceBundle...")
    
    # Create some mock frames
    frames = []
    fps = 30.0
    for i in range(0, 300, cfg.model.frame_sample_rate):
        t_sec = i / fps
        # Simulate a fake section from 2.0s to 5.0s
        is_fake_region = 2.0 <= t_sec <= 5.0
        
        f_score = 0.92 if is_fake_region else 0.12
        frames.append(
            FrameEvidence(
                frame_index=i,
                timestamp_sec=round(t_sec, 2),
                fake_score=f_score,
                rgb_score=f_score - 0.05,
                freq_score=f_score + 0.03,
                heatmap_path=f"/static/heatmaps/demo_vid/frame_{i:04d}.jpg" if is_fake_region else None
            )
        )
        
    # Create mock segments based on the frames
    segments = [
        VideoSegment(
            start_time_sec=0.0,
            end_time_sec=1.9,
            start_frame=0,
            end_frame=57,
            avg_score=0.15,
            label="REAL"
        ),
        VideoSegment(
            start_time_sec=2.0,
            end_time_sec=5.0,
            start_frame=60,
            end_frame=150,
            avg_score=0.94,
            label="FAKE"
        ),
        VideoSegment(
            start_time_sec=5.1,
            end_time_sec=10.0,
            start_frame=153,
            end_frame=300,
            avg_score=0.08,
            label="REAL"
        )
    ]
    
    bundle = EvidenceBundle(
        video_id="demo_deepfake_001",
        video_path="dataset_videos/Face2Face/001_870.mp4",
        fps=fps,
        total_frames=300,
        overall_fake_score=0.88,
        overall_label="FAKE",
        segments=segments,
        frame_data=frames,
        processing_time_ms=1450
    )
    
    json_data = bundle.model_dump_json(indent=2)
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(json_data)
        
    print(f"Success! Wrote API contract to {out_path}")
    
    print("\n--- Core Adapter Demo ---")
    import json
    print(json.dumps(bundle.to_core_result(), indent=2))

if __name__ == "__main__":
    main()
