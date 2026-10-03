# Video Deepfake Detection Pipeline: Evaluation Results

## 1. Test Set (In-Distribution)
*Evaluated on 840 videos using the standard 5 FaceForensics++ methods (c40 compression).*

| Metric | Score |
|--------|-------|
| Accuracy | 0.8571 |
| AUC-ROC | 0.8470 |
| F1 Score | 0.9169 |
| Equal Error Rate (EER) | 0.2357 |

## 2. DeepFakeDetection Set (Out-of-Distribution)
*Evaluated on 1000 videos from a completely unseen dataset. Measures generalizability.*

| Metric | Score |
|--------|-------|
| Accuracy | 0.9020 |
| AUC-ROC | nan |
| F1 Score | 0.9485 |
| Equal Error Rate (EER) | nan |

## Model Configuration Used
- **RGB Backbone**: tf_efficientnet_b4_ns
- **ViT Backbone**: vit_small_patch16_224
- **Frequency**: Differentiable FFT + resnet18
- **Temporal Layers**: 2 (Hidden Dim: 512)
- **Fake Threshold**: 0.5
