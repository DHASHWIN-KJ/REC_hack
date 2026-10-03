# Video Deepfake Detection Pipeline

This document outlines the architecture, data flow, and usage of the `src/video` module.

## 1. Architecture Overview

To meet the stringent 1-3 day hackathon constraint while still achieving state-of-the-art robustness, the pipeline is divided into a massive caching step (Phase E) and a lightweight training step (Phase F). 

### The Tri-Branch Network
Instead of a single backbone, we extract features across three domains:
1. **RGB Branch (EfficientNet-B4)**: Analyzes spatial textures and global context.
2. **ViT Branch (ViT-Small)**: Uses self-attention across image patches to detect localized blending boundaries or asymmetric artifacts (e.g., mismatched eyes).
3. **Frequency Branch (FFT + ResNet18)**: Converts frames into their 2D Fourier transform magnitude spectrums to detect unnatural high-frequency noise introduced by GAN upsampling and c40 compression.

### Temporal Transformer
The three features are concatenated (`[1792 + 384 + 512 = 2688]`), fused via an MLP down to a `512` hidden dimension, and passed into a 2-layer Transformer Encoder to analyze consistency over time (detecting flickering or unnatural temporal jitter).

## 2. Pipeline Stages & How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Extract and Cache Embeddings (OVERNIGHT TASK)
This script runs MTCNN (face detection) and all three heavy backbones, saving the raw PyTorch tensors (`.pt`) to disk.
```bash
python scripts/video_extract_embeddings.py
```
*Note: This script is fully resumable. If it crashes, just run it again.*

### Step 3: Train the Network (FAST)
Once embeddings are cached, training the Fusion + Temporal layers takes minutes.
```bash
python scripts/video_train.py
```
This automatically applies early stopping and temperature calibration, saving the best weights to `data/models/`.

### Step 4: Evaluate Performance
Calculates AUC, F1, Accuracy, and EER on the standard test set and the completely unseen OOD `DeepFakeDetection` set.
```bash
python scripts/video_eval.py
```
Results are saved to `docs/video_results.md`.

## 3. Integrating with the Core / API

If you are on the frontend or API team, you do not need to run the heavy Torch models manually. You can use the CLI or import the `VideoAnalyzer`.

**CLI Usage:**
```bash
python src/video/cli.py analyze dataset_videos/Deepfakes/000_003.mp4 --out result.json
```

**Python API:**
```python
from video.pipeline import VideoAnalyzer

analyzer = VideoAnalyzer()
bundle = analyzer.analyze_video("dataset_videos/Deepfakes/000_003.mp4")

# For the Frontend: Rich data including frame-by-frame scores
json_string = bundle.model_dump_json()

# For the Core Fusion team: Downsampled basic dict
core_dict = bundle.to_core_result()
```

## 4. Design Decisions & Limitations

- **Strict Identity Splits**: Data is split by target identity (`splits.py`). This prevents the model from "cheating" by recognizing the person's face rather than the deepfake artifact.
- **c40 Compression**: We optimized for the hardest compression level, utilizing the frequency branch to look past H.264 artifacts.
- **Hysteresis Thresholding**: Instead of returning raw, jittery frame classifications, `segments.py` uses high/low thresholds to ensure we only report solid, continuous blocks of deepfake activity.
