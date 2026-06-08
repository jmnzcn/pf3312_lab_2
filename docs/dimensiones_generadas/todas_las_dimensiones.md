# Matriz maestra — 6 dimensiones × servicios

| servicio           |   latencia_ms |   ttft_ms |      wer |   costo_usd |   privacidad_1_5 |   customizacion_1_5 |   integracion_1_5 | precision_resumen                   |
|--------------------|---------------|-----------|----------|-------------|------------------|---------------------|-------------------|-------------------------------------|
| llm/anthropic      |     6979.3000 | 1497.1000 | nan      |      0.0057 |                4 |                   5 |                 5 | Coherencia (cualitativo en informe) |
| llm/google         |     5966.0000 | 4834.1000 | nan      |      0.0007 |                3 |                   4 |                 4 | Coherencia (cualitativo en informe) |
| llm/groq           |      675.2000 |  230.7000 | nan      |      0.0002 |                4 |                   3 |                 4 | Coherencia (cualitativo en informe) |
| llm/ollama         |    15400.6000 | 1087.1000 | nan      |      0.0000 |                5 |                   4 |                 3 | Coherencia (cualitativo en informe) |
| llm/openai         |     1918.4000 |  601.1000 | nan      |      0.0021 |                3 |                   5 |                 5 | Coherencia (cualitativo en informe) |
| stt/assemblyai     |     4135.7000 |  nan      |   0.0825 |      0.0006 |                3 |                   4 |                 4 | WER=0.0825                          |
| stt/azure          |     3003.1000 |  nan      |   0.1190 |      0.0026 |                3 |                   4 |                 4 | WER=0.119                           |
| stt/deepgram       |      307.3000 |  nan      |   0.0926 |      0.0007 |                3 |                   4 |                 4 | WER=0.0926                          |
| stt/faster-whisper |    28126.8000 |  nan      |   0.0861 |      0.0000 |                5 |                   3 |                 3 | WER=0.0861                          |
| stt/openai         |     1970.8000 |  nan      |   0.1013 |      0.0009 |                3 |                   3 |                 5 | WER=0.1013                          |
| tts/azure          |      755.0000 |  nan      | nan      |      0.0027 |                3 |                   4 |                 4 | MOS 1-5 (escucha tts_outputs/)      |
| tts/elevenlabs     |     2094.4000 |  nan      | nan      |      0.0508 |                3 |                   5 |                 4 | MOS 1-5 (escucha tts_outputs/)      |
| tts/google         |      301.4000 |  nan      | nan      |      0.0027 |                3 |                   4 |                 4 | MOS 1-5 (escucha tts_outputs/)      |
| tts/openai         |     2557.2000 |  nan      | nan      |      0.1015 |                3 |                   4 |                 5 | MOS 1-5 (escucha tts_outputs/)      |
| tts/piper          |     1436.3000 |  nan      | nan      |      0.0000 |                5 |                   2 |                 2 | MOS 1-5 (escucha tts_outputs/)      |
