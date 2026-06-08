# Resumen comparativo - LLM

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

| provider   | model                   | deployment   |   llamadas |   latencia_ms_prom |   latencia_ms_std |   latencia_ms_p95 |   ttft_ms_prom |   costo_usd_prom | categoria   |
|------------|-------------------------|--------------|------------|--------------------|-------------------|-------------------|----------------|------------------|-------------|
| anthropic  | claude-sonnet-4-6       | cloud        |         25 |            6979.31 |           4672.96 |          14756.4  |        1497.13 |         0.005716 | llm         |
| google     | gemini-2.5-flash        | cloud        |         25 |            5966.03 |           4251.84 |          12148.9  |        4834.07 |         0.000748 | llm         |
| groq       | llama-3.3-70b-versatile | cloud        |         25 |             675.16 |            380.8  |           1399.7  |         230.73 |         0.000218 | llm         |
| ollama     | llama3.2:3b             | local        |         25 |           15400.6  |          12408.9  |          37157    |        1087.1  |         0        | llm         |
| openai     | gpt-4o                  | cloud        |         25 |            1918.41 |           1440.69 |           4816.11 |         601.13 |         0.002081 | llm         |


---

# Resumen comparativo - STT

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

| provider       | model                       | deployment   |   llamadas |   latencia_ms_prom |   latencia_ms_std |   latencia_ms_p95 |   costo_usd_prom |   calidad_prom | categoria   |
|----------------|-----------------------------|--------------|------------|--------------------|-------------------|-------------------|------------------|----------------|-------------|
| assemblyai     | universal-3-pro             | cloud        |         50 |            4135.69 |            834.45 |           6669.46 |         0.000565 |           0.08 | stt         |
| azure          | speech-recognition-standard | cloud        |         50 |            3003.11 |           1666.2  |           5829.81 |         0.002622 |           0.12 | stt         |
| deepgram       | nova-3                      | cloud        |         50 |             307.33 |            182.28 |            691.94 |         0.000675 |           0.09 | stt         |
| faster-whisper | large-v3                    | local        |         50 |           28126.8  |           5684.84 |          37294.8  |         0        |           0.09 | stt         |
| openai         | whisper-1                   | cloud        |         50 |            1970.79 |            715.71 |           3319.25 |         0.000942 |           0.1  | stt         |


---

# Resumen comparativo - TTS

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

| provider   | model                  | deployment   |   llamadas |   latencia_ms_prom |   latencia_ms_std |   latencia_ms_p95 |   costo_usd_prom | categoria   |
|------------|------------------------|--------------|------------|--------------------|-------------------|-------------------|------------------|-------------|
| azure      | es-CR-MariaNeural      | cloud        |         25 |             754.99 |            245.7  |            927.32 |         0.002707 | tts         |
| elevenlabs | eleven_multilingual_v2 | cloud        |         25 |            2094.38 |           1319.89 |           4671.55 |         0.05076  | tts         |
| google     | es-ES-Neural2-A        | cloud        |         25 |             301.38 |            201.68 |            717.94 |         0.002707 | tts         |
| openai     | gpt-4o-mini-tts        | cloud        |         25 |            2557.19 |           1041.41 |           4455.28 |         0.10152  | tts         |
| piper      | es_ES-davefx-medium    | local        |         25 |            1436.26 |            683.72 |           2754.97 |         0        | tts         |
