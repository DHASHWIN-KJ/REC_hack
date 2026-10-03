"""
src/video/frames.py
Handles video decoding, metadata extraction, and face detection/tracking.
Uses MTCNN for robust face detection and simple IoU tracking to maintain the primary subject.
"""
import os
import cv2
import torch
import numpy as np
from pathlib import Path
from pydantic import BaseModel
from typing import List, Tuple, Optional, Dict, Any

try:
    from facenet_pytorch import MTCNN
except ImportError:
    MTCNN = None

from video.config_video import cfg

class VideoMetadata(BaseModel):
    video_path: str
    fps: float
    total_frames: int
    width: int
    height: int
    duration_sec: float

def get_video_metadata(video_path: str | Path) -> VideoMetadata:
    """Extracts metadata from a video using OpenCV."""
    path = str(video_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Video not found: {path}")
        
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Failed to open video: {path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or np.isnan(fps):
        fps = cfg.data.fps_fallback
        
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    cap.release()
    
    duration = total_frames / fps if fps > 0 else 0.0
    
    return VideoMetadata(
        video_path=path,
        fps=fps,
        total_frames=total_frames,
        width=width,
        height=height,
        duration_sec=duration
    )

def compute_iou(box1: np.ndarray, box2: np.ndarray) -> float:
    """Computes Intersection over Union (IoU) for two bounding boxes [x1, y1, x2, y2]."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_area = max(0, x2 - x1) * max(0, y2 - y1)
    if inter_area == 0:
        return 0.0

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    
    union_area = box1_area + box2_area - inter_area
    return inter_area / union_area if union_area > 0 else 0.0

class FaceTracker:
    """Tracks the primary face across frames using IoU."""
    def __init__(self, iou_threshold: float = 0.3):
        self.last_box: Optional[np.ndarray] = None
        self.iou_threshold = iou_threshold
        
    def select_best_face(self, boxes: np.ndarray, frame_center: Tuple[int, int]) -> Optional[np.ndarray]:
        if boxes is None or len(boxes) == 0:
            return None
            
        # If we have a previous box, find the one with highest IoU
        if self.last_box is not None:
            ious = [compute_iou(self.last_box, box) for box in boxes]
            best_idx = np.argmax(ious)
            if ious[best_idx] > self.iou_threshold:
                self.last_box = boxes[best_idx]
                return boxes[best_idx]
                
        # If no previous box or all IoUs were too low, fallback to largest + most central face
        cx, cy = frame_center
        best_box = None
        best_score = -float('inf')
        
        for box in boxes:
            area = (box[2] - box[0]) * (box[3] - box[1])
            box_cx = (box[0] + box[2]) / 2
            box_cy = (box[1] + box[3]) / 2
            
            # Distance from center (negative is better)
            dist = np.sqrt((box_cx - cx)**2 + (box_cy - cy)**2)
            
            # Simple scoring: area - distance_penalty
            score = area - (dist * 2.0)
            if score > best_score:
                best_score = score
                best_box = box
                
        self.last_box = best_box
        return best_box

def extract_faces_from_video(
    video_path: str | Path, 
    sample_rate: int = cfg.model.frame_sample_rate,
    target_size: int = 224,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    margin: int = 20
) -> Dict[str, Any]:
    """
    Decodes video, extracts the primary face per sampled frame, and returns cropped tensors.
    """
    if MTCNN is None:
        raise ImportError("facenet-pytorch is required for face extraction.")
        
    meta = get_video_metadata(video_path)
    cap = cv2.VideoCapture(str(video_path))
    
    # Initialize MTCNN. keep_all=True so we can track and select the right face
    mtcnn = MTCNN(keep_all=True, device=device, margin=margin, post_process=False)
    tracker = FaceTracker()
    
    frame_indices = []
    face_crops = [] # Store as numpy RGB images initially
    
    frame_idx = 0
    center_pt = (meta.width // 2, meta.height // 2)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_idx % sample_rate == 0:
            # Convert BGR (OpenCV) to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            boxes, probs = mtcnn.detect(rgb_frame)
            
            if boxes is not None:
                # Filter low probability boxes
                valid_indices = probs > 0.90
                valid_boxes = boxes[valid_indices]
                
                best_box = tracker.select_best_face(valid_boxes, center_pt)
                
                if best_box is not None:
                    # Crop and resize
                    x1, y1, x2, y2 = map(int, best_box)
                    # Add safety bounds
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(meta.width, x2), min(meta.height, y2)
                    
                    if x2 > x1 and y2 > y1:
                        crop = rgb_frame[y1:y2, x1:x2]
                        resized = cv2.resize(crop, (target_size, target_size))
                        face_crops.append(resized)
                        frame_indices.append(frame_idx)
                        
        frame_idx += 1
        
    cap.release()
    
    # Convert list of numpy arrays to a single PyTorch tensor (N, C, H, W)
    if face_crops:
        # Array shape is (N, H, W, C)
        np_crops = np.array(face_crops, dtype=np.float32) / 255.0
        # Transpose to (N, C, H, W)
        tensor_crops = torch.from_numpy(np_crops).permute(0, 3, 1, 2)
    else:
        tensor_crops = torch.empty((0, 3, target_size, target_size))
        
    return {
        "metadata": meta,
        "frame_indices": frame_indices,
        "faces_tensor": tensor_crops
    }
