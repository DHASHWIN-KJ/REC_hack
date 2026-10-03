"""
src/video/fusion_head.py
Combines the features extracted from RGB, ViT, and Frequency branches.
Uses an MLP-based fusion to allow interactions between different feature domains.
"""
import torch
import torch.nn as nn
from video.config_video import cfg

class FeatureFusion(nn.Module):
    def __init__(self, rgb_dim: int = 1792, vit_dim: int = 384, freq_dim: int = 512):
        super().__init__()
        
        self.rgb_dim = rgb_dim
        self.vit_dim = vit_dim
        self.freq_dim = freq_dim
        
        in_features = rgb_dim + vit_dim + freq_dim
        hidden_dim = cfg.model.hidden_dim
        
        # Simple MLP to fuse the heterogeneous features
        self.fusion_mlp = nn.Sequential(
            nn.Linear(in_features, hidden_dim * 2),
            nn.BatchNorm1d(hidden_dim * 2),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2)
        )
        
    def forward(self, rgb_feat, vit_feat, freq_feat):
        """
        Args:
            rgb_feat: [B, 1792]
            vit_feat: [B, 384]
            freq_feat: [B, 512]
        Returns:
            fused_feat: [B, hidden_dim]
        """
        # Ensure dimensions match before concat
        # Note: If batch size is 1, batchnorm might complain during training, 
        # so training scripts should use drop_last=True or batch_size > 1
        concat = torch.cat([rgb_feat, vit_feat, freq_feat], dim=1)
        fused = self.fusion_mlp(concat)
        return fused
