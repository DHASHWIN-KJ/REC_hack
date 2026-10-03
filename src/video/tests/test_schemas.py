import pytest
from pydantic import ValidationError
from video.schemas import EvidenceBundle, FrameEvidence, VideoSegment

def test_frame_evidence_validation():
    # Valid
    frame = FrameEvidence(frame_index=10, timestamp_sec=0.33, fake_score=0.8)
    assert frame.fake_score == 0.8
    assert frame.heatmap_path is None
    
    # Invalid score (> 1.0)
    with pytest.raises(ValidationError):
        FrameEvidence(frame_index=11, timestamp_sec=0.36, fake_score=1.5)
        
    # Invalid score (< 0.0)
    with pytest.raises(ValidationError):
        FrameEvidence(frame_index=11, timestamp_sec=0.36, fake_score=-0.1)

def test_video_segment_validation():
    seg = VideoSegment(
        start_time_sec=1.0, 
        end_time_sec=2.5, 
        start_frame=30, 
        end_frame=75, 
        avg_score=0.9, 
        label="FAKE"
    )
    assert seg.label == "FAKE"

def test_evidence_bundle_to_core():
    bundle = EvidenceBundle(
        video_id="test_vid",
        video_path="/path/test.mp4",
        fps=30.0,
        total_frames=100,
        overall_fake_score=0.95,
        overall_label="FAKE",
        segments=[
            VideoSegment(
                start_time_sec=0.0, end_time_sec=1.0, 
                start_frame=0, end_frame=30, 
                avg_score=0.1, label="REAL"
            ),
            VideoSegment(
                start_time_sec=1.1, end_time_sec=3.3, 
                start_frame=33, end_frame=99, 
                avg_score=0.98, label="FAKE"
            )
        ]
    )
    
    core_res = bundle.to_core_result()
    
    assert core_res["modality"] == "video"
    assert core_res["score"] == 0.95
    assert core_res["label"] == "FAKE"
    
    # Should only include FAKE segments in the core output for highlights
    assert len(core_res["segments"]) == 1
    assert core_res["segments"][0]["start"] == 1.1
    assert core_res["segments"][0]["score"] == 0.98
