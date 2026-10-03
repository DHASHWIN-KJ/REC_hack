# Audio deepfake detector: capability report


## t1_baseline

300 files (150 real / 150 fake). EER **1.3%**, correct 93.0%, uncertain 6.3%, false alarms 0.7%, misses 0.7%.


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

300 files (150 real / 150 fake). EER **3.0%**, correct 88.3%, uncertain 8.3%, false alarms 6.0%, misses 0.7%.


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

300 files (150 real / 150 fake). EER **2.3%**, correct 87.7%, uncertain 9.7%, false alarms 4.7%, misses 0.7%.


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

300 files (150 real / 150 fake). EER **2.0%**, correct 91.0%, uncertain 7.3%, false alarms 0.7%, misses 2.7%.


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

300 files (150 real / 150 fake). EER **4.0%**, correct 87.7%, uncertain 9.7%, false alarms 2.7%, misses 2.7%.


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

300 files (150 real / 150 fake). EER **6.3%**, correct 81.7%, uncertain 15.7%, false alarms 5.3%, misses 0.0%.


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

300 files (150 real / 150 fake). EER **6.3%**, correct 78.7%, uncertain 12.7%, false alarms 16.7%, misses 0.7%.


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

300 files (150 real / 150 fake). EER **14.0%**, correct 0.0%, uncertain 100.0%, false alarms 0.0%, misses 0.0%.


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

300 files (150 real / 150 fake). EER **7.3%**, correct 38.0%, uncertain 59.0%, false alarms 5.3%, misses 0.7%.


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


## t6_inthewild

300 files (150 real / 150 fake). EER **5.3%**, correct 81.3%, uncertain 14.7%, false alarms 6.0%, misses 2.0%.


**By clip duration**

| Group | Files | EER |
|---|---|---|
| a) under 2 s | 68 | 6.4% |
| b) 2-4 s | 101 | 5.8% |
| c) 4-8 s | 89 | 0.9% |
| d) over 8 s | 42 | 7.1% |


**By audio condition**

| Group | Files | EER |
|---|---|---|
| normal | 190 | 2.2% |
| trimmed | 110 | 8.3% |


## Summary

| Test | Files | EER | Correct | Uncertain | False alarms | Misses |
|---|---|---|---|---|---|---|
| t1_baseline | 300 | 1.3% | 93.0% | 6.3% | 0.7% | 0.7% |
| t2_whatsapp | 300 | 3.0% | 88.3% | 8.3% | 6.0% | 0.7% |
| t2_mp3_low | 300 | 2.3% | 87.7% | 9.7% | 4.7% | 0.7% |
| t3_noise20 | 300 | 2.0% | 91.0% | 7.3% | 0.7% | 2.7% |
| t3_noise10 | 300 | 4.0% | 87.7% | 9.7% | 2.7% | 2.7% |
| t3_noise5 | 300 | 6.3% | 81.7% | 15.7% | 5.3% | 0.0% |
| t4_crop2s | 300 | 6.3% | 78.7% | 12.7% | 16.7% | 0.7% |
| t4_crop1s | 300 | 14.0% | 0.0% | 100.0% | 0.0% | 0.0% |
| t5_hidden | 300 | 7.3% | 38.0% | 59.0% | 5.3% | 0.7% |
| t6_inthewild | 300 | 5.3% | 81.3% | 14.7% | 6.0% | 2.0% |
