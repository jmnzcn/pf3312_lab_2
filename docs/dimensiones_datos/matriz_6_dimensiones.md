# Matriz maestra: 6 dimensiones × servicios

*Los 15 servicios en las seis dimensiones del enunciado. WER solo en STT; TTFT solo en LLM; Priv./Cust./Integr. van de 1 a 5. Gráficos en `docs/graficos_generados/`.*

| Servicio           |   Lat. (ms) |      TTFT |      WER |    USD |   Priv. |   Cust. |   Integr. | Precisión                |
|--------------------|-------------|-----------|----------|--------|---------|---------|-----------|--------------------------|
| llm/anthropic      |   6916.0000 | 1346.4000 | nan      | 0.0057 |       4 |       5 |         5 | Coherencia (cual.)       |
| llm/google         |   5928.3000 | 4832.6000 | nan      | 0.0008 |       3 |       4 |         4 | Coherencia (cual.)       |
| llm/groq           |    695.2000 |  227.0000 | nan      | 0.0002 |       4 |       3 |         4 | Coherencia (cual.)       |
| llm/ollama         |  36642.5000 | 1740.7000 | nan      | 0.0000 |       5 |       4 |         3 | Coherencia (cual.)       |
| llm/openai         |   1780.9000 |  584.0000 | nan      | 0.0020 |       3 |       5 |         5 | Coherencia (cual.)       |
| stt/assemblyai     |   4218.1000 |  nan      |   0.0471 | 0.0011 |       3 |       4 |         4 | WER=0.0471               |
| stt/azure          |   6891.9000 |  nan      |   0.0709 | 0.0049 |       3 |       4 |         4 | WER=0.0709               |
| stt/deepgram       |    428.5000 |  nan      |   0.0659 | 0.0013 |       3 |       4 |         4 | WER=0.0659               |
| stt/faster-whisper |  37481.8000 |  nan      |   0.0499 | 0.0000 |       5 |       3 |         3 | WER=0.0499               |
| stt/openai         |   2127.1000 |  nan      |   0.0655 | 0.0018 |       3 |       3 |         5 | WER=0.0655               |
| tts/azure          |    848.9000 |  nan      | nan      | 0.0027 |       3 |       4 |         4 | MOS 1-5 (escucha manual) |
| tts/elevenlabs     |   2147.5000 |  nan      | nan      | 0.0512 |       3 |       5 |         4 | MOS 1-5 (escucha manual) |
| tts/google         |    300.1000 |  nan      | nan      | 0.0027 |       3 |       4 |         4 | MOS 1-5 (escucha manual) |
| tts/openai         |   3368.6000 |  nan      | nan      | 0.1024 |       3 |       4 |         5 | MOS 1-5 (escucha manual) |
| tts/piper          |   3025.8000 |  nan      | nan      | 0.0000 |       5 |       2 |         2 | MOS 1-5 (escucha manual) |

