import torch
from video.temporal import TemporalTransformer, FullVideoModel
from video.config_video import cfg

def test_temporal_transformer():
    batch_size = 2
    seq_len = 10
    hidden_dim = cfg.model.hidden_dim
    
    model = TemporalTransformer()
    x = torch.randn(batch_size, seq_len, hidden_dim)
    
    out = model(x)
    
    assert "video_logits" in out
    assert "frame_logits" in out
    
    assert out["video_logits"].shape == (batch_size,)
    assert out["frame_logits"].shape == (batch_size, seq_len)

def test_full_video_model():
    batch_size = 2
    seq_len = 10
    
    model = FullVideoModel(rgb_dim=100, vit_dim=50, freq_dim=50)
    
    rgb = torch.randn(batch_size, seq_len, 100)
    vit = torch.randn(batch_size, seq_len, 50)
    freq = torch.randn(batch_size, seq_len, 50)
    
    out = model(rgb, vit, freq)
    
    assert out["video_logits"].shape == (batch_size,)
    assert out["frame_logits"].shape == (batch_size, seq_len)
