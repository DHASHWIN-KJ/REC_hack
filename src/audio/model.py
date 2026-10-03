"""
Loads the pretrained XLS-R + AASIST anti-spoofing model and runs batched inference.

The network definition lives in ssl_aasist.py, which is model.py copied
unchanged from the SSL_Anti-spoofing repo (one line edited, see SETUP notes).
This file only handles loading, device placement, and batching.

Output convention of the original repo (important!):
    logits[:, 0] = spoof (fake)
    logits[:, 1] = bona fide (real)
"""
import os
import threading
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from .config import AudioConfig

_model = None
_device = None
_lock = threading.Lock()


def _strip_module_prefix(state_dict):
    # Checkpoints saved from nn.DataParallel have "module." in front of every key.
    if any(k.startswith("module.") for k in state_dict):
        return {k[len("module."):] if k.startswith("module.") else k: v for k, v in state_dict.items()}
    return state_dict


def load_model(cfg: AudioConfig):
    """Load once and reuse (thread-safe). Returns (model, device)."""
    global _model, _device
    if _model is not None:
        return _model, _device

    with _lock:
        if _model is not None:
            return _model, _device

        import torch

        for label, p in (("XLS-R base weights", cfg.xlsr_path), ("Anti-spoofing checkpoint", cfg.checkpoint_path)):
            if not Path(p).exists():
                raise FileNotFoundError(
                    f"{label} not found at '{p}'. Download it from the SSL_Anti-spoofing "
                    f"README, or set the path with the XLSR_PATH / AUDIO_CKPT_PATH env variables."
                )

        # ssl_aasist.py reads this env var to find the XLS-R weights.
        os.environ["XLSR_PATH"] = str(cfg.xlsr_path)
        from .ssl_aasist import Model

        device = cfg.resolve_device()
        model = Model(SimpleNamespace(), device)
        state = torch.load(cfg.checkpoint_path, map_location=device)
        model.load_state_dict(_strip_module_prefix(state))
        model = model.to(device)
        model.eval()

        # Warm-up pass. The repo's SSLModel.extract_feat() switches XLS-R to
        # train mode the first time it moves weights; calling eval() after the
        # warm-up guarantees dropout is OFF for every real prediction.
        with torch.inference_mode():
            model(torch.zeros(1, cfg.window_samples, device=device))
        model.eval()

        _model, _device = model, device
        return _model, _device


def predict_logits(windows: np.ndarray, cfg: AudioConfig) -> np.ndarray:
    """
    windows: (N, window_samples) float32 array.
    Returns (N, 2) logits as [spoof, bonafide].
    """
    import torch

    model, device = load_model(cfg)
    use_amp = cfg.use_fp16 and device.startswith("cuda")
    outputs = []
    with torch.inference_mode():
        for i in range(0, len(windows), cfg.batch_size):
            batch = torch.from_numpy(windows[i:i + cfg.batch_size]).to(device)
            if use_amp:
                # autocast keeps weights in fp32 (so the repo never re-enters train mode)
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    out = model(batch)
            else:
                out = model(batch)
            outputs.append(out.float().cpu().numpy())
    return np.concatenate(outputs, axis=0)


def input_saliency(windows: np.ndarray, cfg: AudioConfig) -> np.ndarray:
    """
    Gradient x input saliency for each window: |d(fake score)/d(sample) * sample|.
    windows: (N, window_samples). Returns (N, window_samples), non-negative.
    """
    import torch

    model, device = load_model(cfg)
    # Only the input needs gradients; freezing weights saves a lot of memory.
    for p in model.parameters():
        p.requires_grad_(False)
    # Fine-tuned wav2vec2 models may block gradients through the CNN front-end
    # (feature_grad_mult = 0). This only scales gradients, never the forward output.
    w2v = getattr(getattr(model, "ssl_model", None), "model", None)
    if w2v is not None and hasattr(w2v, "feature_grad_mult"):
        w2v.feature_grad_mult = 1.0

    out_maps = []
    for w in windows:
        x = torch.from_numpy(np.ascontiguousarray(w[None, :])).to(device).requires_grad_(True)
        with torch.enable_grad():
            logits = model(x)
            score = logits[0, 0] - logits[0, 1]          # fake minus real
            (grad,) = torch.autograd.grad(score, x)
        out_maps.append((grad * x).abs().detach().cpu().numpy()[0])
    model.eval()
    return np.stack(out_maps)


def is_loaded() -> bool:
    return _model is not None