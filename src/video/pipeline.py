"""
src/video/pipeline.py
The master inference pipeline for video deepfake detection.
Ties together frame extraction, backbones, temporal modeling, 
calibration, segment finding, and JSON serialization.
"""
import time
import torch
from pathlib import Path
from typing import Optional

from video.config_video import cfg, PROJECT_ROOT
from video.frames import extract_faces_from_video
from video.data.augmentation import get_val_transforms
from video.branches import FeatureExtractorManager
from video.temporal import FullVideoModel
from video.calibration import TemperatureScaler
from video.segments import compute_segments
from video.evidence import generate_heatmap
from video.schemas import EvidenceBundle, FrameEvidence

class VideoAnalyzer:
    def __init__(self, weights_dir: str = None, device: str = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        weights_dir = Path(weights_dir) if weights_dir else Path(PROJECT_ROOT) / "data" / "models"
        
        # Initialize and load models
        self.extractor = FeatureExtractorManager().to(self.device)
        self.model = FullVideoModel().to(self.device)
        self.scaler = TemperatureScaler().to(self.device)
        
        self.transform = get_val_transforms()
        
        # Try to load weights if they exist (they won't during initial testing)
        model_path = weights_dir / "video_fusion_best.pt"
        scaler_path = weights_dir / "video_scaler.pt"
        
        if model_path.exists():
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        if scaler_path.exists():
            self.scaler.load_state_dict(torch.load(scaler_path, map_location=self.device))
        self.scaler.eval()
        
    @torch.no_grad()
    def analyze_video(self, video_path: str | Path) -> EvidenceBundle:
        """
        Runs the full detection pipeline on a single video file.
        """
        start_time = time.time()
        video_path = Path(video_path)
        
        # 1. Extract frames & faces
        ext_result = extract_faces_from_video(video_path, device=self.device)
        faces_tensor = ext_result["faces_tensor"]
        frame_indices = ext_result["frame_indices"]
        meta = ext_result["metadata"]
        
        if len(faces_tensor) == 0:
            # Fallback for completely unreadable videos
            return EvidenceBundle(
                video_id=video_path.stem,
                video_path=str(video_path),
                fps=meta.fps,
                total_frames=meta.total_frames,
                overall_fake_score=0.0,
                overall_label="REAL",
                segments=[],
                frame_data=[],
                processing_time_ms=int((time.time() - start_time) * 1000)
            )
            
        # 2. Augmentation (Normalization only)
        batch = self.transform(faces_tensor).to(self.device)
        
        # 3. Extract branch features
        with torch.amp.autocast(device_type="cuda" if "cuda" in self.device else "cpu"):
            features = self.extractor(batch)
            
            # 4. Add batch dimension (B=1) for sequence model
            rgb_seq = features["rgb"].unsqueeze(0)
            vit_seq = features["vit"].unsqueeze(0)
            freq_seq = features["freq"].unsqueeze(0)
            
            # 5. Temporal & Fusion
            out = self.model(rgb_seq, vit_seq, freq_seq)
            
            # 6. Calibration
            vid_score = self.scaler(out["video_logits"]).item()
            frame_scores = self.scaler(out["frame_logits"]).squeeze(0).cpu().tolist()
            
        # 7. Compute Segments
        segments = compute_segments(frame_scores, frame_indices, meta.fps)
        
        # 8. Build detailed frame evidence
        frame_evidence_list = []
        for i, (f_idx, f_score) in enumerate(zip(frame_indices, frame_scores)):
            t_sec = f_idx / meta.fps
            
            # If the frame score is very high, generate a heatmap
            heatmap_uri = None
            if f_score > cfg.detect.fake_threshold:
                # STUB: We pass a dummy tensor here since real Grad-CAM needs gradients
                heatmap_uri = generate_heatmap(batch[i:i+1], self.model)
                
            frame_evidence_list.append(
                FrameEvidence(
                    frame_index=f_idx,
                    timestamp_sec=round(t_sec, 2),
                    fake_score=f_score,
                    heatmap_path=heatmap_uri
                )
            )
            
        # 9. Return structured API payload
        label = "FAKE" if vid_score >= cfg.detect.fake_threshold else "REAL"
        
        return EvidenceBundle(
            video_id=video_path.stem,
            video_path=str(video_path),
            fps=meta.fps,
            total_frames=meta.total_frames,
            overall_fake_score=vid_score,
            overall_label=label,
            segments=segments,
            frame_data=frame_evidence_list,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )
