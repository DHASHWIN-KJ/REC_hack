"""
src/video/calibration.py
Temperature scaling implementation for model calibration.
Ensures that a model output of 0.9 actually implies 90% confidence.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn import functional as F

class TemperatureScaler(nn.Module):
    """
    Learns a single scalar temperature parameter to scale logits.
    Typically trained on the validation set after the main model is frozen.
    """
    def __init__(self):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1) * 1.5)
        
    def forward(self, logits: torch.Tensor) -> torch.Tensor:
        """Scales logits and applies sigmoid for binary classification."""
        return torch.sigmoid(logits / self.temperature)
        
    def calibrate(self, valid_logits: torch.Tensor, valid_labels: torch.Tensor, lr: float = 0.01, max_iter: int = 50):
        """
        Optimizes the temperature using NLL loss on a validation set.
        Args:
            valid_logits: [N] tensor of pre-sigmoid raw logits
            valid_labels: [N] tensor of binary labels (0.0 or 1.0)
        """
        optimizer = optim.LBFGS([self.temperature], lr=lr, max_iter=max_iter)
        
        def eval_loss():
            optimizer.zero_grad()
            scaled_logits = valid_logits / self.temperature
            loss = F.binary_cross_entropy_with_logits(scaled_logits, valid_labels)
            loss.backward()
            return loss
            
        optimizer.step(eval_loss)
        return self.temperature.item()
