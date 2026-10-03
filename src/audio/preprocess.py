"""
Audio preprocessing.

Any input (mp3, m4a, ogg/opus WhatsApp notes, wav, mp4 video, ...) goes through:
  1. SHA-256 hash of the ORIGINAL file (for tamper-evident audit logs)
  2. ffmpeg -> 16 kHz, mono, 16-bit FLAC (archived copy)
  3. Load as float32 numpy array
  4. Trim leading/trailing silence (avoids the ASVspoof "silence shortcut")
"""
import hashlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import soundfile as sf

from .config import AudioConfig


class AudioPreprocessError(Exception):
    """Raised when an input file cannot be turned into usable audio."""


@dataclass
class PreparedAudio:
    waveform: np.ndarray          # float32, mono, trimmed
    sample_rate: int
    sha256: str
    flac_path: str
    original_duration: float      # seconds, before trimming
    offset_seconds: float         # where the trimmed audio starts in the original
    speech_seconds: float         # detected speech duration
    warnings: list = field(default_factory=list)
    lead_silence: float = 0.0     # seconds of non-speech before the first speech
    trail_silence: float = 0.0    # seconds of non-speech after the last speech
    is_trimmed: bool = False      # True if speech runs almost edge to edge


# --------------------------------------------------------------------------
# Basic helpers
# --------------------------------------------------------------------------
def sha256_file(path, chunk_size=1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _require_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise AudioPreprocessError(
            "ffmpeg not found. Install it (e.g. `sudo apt install ffmpeg` or "
            "download from ffmpeg.org) and make sure it is on PATH."
        )


def _run_ffmpeg(cmd, timeout=300) -> bytes:
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AudioPreprocessError("ffmpeg timed out while decoding the file.")
    if proc.returncode != 0:
        msg = proc.stderr.decode(errors="ignore").strip().splitlines()
        raise AudioPreprocessError(
            "Could not decode audio (no audio track or unsupported file). "
            + (msg[-1] if msg else "")
        )
    return proc.stdout


def convert_to_flac(src_path, dst_path, sample_rate=16000):
    """Any audio/video file -> 16 kHz mono 16-bit FLAC."""
    _require_ffmpeg()
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    _run_ffmpeg([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src_path),
        "-vn",                      # drop video stream if present
        "-ac", "1",                 # mono
        "-ar", str(sample_rate),    # 16 kHz
        "-sample_fmt", "s16",       # 16-bit
        "-c:a", "flac",
        str(dst_path),
    ])
    return str(dst_path)


def decode_to_array(src_path, sample_rate=16000) -> np.ndarray:
    """Fast in-memory decode of any file (used by evaluation scripts)."""
    _require_ffmpeg()
    raw = _run_ffmpeg([
        "ffmpeg", "-hide_banner", "-loglevel", "error",
        "-i", str(src_path), "-vn", "-ac", "1", "-ar", str(sample_rate),
        "-f", "s16le", "-",
    ])
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def simulate_codec(src_path, codec="opus", bitrate="16k") -> str:
    """
    Re-encode a file through a lossy codec to simulate social-media sharing.
    opus @ 16k is close to a WhatsApp voice note. Returns a temp file path
    (caller should delete it).
    """
    _require_ffmpeg()
    codecs = {"opus": ("libopus", ".ogg"), "mp3": ("libmp3lame", ".mp3"), "aac": ("aac", ".m4a")}
    if codec not in codecs:
        raise ValueError(f"codec must be one of {list(codecs)}")
    lib, ext = codecs[codec]
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.close()
    _run_ffmpeg([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", str(src_path), "-vn", "-ac", "1", "-c:a", lib, "-b:a", bitrate, tmp.name,
    ])
    return tmp.name


def load_audio(path):
    data, sr = sf.read(path, dtype="float32", always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(np.float32), sr


# --------------------------------------------------------------------------
# Silence trimming (leading/trailing only; internal pauses are kept because
# natural pause rhythm is itself a useful real-vs-fake cue)
# --------------------------------------------------------------------------
_vad = None
_vad_unavailable = False


def _get_vad():
    global _vad, _vad_unavailable
    if _vad is None and not _vad_unavailable:
        try:
            from silero_vad import load_silero_vad
            _vad = load_silero_vad()
        except Exception:
            _vad_unavailable = True
    return _vad


def _energy_trim(wav, sr, rel_db=-35.0):
    frame = int(0.025 * sr)
    if len(wav) < frame:
        return 0, len(wav), len(wav) / sr
    n = len(wav) // frame
    rms = np.sqrt(np.mean(wav[: n * frame].reshape(n, frame) ** 2, axis=1) + 1e-12)
    thr = rms.max() * (10 ** (rel_db / 20))
    active = np.where(rms > thr)[0]
    if len(active) == 0:
        return 0, 0, 0.0
    return active[0] * frame, min(len(wav), (active[-1] + 1) * frame), len(active) * frame / sr


def measure_edge_silence(wav, sr):
    """
    Seconds of non-speech at the start and end of the clip (energy-based,
    deterministic, no VAD model needed). Used to detect 'trimmed' audio, on
    which the pretrained model is known to be biased towards 'fake'.
    """
    start, end, _ = _energy_trim(wav, sr)
    if end <= start:
        return float(len(wav) / sr), 0.0
    return float(start / sr), float((len(wav) - end) / sr)


def is_trimmed_audio(lead, trail, duration, max_edge_silence):
    return bool(duration > 0.5 and (lead + trail) < max_edge_silence)


def find_speech_bounds(wav, sr, threshold=0.5):
    """Returns (start_sample, end_sample, speech_seconds)."""
    vad = _get_vad()
    if vad is None:
        return _energy_trim(wav, sr)
    import torch
    from silero_vad import get_speech_timestamps
    ts = get_speech_timestamps(torch.from_numpy(wav), vad, sampling_rate=sr, threshold=threshold)
    if not ts:
        return 0, 0, 0.0
    speech = sum(t["end"] - t["start"] for t in ts) / sr
    return ts[0]["start"], ts[-1]["end"], speech


# --------------------------------------------------------------------------
# Main entry point
# --------------------------------------------------------------------------
def prepare_audio(path, cfg: AudioConfig) -> PreparedAudio:
    path = Path(path)
    if not path.exists():
        raise AudioPreprocessError(f"File not found: {path}")
    if path.stat().st_size == 0:
        raise AudioPreprocessError("Uploaded file is empty.")

    warnings = []
    digest = sha256_file(path)
    flac_path = Path(cfg.archive_dir) / f"{digest}.flac"
    if not flac_path.exists():
        convert_to_flac(path, flac_path, cfg.sample_rate)

    wav, sr = load_audio(flac_path)
    if sr != cfg.sample_rate:
        raise AudioPreprocessError(f"Unexpected sample rate {sr} after conversion.")
    original_duration = len(wav) / sr
    if original_duration == 0:
        raise AudioPreprocessError("File contains no audio samples.")

    max_samples = int(cfg.max_duration_seconds * sr)
    if len(wav) > max_samples:
        wav = wav[:max_samples]
        warnings.append(f"Audio longer than {cfg.max_duration_seconds:.0f}s; only the first part was analyzed.")

    # Measure edge silence on the untouched audio (before any trimming).
    lead, trail = measure_edge_silence(wav, sr)
    trimmed = is_trimmed_audio(lead, trail, len(wav) / sr, cfg.trimmed_max_silence)

    offset = 0
    speech_seconds = len(wav) / sr
    if cfg.trim_silence:
        start, end, speech_seconds = find_speech_bounds(wav, sr, cfg.vad_threshold)
        if end > start:
            margin = int(0.05 * sr)
            start, end = max(0, start - margin), min(len(wav), end + margin)
            wav, offset = wav[start:end], start
        else:
            warnings.append("No speech detected; analyzing the raw audio.")

    if speech_seconds < cfg.min_speech_seconds:
        warnings.append(f"Very little speech ({speech_seconds:.2f}s); result is unreliable.")

    if np.max(np.abs(wav)) >= 0.999:
        warnings.append("Audio is clipped (distorted); this can affect detection.")

    return PreparedAudio(
        waveform=np.ascontiguousarray(wav, dtype=np.float32),
        sample_rate=sr,
        sha256=digest,
        flac_path=str(flac_path),
        original_duration=original_duration,
        offset_seconds=offset / sr,
        speech_seconds=speech_seconds,
        warnings=warnings,
        lead_silence=lead,
        trail_silence=trail,
        is_trimmed=trimmed,
    )