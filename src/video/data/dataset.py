"""
src/video/data/dataset.py
PyTorch Dataset implementation for FaceForensics++ deepfake detection.
Integrates the identity splits, frames extraction, and augmentations.
"""
import torch
from torch.utils.data import Dataset
from pathlib import Path

from video.data.splits import generate_splits
from video.data.augmentation import get_train_transforms, get_val_transforms
from video.frames import extract_faces_from_video
from video.config_video import cfg, DATA_ROOT

class FaceForensicsDataset(Dataset):
    def __init__(self, split: str = "train", dataset_dir: str = None, transform=None):
        """
        Args:
            split: 'train', 'val', 'test', or 'ood_test'
            dataset_dir: Path to the dataset_videos root folder
        """
        self.split_name = split
        self.dataset_dir = Path(dataset_dir) if dataset_dir else Path(DATA_ROOT)
        
        # Load the split records
        splits = generate_splits(self.dataset_dir / "csv")
        if split not in splits:
            raise ValueError(f"Invalid split '{split}'. Must be one of {list(splits.keys())}")
            
        self.records = splits[split]
        
        # Setup transforms
        if transform:
            self.transform = transform
        else:
            self.transform = get_train_transforms() if split == "train" else get_val_transforms()
            
    def __len__(self):
        return len(self.records)
        
    def __getitem__(self, idx):
        record = self.records[idx]
        
        # Full path to video
        video_path = self.dataset_dir / record["video_path"]
        
        # Extract faces [N, C, H, W]
        # For training, we might only take a random snippet. For validation, take all sampled frames.
        # This implementation extracts all (or up to a limit) and returns the tensor.
        try:
            extraction_result = extract_faces_from_video(
                video_path,
                sample_rate=cfg.model.frame_sample_rate
            )
            faces_tensor = extraction_result["faces_tensor"] # [N, 3, 224, 224]
        except Exception as e:
            # Fallback for corrupted videos: return an empty tensor and dummy label
            # Real-world datasets often have a few unreadable files
            print(f"Error processing {video_path}: {e}")
            faces_tensor = torch.zeros((1, 3, 224, 224))
            
        # Apply transforms. torchvision v2 can take [N, C, H, W] directly!
        if len(faces_tensor) > 0:
            faces_tensor = self.transform(faces_tensor)
            
        # Label: 1 for FAKE, 0 for REAL
        label = 1.0 if record["label"] == "FAKE" else 0.0
        
        return faces_tensor, torch.tensor(label, dtype=torch.float32)
