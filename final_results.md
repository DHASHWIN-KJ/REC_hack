# Audio deepfake detector: capability report


## v_baseline

300 files (150 real / 150 fake). EER **2.0%**, correct 94.0%, uncertain 5.3%, false alarms 0.0%, misses 1.3%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 28 | 0.0% |
| high_mp3 | 32 | 0.0% |
| high_ogg | 46 | 4.3% |
| low_m4a | 19 | 0.0% |
| low_mp3 | 32 | 0.0% |
| low_ogg | 27 | 0.0% |
| mp3m4a | 51 | 0.0% |
| nocodec | 16 | 0.0% |
| oggm4a | 49 | 0.0% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 33 | 6.4% |
| neural_vocoder_nonautoregressive | 36 | 1.4% |
| traditional_vocoder | 71 | 0.0% |
| unknown | 7 (few) | 0.0% |
| waveform_concatenation | 3 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 42 | 1.8% |
| b) 2-4 s | 160 | 3.1% |
| c) 4-8 s | 98 | 3.1% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 238 | 1.7% |
| trimmed | 62 | 1.2% |


## v_whatsapp

300 files (150 real / 150 fake). EER **3.3%**, correct 85.7%, uncertain 10.7%, false alarms 6.7%, misses 0.7%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 28 | 0.0% |
| high_mp3 | 32 | 6.3% |
| high_ogg | 46 | 4.3% |
| low_m4a | 19 | 0.0% |
| low_mp3 | 32 | 0.0% |
| low_ogg | 27 | 10.9% |
| mp3m4a | 51 | 4.0% |
| nocodec | 16 | 4.2% |
| oggm4a | 49 | 0.0% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 33 | 6.7% |
| neural_vocoder_nonautoregressive | 36 | 1.4% |
| traditional_vocoder | 71 | 1.4% |
| unknown | 7 (few) | 0.0% |
| waveform_concatenation | 3 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 42 | 1.8% |
| b) 2-4 s | 160 | 5.0% |
| c) 4-8 s | 98 | 0.0% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 242 | 2.5% |
| trimmed | 58 | 7.6% |


## v_hidden

300 files (150 real / 150 fake). EER **5.3%**, correct 61.3%, uncertain 37.7%, false alarms 2.0%, misses 0.0%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 6.6% |
| high_mp3 | 29 | 7.0% |
| high_ogg | 30 | 3.8% |
| low_m4a | 41 | 7.4% |
| low_mp3 | 31 | 6.5% |
| low_ogg | 37 | 2.5% |
| mp3m4a | 34 | 9.6% |
| nocodec | 33 | 0.0% |
| oggm4a | 34 | 3.3% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 38 | 14.9% |
| neural_vocoder_nonautoregressive | 13 | 1.0% |
| traditional_vocoder | 86 | 3.7% |
| waveform_concatenation | 13 | 1.3% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 224 | 8.9% |
| b) 2-4 s | 75 | 3.9% |
| c) 4-8 s | 1 (few) | n/a |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 1 (few) | n/a |
| trimmed | 299 | 5.4% |


## Summary

| Test | Files | EER | Correct | Uncertain | False alarms | Misses |
|---|---|---|---|---|---|---|
| v_baseline | 300 | 2.0% | 94.0% | 5.3% | 0.0% | 1.3% |
| v_whatsapp | 300 | 3.3% | 85.7% | 10.7% | 6.7% | 0.7% |
| v_hidden | 300 | 5.3% | 61.3% | 37.7% | 2.0% | 0.0% |
