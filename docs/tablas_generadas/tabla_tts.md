# Resumen comparativo - TTS

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

| provider   | model                  | deployment   |   llamadas |   latencia_ms_prom |   latencia_ms_std |   latencia_ms_p95 |   costo_usd_prom | categoria   |
|------------|------------------------|--------------|------------|--------------------|-------------------|-------------------|------------------|-------------|
| azure      | es-CR-MariaNeural      | cloud        |         25 |             754.99 |            245.7  |            927.32 |         0.002707 | tts         |
| elevenlabs | eleven_multilingual_v2 | cloud        |         25 |            2094.38 |           1319.89 |           4671.55 |         0.05076  | tts         |
| google     | es-ES-Neural2-A        | cloud        |         25 |             301.38 |            201.68 |            717.94 |         0.002707 | tts         |
| openai     | gpt-4o-mini-tts        | cloud        |         25 |            2557.19 |           1041.41 |           4455.28 |         0.10152  | tts         |
| piper      | es_ES-davefx-medium    | local        |         25 |            1436.26 |            683.72 |           2754.97 |         0        | tts         |
