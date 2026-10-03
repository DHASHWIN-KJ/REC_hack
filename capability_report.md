# Audio deepfake detector: capability report


## t1_baseline

300 files (150 real / 150 fake). EER **1.3%**, correct 94.3%, uncertain 4.0%, false alarms 2.0%, misses 1.3%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 0.0% |
| high_ogg | 34 | 0.0% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 0.0% |
| low_ogg | 46 | 0.0% |
| mp3m4a | 43 | 2.0% |
| nocodec | 21 | 0.0% |
| oggm4a | 54 | 3.7% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 2.2% |
| neural_vocoder_nonautoregressive | 41 | 0.0% |
| traditional_vocoder | 61 | 0.3% |
| unknown | 6 (few) | 0.3% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 1.5% |
| b) 2-4 s | 163 | 1.2% |
| c) 4-8 s | 93 | 0.0% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 241 | 0.0% |
| trimmed | 59 | 5.1% |


## t2_whatsapp

300 files (150 real / 150 fake). EER **3.0%**, correct 85.7%, uncertain 7.3%, false alarms 13.3%, misses 0.7%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 0.0% |
| high_ogg | 34 | 0.0% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 0.0% |
| low_ogg | 46 | 0.0% |
| mp3m4a | 43 | 4.8% |
| nocodec | 21 | 0.0% |
| oggm4a | 54 | 3.7% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 4.4% |
| neural_vocoder_nonautoregressive | 41 | 0.3% |
| traditional_vocoder | 61 | 1.5% |
| unknown | 6 (few) | 0.7% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 1.5% |
| b) 2-4 s | 163 | 2.5% |
| c) 4-8 s | 93 | 0.0% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 243 | 1.2% |
| trimmed | 57 | 10.5% |


## t2_mp3_low

300 files (150 real / 150 fake). EER **2.3%**, correct 88.3%, uncertain 5.0%, false alarms 12.0%, misses 1.3%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 0.0% |
| high_ogg | 34 | 6.1% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 0.0% |
| low_ogg | 46 | 0.0% |
| mp3m4a | 43 | 4.8% |
| nocodec | 21 | 0.0% |
| oggm4a | 54 | 3.7% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 4.4% |
| neural_vocoder_nonautoregressive | 41 | 0.0% |
| traditional_vocoder | 61 | 0.8% |
| unknown | 6 (few) | 0.0% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 1.5% |
| b) 2-4 s | 163 | 1.9% |
| c) 4-8 s | 93 | 2.2% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 241 | 1.7% |
| trimmed | 59 | 3.7% |


## t3_noise20

300 files (150 real / 150 fake). EER **2.0%**, correct 94.3%, uncertain 3.3%, false alarms 0.7%, misses 4.0%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 0.0% |
| high_ogg | 34 | 0.0% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 0.0% |
| low_ogg | 46 | 0.0% |
| mp3m4a | 43 | 4.8% |
| nocodec | 21 | 4.2% |
| oggm4a | 54 | 5.5% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 7.7% |
| neural_vocoder_nonautoregressive | 41 | 1.6% |
| traditional_vocoder | 61 | 0.3% |
| unknown | 6 (few) | 0.3% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 3.0% |
| b) 2-4 s | 163 | 2.5% |
| c) 4-8 s | 93 | 3.1% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 1 (few) | n/a |
| trimmed | 299 | 2.0% |


## t3_noise10

300 files (150 real / 150 fake). EER **4.0%**, correct 89.3%, uncertain 7.0%, false alarms 0.7%, misses 6.7%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 4.2% |
| high_ogg | 34 | 0.0% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 0.0% |
| low_ogg | 46 | 0.0% |
| mp3m4a | 43 | 2.0% |
| nocodec | 21 | 4.2% |
| oggm4a | 54 | 5.5% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 6.0% |
| neural_vocoder_nonautoregressive | 41 | 5.4% |
| traditional_vocoder | 61 | 3.0% |
| unknown | 6 (few) | 2.3% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 7.6% |
| b) 2-4 s | 163 | 7.4% |
| c) 4-8 s | 93 | 1.3% |


## t3_noise5

300 files (150 real / 150 fake). EER **6.3%**, correct 86.0%, uncertain 9.7%, false alarms 3.3%, misses 5.3%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 4.2% |
| high_ogg | 34 | 3.6% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 7.1% |
| low_ogg | 46 | 0.0% |
| mp3m4a | 43 | 4.8% |
| nocodec | 21 | 0.0% |
| oggm4a | 54 | 7.4% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 5.8% |
| neural_vocoder_nonautoregressive | 41 | 7.0% |
| traditional_vocoder | 61 | 5.1% |
| unknown | 6 (few) | 13.3% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 18.2% |
| b) 2-4 s | 163 | 9.8% |
| c) 4-8 s | 93 | 1.3% |


## t4_crop2s

300 files (150 real / 150 fake). EER **6.3%**, correct 85.0%, uncertain 11.7%, false alarms 6.0%, misses 0.7%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 0.0% |
| high_mp3 | 22 | 0.0% |
| high_ogg | 34 | 6.1% |
| low_m4a | 21 | 0.0% |
| low_mp3 | 28 | 7.1% |
| low_ogg | 46 | 1.9% |
| mp3m4a | 43 | 4.8% |
| nocodec | 21 | 0.0% |
| oggm4a | 54 | 12.9% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 12.1% |
| neural_vocoder_nonautoregressive | 41 | 4.4% |
| traditional_vocoder | 61 | 4.5% |
| unknown | 6 (few) | 13.0% |
| waveform_concatenation | 1 (few) | 0.0% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 44 | 1.5% |
| b) 2-4 s | 256 | 5.1% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 90 | 0.0% |
| trimmed | 210 | 7.5% |


## t4_crop1s

300 files (150 real / 150 fake). EER **14.0%**, correct 70.3%, uncertain 19.0%, false alarms 20.0%, misses 1.3%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 31 | 12.9% |
| high_mp3 | 22 | 13.3% |
| high_ogg | 34 | 8.6% |
| low_m4a | 21 | 14.1% |
| low_mp3 | 28 | 7.1% |
| low_ogg | 46 | 15.2% |
| mp3m4a | 43 | 23.1% |
| nocodec | 21 | 0.0% |
| oggm4a | 54 | 18.4% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 41 | 16.9% |
| neural_vocoder_nonautoregressive | 41 | 14.0% |
| traditional_vocoder | 61 | 8.4% |
| unknown | 6 (few) | 18.7% |
| waveform_concatenation | 1 (few) | 1.7% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 14 | 3.8% |
| trimmed | 286 | 14.0% |


## t5_hidden

300 files (150 real / 150 fake). EER **7.3%**, correct 83.7%, uncertain 11.3%, false alarms 5.3%, misses 4.7%.


**By codec**

| Group | Files | EER |
|---|---|---|
| high_m4a | 29 | 3.3% |
| high_mp3 | 41 | 9.8% |
| high_ogg | 30 | 0.0% |
| low_m4a | 42 | 3.1% |
| low_mp3 | 33 | 6.1% |
| low_ogg | 32 | 6.2% |
| mp3m4a | 28 | 0.0% |
| nocodec | 32 | 0.0% |
| oggm4a | 33 | 15.1% |


**By vocoder type (fakes vs all real)**

| Group | Files | EER |
|---|---|---|
| neural_vocoder_autoregressive | 44 | 14.2% |
| neural_vocoder_nonautoregressive | 8 (few) | 1.0% |
| traditional_vocoder | 85 | 5.0% |
| waveform_concatenation | 13 | 1.7% |


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 216 | 7.9% |
| b) 2-4 s | 84 | 3.5% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 1 (few) | n/a |
| trimmed | 299 | 7.4% |


## Summary

| Test | Files | EER | Correct | Uncertain | False alarms | Misses |
|---|---|---|---|---|---|---|
| t1_baseline | 300 | 1.3% | 94.3% | 4.0% | 2.0% | 1.3% |
| t2_whatsapp | 300 | 3.0% | 85.7% | 7.3% | 13.3% | 0.7% |
| t2_mp3_low | 300 | 2.3% | 88.3% | 5.0% | 12.0% | 1.3% |
| t3_noise20 | 300 | 2.0% | 94.3% | 3.3% | 0.7% | 4.0% |
| t3_noise10 | 300 | 4.0% | 89.3% | 7.0% | 0.7% | 6.7% |
| t3_noise5 | 300 | 6.3% | 86.0% | 9.7% | 3.3% | 5.3% |
| t4_crop2s | 300 | 6.3% | 85.0% | 11.7% | 6.0% | 0.7% |
| t4_crop1s | 300 | 14.0% | 70.3% | 19.0% | 20.0% | 1.3% |
| t5_hidden | 300 | 7.3% | 83.7% | 11.3% | 5.3% | 4.7% |
