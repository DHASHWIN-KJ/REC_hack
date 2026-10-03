"""
Explainability figure (returned as "saliency_map"):
  1. Spectrogram (for humans; the model itself works on raw audio)
  2. Saliency: which moments pushed the model toward "fake"
  3. Fake-probability timeline per 4 s window
"""
import base64
import io

import matplotlib
matplotlib.use("Agg")  # no display needed (server)
import matplotlib.pyplot as plt
import numpy as np

from .config import AudioConfig


def _time_profile(segments, t_min, t_max, step=0.05):
    """For each time point, take the highest fake probability of any window covering it."""
    times = np.arange(t_min, t_max + step, step)
    values = np.zeros_like(times)
    for seg in segments:
        mask = (times >= seg["start"]) & (times <= seg["end"])
        values[mask] = np.maximum(values[mask], seg["fake_prob"])
    return times, values


def _strip(ax, times, values, cmap, label):
    ax.imshow(values[None, :], aspect="auto", cmap=cmap, vmin=0, vmax=1,
              extent=(times[0], times[-1], 0, 1), alpha=0.85)
    ax.plot(times, values, color="black", linewidth=1.0)
    ax.set_ylim(0, 1)
    ax.set_ylabel(label)


def saliency_figure_base64(wav, sr, segments, offset_seconds, cfg: AudioConfig,
                           sal_times=None, sal_values=None) -> str:
    has_sal = sal_times is not None and sal_values is not None and len(sal_values) > 1
    rows = 3 if has_sal else 2
    ratios = [3, 1.2, 1.2] if has_sal else [3, 1.3]
    fig, axes = plt.subplots(rows, 1, figsize=(10, 5.2 if has_sal else 4.2), sharex=True,
                             gridspec_kw={"height_ratios": ratios}, constrained_layout=True)
    ax_spec, ax_prob = axes[0], axes[-1]
    t_end = offset_seconds + len(wav) / sr

    with np.errstate(divide="ignore"):  # silent frames give log10(0)
        ax_spec.specgram(wav + 1e-7, NFFT=512, Fs=sr, noverlap=384, cmap="magma",
                         xextent=(offset_seconds, t_end))
    ax_spec.set_ylabel("Frequency (Hz)")
    ax_spec.set_title("Spectrogram, model saliency, and fake-probability timeline"
                      if has_sal else "Spectrogram and fake-probability timeline")

    if has_sal:
        _strip(axes[1], sal_times, sal_values, "Purples", "Saliency")

    times, values = _time_profile(segments, offset_seconds, t_end)
    _strip(ax_prob, times, values, "RdYlGn_r", "P(fake)")
    ax_prob.axhline(cfg.threshold_fake, color="black", linestyle="--", linewidth=0.8)
    ax_prob.axhline(cfg.threshold_genuine, color="black", linestyle=":", linewidth=0.8)
    ax_prob.set_xlabel("Time (s)")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")