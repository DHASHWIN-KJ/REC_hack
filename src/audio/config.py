"""
Configuration for the audio deepfake detection module.

Every value can be overridden with an environment variable, so teammates
can run the module on different machines without editing code.
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

AUDIO_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AUDIO_DIR.parent.parent
CALIBRATION_FILE = AUDIO_DIR / "calibration.json"


def _env(name, default):
    return os.getenv(name, default)


@dataclass
class AudioConfig:
    # ---- Model files (download from the SSL_Anti-spoofing repo README) ----
    xlsr_path: str = _env("XLSR_PATH", str(PROJECT_ROOT / "weights" / "xlsr2_300m.pt"))
    checkpoint_path: str = _env(
        "AUDIO_CKPT_PATH", str(PROJECT_ROOT / "weights" / "Best_LA_model_for_DF.pth")
    )
    model_version: str = _env("AUDIO_MODEL_VERSION", "xlsr-aasist-df-v1.0")
    device: str = _env("AUDIO_DEVICE", "auto")  # "auto", "cuda", or "cpu"
    use_fp16: bool = _env("AUDIO_FP16", "1") == "1"  # only used on GPU
    batch_size: int = int(_env("AUDIO_BATCH_SIZE", "8"))

    # ---- Audio format (must match what the model was trained on) ----
    sample_rate: int = 16000
    window_samples: int = 64600   # ~4.04 s, the length used in training
    hop_samples: int = 32300      # 50% overlap between windows

    # ---- Preprocessing ----
    archive_dir: str = _env("AUDIO_ARCHIVE_DIR", str(PROJECT_ROOT / "data" / "audio_archive"))
    trim_silence: bool = _env("AUDIO_TRIM_SILENCE", "0") == "1"  # off: measured lower EER with the pretrained model
    vad_threshold: float = 0.5
    # Clips shorter than this get 'uncertain' (too little audio to judge).
    min_speech_seconds: float = float(_env("AUDIO_MIN_SECONDS", "1.0"))
    # Clips between min_speech_seconds and this still get a verdict, but with
    # 'low' confidence and a warning, because accuracy drops on short audio.
    short_clip_seconds: float = float(_env("AUDIO_SHORT_CLIP_SECONDS", "2.0"))
    max_duration_seconds: float = float(_env("AUDIO_MAX_SECONDS", "600"))
    max_upload_mb: int = int(_env("AUDIO_MAX_UPLOAD_MB", "100"))

    # ---- Scoring ----
    max_saliency_windows: int = int(_env("AUDIO_SALIENCY_WINDOWS", "6"))  # saliency is slower than scoring
    top_k: int = 3                  # overall score = mean of the k most suspicious windows
    threshold_genuine: float = 0.30  # fake_probability below this -> likely_genuine
    threshold_fake: float = 0.70     # fake_probability above this -> likely_fake

    # ---- Trimmed-audio handling ----
    # If leading + trailing silence is below this, the clip counts as "trimmed".
    # The pretrained model learned that real speech has pauses at the edges
    # (an ASVspoof 2019 bias), so trimmed real speech gets pushed towards "fake".
    trimmed_max_silence: float = float(_env("AUDIO_TRIMMED_MAX_SILENCE", "0.30"))

    # ---- Calibration (filled from calibration.json if it exists) ----
    # "default" is used for normal audio, "trimmed" for edge-to-edge speech.
    calib_a: float = 1.0
    calib_b: float = 0.0
    calibrated: bool = False
    trim_calib_a: float = 1.0
    trim_calib_b: float = 0.0
    trim_calibrated: bool = False

    def __post_init__(self):
        if not CALIBRATION_FILE.exists():
            return
        try:
            data = json.loads(CALIBRATION_FILE.read_text())
        except (ValueError, json.JSONDecodeError):
            return
        if "a" in data and "default" not in data:      # old single-section format
            data = {"default": data}
        default = data.get("default")
        if default:
            self.calib_a, self.calib_b = float(default["a"]), float(default["b"])
            self.threshold_genuine = float(default.get("threshold_genuine", self.threshold_genuine))
            self.threshold_fake = float(default.get("threshold_fake", self.threshold_fake))
            self.calibrated = True
        trimmed = data.get("trimmed")
        if trimmed:
            self.trim_calib_a, self.trim_calib_b = float(trimmed["a"]), float(trimmed["b"])
            self.trim_calibrated = True

    def resolve_device(self) -> str:
        if self.device != "auto":
            return self.device
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"


_config = None


def get_config() -> AudioConfig:
    global _config
    if _config is None:
        _config = AudioConfig()
    return _config