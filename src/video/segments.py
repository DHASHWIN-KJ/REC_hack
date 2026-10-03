"""
src/video/segments.py
Logic for converting raw frame-by-frame scores into continuous, smooth temporal segments.
Uses hysteresis thresholding to prevent segments from flickering on and off rapidly.
"""
from typing import List, Tuple
from video.config_video import cfg
from video.schemas import VideoSegment

def compute_segments(
    frame_scores: List[float], 
    frame_indices: List[int],
    fps: float
) -> List[VideoSegment]:
    """
    Applies hysteresis thresholding to identify contiguous FAKE segments.
    
    Args:
        frame_scores: List of float scores (0.0 to 1.0) for each sampled frame.
        frame_indices: The actual video frame index for each score.
        fps: Frames per second of the original video.
        
    Returns:
        List of VideoSegment objects representing FAKE regions.
    """
    if not frame_scores:
        return []
        
    high_thresh = cfg.detect.segment_hysteresis_high
    low_thresh = cfg.detect.segment_hysteresis_low
    min_frames = cfg.detect.min_segment_frames
    
    segments = []
    in_segment = False
    start_idx = 0
    
    for i, score in enumerate(frame_scores):
        if not in_segment and score >= high_thresh:
            # Trigger start of a fake segment
            in_segment = True
            start_idx = i
        elif in_segment and score < low_thresh:
            # Trigger end of a fake segment
            in_segment = False
            end_idx = i - 1
            
            _add_segment(segments, start_idx, end_idx, frame_scores, frame_indices, fps, min_frames)
            
    # Handle case where video ends while inside a segment
    if in_segment:
        _add_segment(segments, start_idx, len(frame_scores) - 1, frame_scores, frame_indices, fps, min_frames)
        
    return segments

def _add_segment(segments, start_idx, end_idx, scores, indices, fps, min_frames):
    """Helper to compute stats and append a segment if it meets minimum duration."""
    # The actual video frame numbers
    start_frame = indices[start_idx]
    end_frame = indices[end_idx]
    
    duration_frames = end_frame - start_frame + 1
    
    if duration_frames >= min_frames:
        segment_scores = scores[start_idx : end_idx + 1]
        avg_score = sum(segment_scores) / len(segment_scores)
        
        segments.append(
            VideoSegment(
                start_time_sec=start_frame / fps,
                end_time_sec=end_frame / fps,
                start_frame=start_frame,
                end_frame=end_frame,
                avg_score=avg_score,
                label="FAKE"
            )
        )
