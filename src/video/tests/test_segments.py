import pytest
from video.segments import compute_segments
from video.config_video import cfg

def test_hysteresis_thresholding():
    # Configure mock thresholds for test
    cfg.detect.segment_hysteresis_high = 0.8
    cfg.detect.segment_hysteresis_low = 0.5
    cfg.detect.min_segment_frames = 5
    
    fps = 30.0
    
    # Simulate scores. 
    # Starts low, spikes above 0.8, dips to 0.6 (should NOT break segment), 
    # dips to 0.3 (should break segment).
    scores = [
        0.1, 0.2, 0.1,       # REAL
        0.85, 0.9, 0.95,     # FAKE triggers
        0.6, 0.7,            # FAKE continues (above 0.5)
        0.4, 0.2, 0.1        # FAKE ends, REAL resumes
    ]
    
    # 1 score per 10 frames
    indices = [i * 10 for i in range(len(scores))]
    
    segments = compute_segments(scores, indices, fps)
    
    assert len(segments) == 1
    seg = segments[0]
    
    # Segment should be from index 3 (score 0.85) to index 7 (score 0.7)
    assert seg.start_frame == 30
    assert seg.end_frame == 70
    assert seg.label == "FAKE"
    
def test_min_segment_frames_filter():
    cfg.detect.segment_hysteresis_high = 0.8
    cfg.detect.segment_hysteresis_low = 0.5
    cfg.detect.min_segment_frames = 30 # Must be at least 30 frames long
    
    fps = 30.0
    
    # A tiny blip above threshold
    scores = [0.1, 0.9, 0.9, 0.1]
    indices = [0, 10, 20, 30] # Duration of fake segment is 20 - 10 = 10 frames
    
    segments = compute_segments(scores, indices, fps)
    
    # Should be filtered out because 10 < 30
    assert len(segments) == 0
