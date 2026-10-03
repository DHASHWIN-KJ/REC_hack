"""
src/video/config_video.py
Configuration parameters for the Video Deepfake Detection pipeline.
"""
from pathlib import Path
from pydantic import BaseModel, Field

# Base Paths
VIDEO_MODULE_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = VIDEO_MODULE_ROOT.parent.parent
DATA_ROOT = VIDEO_MODULE_ROOT / "dataset_videos"
CACHE_ROOT = VIDEO_MODULE_ROOT / "cache"

class DataConfig(BaseModel):
    """Dataset and split configuration"""
    seed: int = 42
    split_ratios: tuple[float, float, float] = (0.72, 0.14, 0.14) # Train, Val, Test
    compression_level: str = "c40"  # Target compression for training/eval
    fps_fallback: float = 30.0  # Fallback if container FPS is unreadable

class ModelConfig(BaseModel):
    """Model hyperparameter configuration"""
    # Branches
    rgb_backbone: str = "tf_efficientnet_b4_ns"
    freq_backbone: str = "resnet18"
    vit_backbone: str = "vit_small_patch16_224"
    
    # Fusion and Temporal
    temporal_layers: int = 2
    hidden_dim: int = 512
    
    # Inference
    batch_size: int = 16
    frame_sample_rate: int = 60  # Process 1 frame every 60 frames (guarantees < 4 hours)
    
class DetectionConfig(BaseModel):
    """Thresholds and inference settings"""
    fake_threshold: float = 0.5  # Base threshold for binary classification
    segment_hysteresis_high: float = 0.6  # Upper threshold to start a fake segment
    segment_hysteresis_low: float = 0.4   # Lower threshold to end a fake segment
    min_segment_frames: int = 15          # Minimum length of a fake segment to report

class VideoConfig(BaseModel):
    """Main video configuration object"""
    data: DataConfig = Field(default_factory=DataConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    detect: DetectionConfig = Field(default_factory=DetectionConfig)

# Global singleton configuration
cfg = VideoConfig()
