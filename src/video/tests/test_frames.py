import pytest
import numpy as np
from video.frames import compute_iou, FaceTracker

def test_compute_iou():
    # Identical boxes
    box1 = np.array([0, 0, 100, 100])
    assert compute_iou(box1, box1) == 1.0
    
    # Non-overlapping
    box2 = np.array([101, 101, 200, 200])
    assert compute_iou(box1, box2) == 0.0
    
    # Partial overlap
    box3 = np.array([50, 50, 150, 150])
    iou = compute_iou(box1, box3)
    assert 0.0 < iou < 1.0
    
def test_face_tracker_initial():
    tracker = FaceTracker()
    
    # Frame center
    cx, cy = (960, 540)
    
    # Two boxes, one big/central, one small/edge
    boxes = np.array([
        [0, 0, 50, 50],             # Small, far
        [900, 480, 1020, 600]       # Big, central
    ])
    
    best_box = tracker.select_best_face(boxes, (cx, cy))
    assert np.array_equal(best_box, boxes[1])
    
def test_face_tracker_iou_continuity():
    tracker = FaceTracker(iou_threshold=0.3)
    cx, cy = (960, 540)
    
    # First frame, picks central box
    boxes1 = np.array([
        [900, 480, 1020, 600]
    ])
    tracker.select_best_face(boxes1, (cx, cy))
    
    # Second frame, original box shifted slightly, PLUS a new huge box
    boxes2 = np.array([
        [0, 0, 500, 500],           # Huge new box
        [905, 485, 1025, 605]       # Shifted original box
    ])
    
    # Should pick the shifted box due to IoU, ignoring the huge one
    best_box = tracker.select_best_face(boxes2, (cx, cy))
    assert np.array_equal(best_box, boxes2[1])
