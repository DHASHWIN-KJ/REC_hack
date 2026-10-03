import pytest
from pathlib import Path
from video.data.splits import _parse_id, generate_splits, METHODS, OOD_METHOD

def test_parse_id():
    # Standard FF++
    assert _parse_id("000_003.mp4") == "000"
    assert _parse_id("999_123.mp4") == "999"
    # Original
    assert _parse_id("001.mp4") == "001"
    # DFD (will return '01' but we don't use DFD for train splits anyway)
    assert _parse_id("01_02__meeting.mp4") == "01"

def test_split_identity_leakage(monkeypatch):
    """
    Ensures that no identity target in the train set ever appears in val or test.
    We mock load_all_video_records to provide a controlled subset of data.
    """
    
    # Mock data
    def mock_load(csv_dir):
        return {
            "original": [
                {"File Path": "000.mp4", "Label": "REAL"},
                {"File Path": "001.mp4", "Label": "REAL"},
                {"File Path": "002.mp4", "Label": "REAL"},
                {"File Path": "003.mp4", "Label": "REAL"},
                {"File Path": "004.mp4", "Label": "REAL"},
            ],
            "Deepfakes": [
                {"File Path": "000_001.mp4", "Label": "FAKE"},
                {"File Path": "001_000.mp4", "Label": "FAKE"},
                {"File Path": "002_003.mp4", "Label": "FAKE"},
                {"File Path": "003_002.mp4", "Label": "FAKE"},
                {"File Path": "004_001.mp4", "Label": "FAKE"},
            ],
            OOD_METHOD: [
                {"File Path": "01_02__mock.mp4", "Label": "FAKE"}
            ]
        }
        
    import video.data.splits
    monkeypatch.setattr(video.data.splits, "load_all_video_records", mock_load)
    
    # Generate splits
    splits = generate_splits("dummy_dir")
    
    # Extract sets of IDs present in each split
    def extract_ids(records):
        return set(_parse_id(r["video_path"]) for r in records)
        
    train_ids = extract_ids(splits["train"])
    val_ids = extract_ids(splits["val"])
    test_ids = extract_ids(splits["test"])
    ood_ids = extract_ids(splits["ood_test"])
    
    # 1. Assert no overlap between train, val, and test
    assert train_ids.isdisjoint(val_ids), "Leakage between train and val!"
    assert train_ids.isdisjoint(test_ids), "Leakage between train and test!"
    assert val_ids.isdisjoint(test_ids), "Leakage between val and test!"
    
    # 2. Assert OOD set is ONLY in ood_test
    # (Since we mocked it with an ID '01' that doesn't exist in original, 
    # it won't be mapped to standard splits)
    assert len(splits["ood_test"]) == 1
    assert splits["ood_test"][0]["method"] == OOD_METHOD
