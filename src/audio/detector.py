"""
Main detection logic: windowing -> model -> calibration -> aggregation -> verdict.

Public function for the rest of the project:  analyze_audio(path) -> dict
"""
import time

import numpy as np

from . import model as model_lib
from .config import AudioConfig, get_config
from .preprocess import prepare_audio


# --------------------------------------------------------------------------
# Windowing
# --------------------------------------------------------------------------
def repeat_pad(x: np.ndarray, length: int) -> np.ndarray:
    """Same padding as the original repo: repeat the audio until it is long enough."""
    if len(x) >= length:
        return x[:length]
    if len(x) == 0:
        return np.zeros(length, dtype=np.float32)
    reps = length // len(x) + 1
    return np.tile(x, reps)[:length]


def make_windows(wav: np.ndarray, length: int, hop: int):
    """Returns (windows (N, length), start_samples, end_samples)."""
    n = len(wav)
    if n <= length:
        return repeat_pad(wav, length)[None, :], [0], [n]
    starts = list(range(0, n - length + 1, hop))
    if starts[-1] + length < n:          # make sure the tail is covered
        starts.append(n - length)
    windows = np.stack([wav[s:s + length] for s in starts]).astype(np.float32)
    return windows, starts, [s + length for s in starts]


# --------------------------------------------------------------------------
# Scoring
# --------------------------------------------------------------------------
def raw_fake_scores(logits: np.ndarray) -> np.ndarray:
    """Higher = more fake. Equal to log-odds of 'spoof' under the model's softmax."""
    return logits[:, 0] - logits[:, 1]


def to_probability(scores, cfg: AudioConfig, trimmed: bool = False):
    """
    Calibrated probability of being fake. With a=1, b=0 this equals plain softmax.
    Trimmed (edge-to-edge speech) inputs use their own calibration, because the
    model's raw scores are shifted towards 'fake' for that kind of audio.
    """
    if trimmed and cfg.trim_calibrated:
        a, b = cfg.trim_calib_a, cfg.trim_calib_b
    else:
        a, b = cfg.calib_a, cfg.calib_b
    z = a * np.asarray(scores, dtype=np.float64) + b
    p = 1.0 / (1.0 + np.exp(-z))
    # No detector is ever 100% sure; keep displayed values in [0.01, 0.99].
    return np.clip(p, 0.01, 0.99)


def aggregate(scores: np.ndarray, top_k: int) -> float:
    """Mean of the k most suspicious windows, so a short fake insert isn't averaged away."""
    k = max(1, min(top_k, len(scores)))
    return float(np.mean(np.sort(scores)[-k:]))


def verdict_from_probability(p: float, cfg: AudioConfig):
    if p >= cfg.threshold_fake:
        verdict = "likely_fake"
    elif p <= cfg.threshold_genuine:
        verdict = "likely_genuine"
    else:
        return "uncertain", "low"
    confidence = "high" if abs(p - 0.5) >= 0.35 else "medium"
    return verdict, confidence


def score_waveform(wav: np.ndarray, cfg: AudioConfig):
    """Core scoring on an already-prepared waveform. Used by analyze_audio and evaluate.py."""
    windows, starts, ends = make_windows(wav, cfg.window_samples, cfg.hop_samples)
    logits = model_lib.predict_logits(windows, cfg)
    scores = raw_fake_scores(logits)
    overall_score = aggregate(scores, cfg.top_k)
    return {
        "window_scores": scores,
        "starts": starts,
        "ends": ends,
        "overall_score": overall_score,
    }


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def compute_saliency(wav, starts, ends, sr, offset_seconds, window_probs, cfg: AudioConfig):
    """
    Gradient x input saliency: how much each moment of the audio pushed the model
    toward "fake". Computed for the most suspicious windows (it is slower than
    plain inference), combined over time, and normalised to 0..1.
    Returns (times, values) on a 20 ms grid in original-file seconds.
    """
    frame = int(0.02 * sr)
    n_frames = int(np.ceil(len(wav) / frame)) or 1
    values = np.zeros(n_frames)

    order = np.argsort(window_probs)[::-1][: cfg.max_saliency_windows]
    windows = np.stack([repeat_pad(wav[starts[i]:ends[i]], cfg.window_samples) for i in order])
    sal = model_lib.input_saliency(windows, cfg)          # (k, window_samples)

    for row, i in zip(sal, order):
        length = ends[i] - starts[i]                        # ignore looped padding
        row = row[:length]
        k = int(np.ceil(len(row) / frame))
        per_frame = np.pad(row, (0, k * frame - len(row))).reshape(k, frame).sum(axis=1)
        f0 = starts[i] // frame
        seg = values[f0:f0 + k]
        values[f0:f0 + k] = np.maximum(seg, per_frame[: len(seg)])

    values = np.convolve(values, np.ones(5) / 5, mode="same")   # light smoothing
    if values.max() > 0:
        values = values / values.max()
    times = offset_seconds + np.arange(n_frames) * frame / sr
    return times, values


def analyze_audio(path, cfg: AudioConfig = None, include_saliency: bool = True,
                  include_details: bool = True, include_plot=None) -> dict:
    """
    Analyze one audio or video file. Returns:

    {
      "file_sha256": "a3f9...",
      "verdict": "likely_fake" | "likely_genuine" | "uncertain",
      "fake_probability": 0.91,
      "confidence": "high" | "medium" | "low",
      "segments": [{"start": 0.0, "end": 4.04, "fake_prob": 0.12}, ...],
      "saliency_map": "<base64 PNG>" | null,
      "model_version": "...",
      "details": {...}            # extra info, omitted if include_details=False
    }
    """
    if include_plot is not None:          # backward compatibility with older calls
        include_saliency = include_plot
    cfg = cfg or get_config()
    t0 = time.time()
    prepared = prepare_audio(path, cfg)
    sr = prepared.sample_rate
    wav = prepared.waveform

    result = score_waveform(wav, cfg)
    trimmed = prepared.is_trimmed
    window_probs = to_probability(result["window_scores"], cfg, trimmed)
    overall_p = float(to_probability(result["overall_score"], cfg, trimmed))
    verdict, confidence = verdict_from_probability(overall_p, cfg)

    warnings = list(prepared.warnings)
    if trimmed:
        if cfg.trim_calibrated:
            warnings.append(
                "Speech runs edge to edge with almost no pauses (trimmed audio); "
                "a separate calibration for this condition was applied."
            )
        else:
            warnings.append(
                "Speech runs edge to edge with almost no pauses (trimmed audio). "
                "The model over-flags such audio as fake, so no 'fake' verdict is "
                "given until trimmed-audio calibration is done."
            )
            if verdict == "likely_fake":
                verdict, confidence = "uncertain", "low"
    clip_seconds = len(wav) / sr
    if prepared.speech_seconds < cfg.min_speech_seconds:
        verdict, confidence = "uncertain", "low"
    elif clip_seconds < cfg.short_clip_seconds and verdict != "uncertain":
        confidence = "low"
        warnings.append(
            f"Short clip ({clip_seconds:.1f} s); a verdict is given but it is less "
            f"reliable than for clips of {cfg.short_clip_seconds:.0f} s or longer."
        )
    if len(wav) < cfg.window_samples:
        warnings.append("Clip shorter than 4 s; it was looped to fill the model window.")

    segments = [
        {
            "start": round(prepared.offset_seconds + s / sr, 2),
            "end": round(prepared.offset_seconds + e / sr, 2),
            "fake_prob": round(float(p), 4),
        }
        for s, e, p in zip(result["starts"], result["ends"], window_probs)
    ]

    saliency_png = None
    if include_saliency:
        try:
            times, sal = compute_saliency(wav, result["starts"], result["ends"], sr,
                                          prepared.offset_seconds, window_probs, cfg)
        except Exception as exc:
            times, sal = None, None
            warnings.append(f"Saliency unavailable ({exc}); showing timeline only.")
        try:
            from .visualize import saliency_figure_base64
            saliency_png = saliency_figure_base64(wav, sr, segments, prepared.offset_seconds,
                                                  cfg, times, sal)
        except Exception as exc:  # a plot failure must never break detection
            warnings.append(f"Plot generation failed: {exc}")

    output = {
        "file_sha256": prepared.sha256,
        "verdict": verdict,
        "fake_probability": round(overall_p, 4),
        "confidence": confidence,
        "segments": segments,
        "saliency_map": saliency_png,
        "model_version": cfg.model_version,
    }
    if include_details:
        output["details"] = {
            "modality": "audio",
            "most_suspicious_segment": max(segments, key=lambda s: s["fake_prob"]),
            "duration_seconds": round(prepared.original_duration, 2),
            "speech_seconds": round(prepared.speech_seconds, 2),
            "calibrated": cfg.calibrated,
            "input_condition": {
                "trimmed": trimmed,
                "lead_silence_seconds": round(prepared.lead_silence, 2),
                "trail_silence_seconds": round(prepared.trail_silence, 2),
                "calibration_used": "trimmed" if (trimmed and cfg.trim_calibrated) else "default",
            },
            "thresholds": {"genuine_below": cfg.threshold_genuine, "fake_above": cfg.threshold_fake},
            "archived_flac": prepared.flac_path,
            "warnings": warnings,
            "processing_seconds": round(time.time() - t0, 2),
        }
    return output


def warmup(cfg: AudioConfig = None):
    """Load the model ahead of the first request (call from the API startup)."""
    model_lib.load_model(cfg or get_config())