"""
src/video/schemas.py
API data models for Video Deepfake Detection.
Provides Pydantic schemas for frames, segments, and the final evidence bundle.
Includes adapter to core pipeline result.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class FrameEvidence(BaseModel):
    """Detailed evidence for a single analyzed frame"""
    frame_index: int
    timestamp_sec: float
    fake_score: float = Field(..., ge=0.0, le=1.0, description="Probability that the frame is fake (0=real, 1=fake)")
    rgb_score: Optional[float] = None
    freq_score: Optional[float] = None
    heatmap_path: Optional[str] = Field(None, description="Path to Grad-CAM or attention heatmap image")
    
class VideoSegment(BaseModel):
    """A continuous temporal segment identified as fake or real"""
    start_time_sec: float
    end_time_sec: float
    start_frame: int
    end_frame: int
    avg_score: float = Field(..., ge=0.0, le=1.0)
    label: str = Field(..., description="'FAKE' or 'REAL'")

class EvidenceBundle(BaseModel):
    """
    Final output bundle for a single analyzed video.
    This is what the frontend or API will consume from the video subsystem.
    """
    video_id: str
    video_path: str
    fps: float
    total_frames: int
    overall_fake_score: float = Field(..., ge=0.0, le=1.0, description="Aggregated video-level score")
    overall_label: str = Field(..., description="'FAKE' or 'REAL'")
    
    # Granular data
    segments: List[VideoSegment] = Field(default_factory=list, description="List of contiguous fake/real segments")
    frame_data: List[FrameEvidence] = Field(default_factory=list, description="Detailed score and evidence per sampled frame")
    
    # Metadata and provenance
    model_version: str = "v1.0-fusion"
    processing_time_ms: int = 0
    
    def to_core_result(self) -> dict:
        """
        Adapter to map the Video EvidenceBundle into the shared core format.
        Since src/core/models.py is currently empty, this returns a generic dict
        that can be easily mapped to a CoreResult dataclass later.
        
        Expected fields from Core team:
        - modality: str ("video")
        - score: float
        - confidence: float
        - explanation: str
        - details: dict
        """
        return {
            "modality": "video",
            "score": self.overall_fake_score,
            "label": self.overall_label,
            "segments": [
                {
                    "start": seg.start_time_sec,
                    "end": seg.end_time_sec,
                    "score": seg.avg_score
                }
                for seg in self.segments if seg.label == "FAKE"
            ],
            "details": {
                "fps": self.fps,
                "frames_analyzed": len(self.frame_data),
                "model": self.model_version
            }
        }
