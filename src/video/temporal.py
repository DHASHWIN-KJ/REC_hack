"""
src/video/temporal.py
Temporal Transformer to analyze frame sequence consistencies (e.g. flickering).
"""
import torch
import torch.nn as nn
from video.config_video import cfg

class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 1000):
        super().__init__()
        # Simple learnable positional embeddings (since videos might be variable length)
        self.pos_embed = nn.Embedding(max_len, d_model)
        
    def forward(self, seq_len: int, device: torch.device):
        positions = torch.arange(seq_len, device=device).unsqueeze(0) # [1, seq_len]
        return self.pos_embed(positions) # [1, seq_len, d_model]

class TemporalTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        
        hidden_dim = cfg.model.hidden_dim
        num_layers = cfg.model.temporal_layers
        
        self.pos_encoding = PositionalEncoding(d_model=hidden_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim, 
            nhead=8, 
            dim_feedforward=hidden_dim * 2,
            dropout=0.1,
            activation='gelu',
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Frame-level classifier (for segment analysis)
        self.frame_classifier = nn.Linear(hidden_dim, 1)
        
        # Video-level classifier (uses CLS token or mean pooling)
        self.video_classifier = nn.Linear(hidden_dim, 1)
        
    def forward(self, fused_sequence: torch.Tensor):
        """
        Args:
            fused_sequence: [B, SeqLen, HiddenDim]
        Returns:
            dict containing video_logits and frame_logits
        """
        B, seq_len, _ = fused_sequence.shape
        device = fused_sequence.device
        
        # Add positional encoding
        x = fused_sequence + self.pos_encoding(seq_len, device)
        
        # Pass through transformer
        # [B, SeqLen, HiddenDim]
        encoded = self.transformer(x)
        
        # Frame-level predictions
        # [B, SeqLen, 1] -> [B, SeqLen]
        frame_logits = self.frame_classifier(encoded).squeeze(-1)
        
        # Video-level prediction (mean pooling over time)
        # [B, HiddenDim]
        video_feat = encoded.mean(dim=1)
        # [B, 1] -> [B]
        video_logits = self.video_classifier(video_feat).squeeze(-1)
        
        return {
            "video_logits": video_logits,
            "frame_logits": frame_logits,
            "encoded_features": encoded
        }

class FullVideoModel(nn.Module):
    """Wraps Fusion and Temporal layers into one trainable module."""
    def __init__(self, rgb_dim=1792, vit_dim=384, freq_dim=512):
        super().__init__()
        from video.fusion_head import FeatureFusion
        self.fusion = FeatureFusion(rgb_dim, vit_dim, freq_dim)
        self.temporal = TemporalTransformer()
        
    def forward(self, rgb_seq, vit_seq, freq_seq):
        """
        Args:
            *_seq tensors of shape [B, SeqLen, Dim]
        """
        B, seq_len, _ = rgb_seq.shape
        
        # Flatten time into batch for fusion MLP
        rgb_flat = rgb_seq.view(B * seq_len, -1)
        vit_flat = vit_seq.view(B * seq_len, -1)
        freq_flat = freq_seq.view(B * seq_len, -1)
        
        # [B * SeqLen, HiddenDim]
        fused_flat = self.fusion(rgb_flat, vit_flat, freq_flat)
        
        # Reshape back to sequence
        # [B, SeqLen, HiddenDim]
        fused_seq = fused_flat.view(B, seq_len, -1)
        
        return self.temporal(fused_seq)
