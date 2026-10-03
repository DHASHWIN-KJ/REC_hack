#!/usr/bin/env python3
"""
scripts/video_train.py
Main training loop for the Fusion and Temporal modules using pre-cached embeddings.
Since embeddings are pre-computed, this trains extremely fast.
"""

import sys
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from tqdm import tqdm

# Add src to python path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from video.temporal import FullVideoModel
from video.calibration import TemperatureScaler
from video.data.splits import generate_splits
from video.config_video import cfg

class CachedEmbeddingDataset(Dataset):
    def __init__(self, split_name: str, max_seq_len: int = 60):
        self.split_name = split_name
        self.max_seq_len = max_seq_len
        self.embed_dir = PROJECT_ROOT / "data" / "embeddings"
        
        splits = generate_splits()
        records = splits.get(split_name, [])
        
        # Only keep records that actually have a cached .pt file
        self.valid_files = []
        for r in records:
            pt_path = self.embed_dir / Path(r["video_path"]).parent / f"{Path(r['video_path']).stem}.pt"
            if pt_path.exists():
                self.valid_files.append(pt_path)
                
        print(f"[{split_name}] Found {len(self.valid_files)} cached embedding files.")
        
    def __len__(self):
        return len(self.valid_files)
        
    def __getitem__(self, idx):
        data = torch.load(self.valid_files[idx], weights_only=True)
        
        rgb = data["rgb"]       # [N, 1792]
        vit = data["vit"]       # [N, 384]
        freq = data["freq"]     # [N, 512]
        label = data["label"]   # float
        
        N = rgb.shape[0]
        
        # Truncate or pad to max_seq_len
        if N > self.max_seq_len:
            # Random crop for training, deterministic crop for val
            if self.split_name == "train":
                start = torch.randint(0, N - self.max_seq_len + 1, (1,)).item()
            else:
                start = 0
            end = start + self.max_seq_len
            
            rgb = rgb[start:end]
            vit = vit[start:end]
            freq = freq[start:end]
        elif N < self.max_seq_len:
            # Zero pad
            pad_len = self.max_seq_len - N
            rgb = torch.cat([rgb, torch.zeros(pad_len, rgb.shape[1])])
            vit = torch.cat([vit, torch.zeros(pad_len, vit.shape[1])])
            freq = torch.cat([freq, torch.zeros(pad_len, freq.shape[1])])
            
        return rgb, vit, freq, torch.tensor(label, dtype=torch.float32)

def train_epoch(model, dataloader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for rgb, vit, freq, labels in tqdm(dataloader, desc="Training", leave=False):
        rgb, vit, freq, labels = rgb.to(device), vit.to(device), freq.to(device), labels.to(device)
        
        optimizer.zero_grad()
        out = model(rgb, vit, freq)
        logits = out["video_logits"]
        
        loss = criterion(logits, labels)
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        total_loss += loss.item()
        preds = (torch.sigmoid(logits) > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        
    return total_loss / len(dataloader), correct / total

@torch.no_grad()
def validate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    all_logits = []
    all_labels = []
    
    for rgb, vit, freq, labels in dataloader:
        rgb, vit, freq, labels = rgb.to(device), vit.to(device), freq.to(device), labels.to(device)
        
        out = model(rgb, vit, freq)
        logits = out["video_logits"]
        
        loss = criterion(logits, labels)
        total_loss += loss.item()
        
        preds = (torch.sigmoid(logits) > 0.5).float()
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        
        all_logits.append(logits.cpu())
        all_labels.append(labels.cpu())
        
    return total_loss / len(dataloader), correct / total, torch.cat(all_logits), torch.cat(all_labels)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on {device}")
    
    # Hyperparams
    epochs = 15
    batch_size = 32
    lr = 3e-4
    patience = 3
    
    train_ds = CachedEmbeddingDataset("train")
    val_ds = CachedEmbeddingDataset("val")
    
    if len(train_ds) == 0:
        print("Error: No cached embeddings found. Please run scripts/video_extract_embeddings.py first.")
        return
        
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=2, drop_last=True)
    val_dl = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=2)
    
    model = FullVideoModel().to(device)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.BCEWithLogitsLoss()
    
    best_val_acc = 0.0
    patience_counter = 0
    
    models_dir = PROJECT_ROOT / "data" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    save_path = models_dir / "video_fusion_best.pt"
    
    print("Starting Training Loop...")
    
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = train_epoch(model, train_dl, optimizer, criterion, device)
        val_loss, val_acc, val_logits, val_labels = validate(model, val_dl, criterion, device)
        
        print(f"Epoch {epoch:02d} | Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            
            # Save best weights
            torch.save(model.state_dict(), save_path)
            
            # Fit temperature scaler on the best validation logits
            scaler = TemperatureScaler()
            t = scaler.calibrate(val_logits, val_labels)
            torch.save(scaler.state_dict(), models_dir / "video_scaler.pt")
            print(f"  -> Saved new best model. Calibrated Temperature: {t:.3f}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered after {epoch} epochs.")
                break
                
    print(f"Training Complete. Best Val Accuracy: {best_val_acc:.4f}")

if __name__ == "__main__":
    main()
