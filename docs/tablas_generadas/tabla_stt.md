# Resumen comparativo - STT

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

| provider       | model                       | deployment   |   llamadas |   latencia_ms_prom |   latencia_ms_std |   latencia_ms_p95 |   costo_usd_prom |   calidad_prom | categoria   |
|----------------|-----------------------------|--------------|------------|--------------------|-------------------|-------------------|------------------|----------------|-------------|
| assemblyai     | universal-3-pro             | cloud        |         50 |            4135.69 |            834.45 |           6669.46 |         0.000565 |           0.08 | stt         |
| azure          | speech-recognition-standard | cloud        |         50 |            3003.11 |           1666.2  |           5829.81 |         0.002622 |           0.12 | stt         |
| deepgram       | nova-3                      | cloud        |         50 |             307.33 |            182.28 |            691.94 |         0.000675 |           0.09 | stt         |
| faster-whisper | large-v3                    | local        |         50 |           28126.8  |           5684.84 |          37294.8  |         0        |           0.09 | stt         |
| openai         | whisper-1                   | cloud        |         50 |            1970.79 |            715.71 |           3319.25 |         0.000942 |           0.1  | stt         |
