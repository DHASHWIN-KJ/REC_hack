"""
src/video/evidence.py
Explainability module. Stubbed for Hackathon Phase G.
Future implementation: Generates Grad-CAM or Attention Rollout heatmaps 
to explain WHY a specific frame was classified as fake.
"""
import torch

def generate_heatmap(frame_tensor: torch.Tensor, model: torch.nn.Module, target_layer: str = "rgb") -> str:
    """
    Generates a visual heatmap showing which parts of the frame contributed to the FAKE score.
    
    Args:
        frame_tensor: The input RGB tensor [1, 3, 224, 224]
        model: The FullVideoModel
        target_layer: Which branch to visualize ('rgb', 'vit', 'freq')
        
    Returns:
        String path or URI to the generated heatmap image.
    """
    # STUB: For the hackathon, returning a placeholder URL or path.
    # To fully implement, we would attach a backward hook to model.fusion.rgb_net,
    # run a backward pass from the output logit, and compute the Grad-CAM mask.
    return "/static/heatmaps/placeholder.png"
