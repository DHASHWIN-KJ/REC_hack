"""
src/video/branches.py
Neural network backbones for feature extraction.
Contains RGB (EfficientNet), ViT (Patch analysis), and Frequency (ResNet) branches.
All branches are frozen to act as pure feature extractors for speed/memory efficiency.
"""
import torch
import torch.nn as nn
import timm

from video.config_video import cfg

class FrequencyTransform(nn.Module):
    """Simple differentiable FFT magnitude extractor."""
    def __init__(self):
        super().__init__()
        
    def forward(self, x):
        # x: [B, C, H, W]
        # Compute 2D FFT
        fft = torch.fft.fft2(x)
        # Shift zero-frequency component to center
        fft_shift = torch.fft.fftshift(fft, dim=(-2, -1))
        # Get magnitude spectrum
        magnitude = torch.abs(fft_shift)
        # Log scaling to compress dynamic range
        magnitude = torch.log(magnitude + 1e-8)
        
        # Normalize roughly to [-1, 1] range for backbone stability
        magnitude = (magnitude - magnitude.mean(dim=(-2, -1), keepdim=True)) / (magnitude.std(dim=(-2, -1), keepdim=True) + 1e-5)
        return magnitude


class FeatureExtractorManager(nn.Module):
    """
    Manager that holds the 3 backbones.
    All backbones are loaded from timm, have their classifier heads removed (num_classes=0),
    and are frozen (requires_grad=False).
    """
    def __init__(self):
        super().__init__()
        
        # 1. RGB Branch (EfficientNet B4)
        # Global pooling yields [B, 1792]
        self.rgb_net = timm.create_model(
            cfg.model.rgb_backbone, 
            pretrained=True, 
            num_classes=0
        )
        
        # 2. ViT Branch (ViT Small)
        # Global pooling yields [B, 384]
        self.vit_net = timm.create_model(
            cfg.model.vit_backbone, 
            pretrained=True, 
            num_classes=0
        )
        
        # 3. Frequency Branch
        # Takes FFT magnitude, passes through ResNet18
        # Global pooling yields [B, 512]
        self.freq_transform = FrequencyTransform()
        self.freq_net = timm.create_model(
            cfg.model.freq_backbone, 
            pretrained=True, 
            num_classes=0
        )
        
        self._freeze_all()
        
    def _freeze_all(self):
        """Freezes all parameters to act purely as an extractor."""
        for param in self.parameters():
            param.requires_grad = False
            
        self.eval() # Always in eval mode (batchnorm/dropout frozen)
            
    def get_output_dims(self) -> dict:
        """Returns the output feature dimension for each branch."""
        # Using dummy data to dynamically compute sizes
        with torch.no_grad():
            dummy = torch.randn(1, 3, 224, 224)
            rgb_dim = self.rgb_net(dummy).shape[1]
            vit_dim = self.vit_net(dummy).shape[1]
            freq_dim = self.freq_net(self.freq_transform(dummy)).shape[1]
            
        return {
            "rgb": rgb_dim,
            "vit": vit_dim,
            "freq": freq_dim,
            "total": rgb_dim + vit_dim + freq_dim
        }
        
    def forward(self, x: torch.Tensor) -> dict:
        """
        Extracts features from the input tensor.
        Args:
            x: [B, 3, 224, 224] RGB tensor
        Returns:
            dict of embeddings
        """
        # Ensure we don't compute gradients for extraction
        with torch.no_grad():
            rgb_feat = self.rgb_net(x)
            vit_feat = self.vit_net(x)
            
            freq_in = self.freq_transform(x)
            freq_feat = self.freq_net(freq_in)
            
            # Concatenated super-vector
            concat_feat = torch.cat([rgb_feat, vit_feat, freq_feat], dim=1)
            
            return {
                "rgb": rgb_feat,
                "vit": vit_feat,
                "freq": freq_feat,
                "concat": concat_feat
            }
