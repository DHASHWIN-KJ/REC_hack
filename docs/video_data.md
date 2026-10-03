# FaceForensics++ Dataset Inspection Report

Dataset root: `C:\Users\DHASHWIN K J\OneDrive\Desktop\rec\REC_The_ONE\src\video\dataset_videos`
CSV directory: `C:\Users\DHASHWIN K J\OneDrive\Desktop\rec\REC_The_ONE\src\video\dataset_videos\csv`

## 1. Folder Scan (on-disk video count)

| Folder | Exists | Video Files (.mp4) |
|--------|--------|--------------------|
| original | ✅ | 1000 |
| Deepfakes | ✅ | 1000 |
| Face2Face | ✅ | 1000 |
| FaceShifter | ✅ | 1000 |
| FaceSwap | ✅ | 1000 |
| NeuralTextures | ✅ | 1000 |
| DeepFakeDetection | ✅ | 1000 |

## 2. CSV Metadata Analysis

CSV files found: 10
  - `DeepFakeDetection.csv` (92.9 KB)
  - `Deepfakes.csv` (52.2 KB)
  - `Face2Face.csv` (52.2 KB)
  - `FaceShifter.csv` (54.2 KB)
  - `FaceSwap.csv` (51.2 KB)
  - `FF++_Metadata.csv` (413.2 KB)
  - `FF++_Metadata_Shuffled.csv` (413.2 KB)
  - `Mean_Data.csv` (0.4 KB)
  - `NeuralTextures.csv` (57.1 KB)
  - `original.csv` (47.3 KB)

### Video counts from CSVs

| Folder | CSV Rows | Disk Files | Match? | Label |
|--------|----------|------------|--------|-------|
| original | 1000 | 1000 | ✅ | REAL |
| Deepfakes | 1000 | 1000 | ✅ | FAKE |
| Face2Face | 1000 | 1000 | ✅ | FAKE |
| FaceShifter | 1000 | 1000 | ✅ | FAKE |
| FaceSwap | 1000 | 1000 | ✅ | FAKE |
| NeuralTextures | 1000 | 1000 | ✅ | FAKE |
| DeepFakeDetection | 1000 | 1000 | ✅ | FAKE |

**Totals:** 1000 real, 5000 fake (5 methods), 1000 DFD (OOD)
**Imbalance ratio (fake:real):** 5.0:1

## 3. Per-Folder Video Statistics (from CSV)

### original (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 287 | 458 | 1814 | 509.13 |
| Width | 272 | 854 | 1920 | 1036.35 |
| Height | 480 | 480 | 1080 | 636.72 |
| File Size (MB) | 0.32 | 1.36 | 13.45 | 1.85 |
| Est. Bitrate (Mbps) | 0.16 | 0.68 | 5.17 | 0.90 |

Codecs: h264
Top resolutions: 1280x720(325), 640x480(257), 1920x1080(123), 854x480(98), 656x480(66)

### Deepfakes (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 287 | 458 | 1814 | 509.13 |
| Width | 272 | 854 | 1920 | 1036.35 |
| Height | 480 | 480 | 1080 | 636.72 |
| File Size (MB) | 0.33 | 1.4 | 13.45 | 1.9 |
| Est. Bitrate (Mbps) | 0.17 | 0.69 | 5.31 | 0.93 |

Codecs: h264
Top resolutions: 1280x720(325), 640x480(257), 1920x1080(123), 854x480(98), 656x480(66)

### Face2Face (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 287 | 458 | 1814 | 509.13 |
| Width | 256 | 832 | 1920 | 1030.91 |
| Height | 480 | 480 | 1080 | 636.72 |
| File Size (MB) | 0.33 | 1.38 | 19.99 | 1.86 |
| Est. Bitrate (Mbps) | 0.16 | 0.68 | 5.20 | 0.91 |

Codecs: h264
Top resolutions: 640x480(348), 1280x720(325), 1920x1080(123), 832x480(102), 576x480(52)

### FaceShifter (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 287 | 458 | 1814 | 509.13 |
| Width | 272 | 854 | 1920 | 1036.35 |
| Height | 480 | 480 | 1080 | 636.72 |
| File Size (MB) | 0.3 | 1.32 | 12.49 | 1.83 |
| Est. Bitrate (Mbps) | 0.15 | 0.67 | 5.03 | 0.89 |

Codecs: h264
Top resolutions: 1280x720(325), 640x480(257), 1920x1080(123), 854x480(98), 656x480(66)

### FaceSwap (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 287 | 375 | 1038 | 406.14 |
| Width | 272 | 854 | 1920 | 1036.35 |
| Height | 480 | 480 | 1080 | 636.72 |
| File Size (MB) | 0.36 | 1.19 | 11.36 | 1.56 |
| Est. Bitrate (Mbps) | 0.20 | 0.72 | 5.24 | 0.95 |

Codecs: h264
Top resolutions: 1280x720(325), 640x480(257), 1920x1080(123), 854x480(98), 656x480(66)

### NeuralTextures (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 287 | 375 | 1038 | 406.14 |
| Width | 256 | 832 | 1920 | 1030.91 |
| Height | 480 | 480 | 1080 | 636.72 |
| File Size (MB) | 0.31 | 1.1 | 11.2 | 1.46 |
| Est. Bitrate (Mbps) | 0.16 | 0.66 | 5.18 | 0.89 |

Codecs: h264
Top resolutions: 640x480(348), 1280x720(325), 1920x1080(123), 832x480(102), 576x480(52)

### DeepFakeDetection (1000 videos)

| Metric | Min | Median | Max | Mean |
|--------|-----|--------|-----|------|
| Frame Count | 5 | 723 | 1620 | 733.79 |
| Width | 1920 | 1920 | 1920 | 1920.0 |
| Height | 1080 | 1080 | 1080 | 1080.0 |
| File Size (MB) | 0.15 | 5.45 | 25.69 | 6.64 |
| Est. Bitrate (Mbps) | 0.89 | 1.82 | 7.20 | 2.10 |

Codecs: h264
Top resolutions: 1920x1080(1000)

## 4. Compression Level Inference

Estimated from bitrate: raw (≥10 Mbps), c23 (1-10 Mbps), c40 (<1 Mbps)

- **original**: raw=0 (0%), c23=292 (29%), c40=708 (71%) → likely **c40**
- **Deepfakes**: raw=0 (0%), c23=313 (31%), c40=687 (69%) → likely **c40**
- **Face2Face**: raw=0 (0%), c23=304 (30%), c40=696 (70%) → likely **c40**
- **FaceShifter**: raw=0 (0%), c23=285 (28%), c40=715 (72%) → likely **c40**
- **FaceSwap**: raw=0 (0%), c23=327 (33%), c40=673 (67%) → likely **c40**
- **NeuralTextures**: raw=0 (0%), c23=280 (28%), c40=720 (72%) → likely **c40**
- **DeepFakeDetection**: raw=0 (0%), c23=982 (98%), c40=18 (2%) → likely **c23**

## 5. CSV Structure Inspection

### DeepFakeDetection.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'DeepFakeDetection/01_02__meeting_serious__YVGY8LOK.mp4', 'Label': 'FAKE', 'Frame Count': '1044', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '6.43'}
{'': '1', 'File Path': 'DeepFakeDetection/01_02__outside_talking_still_laughing__YVGY8LOK.mp4', 'Label': 'FAKE', 'Frame Count': '727', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '5.05'}
{'': '2', 'File Path': 'DeepFakeDetection/01_02__talking_against_wall__YVGY8LOK.mp4', 'Label': 'FAKE', 'Frame Count': '841', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '3.31'}
```

### Deepfakes.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'Deepfakes/000_003.mp4', 'Label': 'FAKE', 'Frame Count': '396', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.85'}
{'': '1', 'File Path': 'Deepfakes/001_870.mp4', 'Label': 'FAKE', 'Frame Count': '460', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.74'}
{'': '2', 'File Path': 'Deepfakes/002_006.mp4', 'Label': 'FAKE', 'Frame Count': '693', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '1.98'}
```

### Face2Face.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'Face2Face/000_003.mp4', 'Label': 'FAKE', 'Frame Count': '303', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.64'}
{'': '1', 'File Path': 'Face2Face/001_870.mp4', 'Label': 'FAKE', 'Frame Count': '604', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '3.51'}
{'': '2', 'File Path': 'Face2Face/002_006.mp4', 'Label': 'FAKE', 'Frame Count': '310', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '0.91'}
```

### FaceShifter.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'FaceShifter/000_003.mp4', 'Label': 'FAKE', 'Frame Count': '396', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.85'}
{'': '1', 'File Path': 'FaceShifter/001_870.mp4', 'Label': 'FAKE', 'Frame Count': '460', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.75'}
{'': '2', 'File Path': 'FaceShifter/002_006.mp4', 'Label': 'FAKE', 'Frame Count': '693', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.1'}
```

### FaceSwap.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'FaceSwap/000_003.mp4', 'Label': 'FAKE', 'Frame Count': '303', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.69'}
{'': '1', 'File Path': 'FaceSwap/001_870.mp4', 'Label': 'FAKE', 'Frame Count': '460', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.77'}
{'': '2', 'File Path': 'FaceSwap/002_006.mp4', 'Label': 'FAKE', 'Frame Count': '310', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '0.96'}
```

### FF++_Metadata.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 7000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'DeepFakeDetection/01_02__meeting_serious__YVGY8LOK.mp4', 'Label': 'FAKE', 'Frame Count': '1044', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '6.43'}
{'': '1', 'File Path': 'DeepFakeDetection/01_02__outside_talking_still_laughing__YVGY8LOK.mp4', 'Label': 'FAKE', 'Frame Count': '727', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '5.05'}
{'': '2', 'File Path': 'DeepFakeDetection/01_02__talking_against_wall__YVGY8LOK.mp4', 'Label': 'FAKE', 'Frame Count': '841', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '3.31'}
```

### FF++_Metadata_Shuffled.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 7000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'original/500.mp4', 'Label': 'REAL', 'Frame Count': '292', 'Width': '1920', 'Height': '1080', 'Codec': 'h264', 'File Size(MB)': '2.66'}
{'': '1', 'File Path': 'Face2Face/944_032.mp4', 'Label': 'FAKE', 'Frame Count': '310', 'Width': '704', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.46'}
{'': '2', 'File Path': 'Face2Face/024_073.mp4', 'Label': 'FAKE', 'Frame Count': '703', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '1.14'}
```

### Mean_Data.csv
Columns: `['', 'Frame Count Mean', 'Width Mean', 'Height Mean', 'File Size(MB) Mean']`
Row count: 7

No split columns found.

Sample rows:
```
{'': 'DeepFakeDetection', 'Frame Count Mean': '733.791', 'Width Mean': '1920.0', 'Height Mean': '1080.0', 'File Size(MB) Mean': '6.6376100000000005'}
{'': 'Deepfakes', 'Frame Count Mean': '509.128', 'Width Mean': '1036.348', 'Height Mean': '636.718', 'File Size(MB) Mean': '1.90042'}
{'': 'Face2Face', 'Frame Count Mean': '509.128', 'Width Mean': '1030.912', 'Height Mean': '636.718', 'File Size(MB) Mean': '1.8566599999999998'}
```

### NeuralTextures.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'NeuralTextures/000_003.mp4', 'Label': 'FAKE', 'Frame Count': '303', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.62'}
{'': '1', 'File Path': 'NeuralTextures/001_870.mp4', 'Label': 'FAKE', 'Frame Count': '460', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.71'}
{'': '2', 'File Path': 'NeuralTextures/002_006.mp4', 'Label': 'FAKE', 'Frame Count': '310', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '0.91'}
```

### original.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 1000

No split columns found.

Sample rows:
```
{'': '0', 'File Path': 'original/000.mp4', 'Label': 'REAL', 'Frame Count': '396', 'Width': '640', 'Height': '480', 'Codec': 'h264', 'File Size(MB)': '0.85'}
{'': '1', 'File Path': 'original/001.mp4', 'Label': 'REAL', 'Frame Count': '460', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.78'}
{'': '2', 'File Path': 'original/002.mp4', 'Label': 'REAL', 'Frame Count': '693', 'Width': '1280', 'Height': '720', 'Codec': 'h264', 'File Size(MB)': '2.02'}
```

## 6. Fake→Original Filename Matching

Original video IDs found: 1000

### Deepfakes: 1000/1000 matched, 0 unmatched

### Face2Face: 1000/1000 matched, 0 unmatched

### FaceShifter: 1000/1000 matched, 0 unmatched

### FaceSwap: 1000/1000 matched, 0 unmatched

### NeuralTextures: 1000/1000 matched, 0 unmatched

### DeepFakeDetection: Different naming convention (not target_source.mp4)
  Sample filenames: ['01_02__meeting_serious__YVGY8LOK.mp4', '01_02__outside_talking_still_laughing__YVGY8LOK.mp4', '01_02__talking_against_wall__YVGY8LOK.mp4', '01_02__walk_down_hall_angry__YVGY8LOK.mp4', '01_02__walking_down_indoor_hall_disgust__YVGY8LOK.mp4']
  Total videos: 1000

## 7. Class Imbalance Summary

| Set | Count | Ratio to Original |
|-----|-------|--------------------|
| original (REAL) | 1000 | 1.0 |
| Deepfakes (FAKE) | 1000 | 1.00 |
| Face2Face (FAKE) | 1000 | 1.00 |
| FaceShifter (FAKE) | 1000 | 1.00 |
| FaceSwap (FAKE) | 1000 | 1.00 |
| NeuralTextures (FAKE) | 1000 | 1.00 |
| **Total FAKE** | **5000** | **5.0** |
| DeepFakeDetection (OOD) | 1000 | 1.00 |

## 8. Official Train/Val/Test Split Check

### FF++_Metadata.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 7000
No split columns found in this CSV.

### FF++_Metadata_Shuffled.csv
Columns: `['', 'File Path', 'Label', 'Frame Count', 'Width', 'Height', 'Codec', 'File Size(MB)']`
Row count: 7000
No split columns found in this CSV.

No separate split files found in csv/ directory.
No split files in dataset root either.

**Conclusion:** If no official splits are found, we will create deterministic identity-aware splits (seed-based) in `src/video/data/splits.py`.

## 9. Summary & Recommendations

- **1000** real videos, **5000** fake videos across **5** methods, **1000** DFD (OOD)
- Imbalance: ~5:1 fake-to-real
- All videos are h264 codec
- Variable resolutions (480p to 1080p)
- Filename pattern `<target>_<source>.mp4` confirmed for standard methods
- DFD uses a different naming convention
- Compression level appears to be **c23** based on bitrate analysis
