"""
src/video/data/augmentation.py
Video and frame-level augmentations using torchvision.
Provides data augmentation to prevent overfitting and improve robustness
to heavy compression, blur, and color shifts.
"""
import torch
from torchvision.transforms import v2

def get_train_transforms(target_size: int = 224) -> v2.Transform:
    """
    Data augmentation pipeline for training.
    Assumes input is a PyTorch tensor (C, H, W) normalized to [0, 1].
    """
    return v2.Compose([
        v2.RandomHorizontalFlip(p=0.5),
        v2.RandomApply([
            v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05)
        ], p=0.4),
        v2.RandomApply([
            v2.GaussianBlur(kernel_size=(5, 9), sigma=(0.1, 2.0))
        ], p=0.3),
        # Random erasing helps robustness to occlusions and artifacts
        v2.RandomErasing(p=0.2, scale=(0.02, 0.1)),
        # Normalization (ImageNet stats as default for pretrained backbones)
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

def get_val_transforms(target_size: int = 224) -> v2.Transform:
    """
    Transforms for validation/testing (No random augs, just normalization).
    """
    return v2.Compose([
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
