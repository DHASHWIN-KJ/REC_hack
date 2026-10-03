import torch
from video.fusion_head import FeatureFusion
from video.config_video import cfg

def test_feature_fusion():
    batch_size = 4
    rgb_dim = 1792
    vit_dim = 384
    freq_dim = 512
    hidden_dim = cfg.model.hidden_dim
    
    fusion = FeatureFusion(rgb_dim, vit_dim, freq_dim)
    
    rgb = torch.randn(batch_size, rgb_dim)
    vit = torch.randn(batch_size, vit_dim)
    freq = torch.randn(batch_size, freq_dim)
    
    out = fusion(rgb, vit, freq)
    
    assert out.shape == (batch_size, hidden_dim)
    assert not torch.isnan(out).any()
