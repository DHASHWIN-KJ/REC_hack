"""
Audio deepfake detection module (XLS-R + AASIST).

Usage from other modules (fusion, bulk_verify, etc.):

    from src.audio import analyze_audio
    result = analyze_audio("clip.mp3")
    result["fake_probability"], result["verdict"], result["segments"]
"""
from .detector import analyze_audio, warmup

__all__ = ["analyze_audio", "warmup"]
