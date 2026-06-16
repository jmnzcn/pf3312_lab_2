# Dimensión 1: Latencia empírica

| servicio           |   latencia_ms |   ttft_ms | categoria   |
|--------------------|---------------|-----------|-------------|
| llm/anthropic      |       6916.00 |   1346.40 | llm         |
| llm/google         |       5928.30 |   4832.60 | llm         |
| llm/groq           |        695.20 |    227.00 | llm         |
| llm/ollama         |      36642.50 |   1740.70 | llm         |
| llm/openai         |       1780.90 |    584.00 | llm         |
| stt/assemblyai     |       4218.10 |    nan    | stt         |
| stt/azure          |       6891.90 |    nan    | stt         |
| stt/deepgram       |        428.50 |    nan    | stt         |
| stt/faster-whisper |      37481.80 |    nan    | stt         |
| stt/openai         |       2127.10 |    nan    | stt         |
| tts/azure          |        848.90 |    nan    | tts         |
| tts/elevenlabs     |       2147.50 |    nan    | tts         |
| tts/google         |        300.10 |    nan    | tts         |
| tts/openai         |       3368.60 |    nan    | tts         |
| tts/piper          |       3025.80 |    nan    | tts         |

*TTFT solo aplica a LLM con streaming.*



---

# Dimensión 2: Precisión y calidad

| servicio           | categoria   |      wer | precision_resumen            |
|--------------------|-------------|----------|------------------------------|
| llm/anthropic      | llm         | nan      | Coherencia (revisión manual) |
| llm/google         | llm         | nan      | Coherencia (revisión manual) |
| llm/groq           | llm         | nan      | Coherencia (revisión manual) |
| llm/ollama         | llm         | nan      | Coherencia (revisión manual) |
| llm/openai         | llm         | nan      | Coherencia (revisión manual) |
| stt/assemblyai     | stt         |   0.0471 | WER=0.0471                   |
| stt/azure          | stt         |   0.0709 | WER=0.0709                   |
| stt/deepgram       | stt         |   0.0659 | WER=0.0659                   |
| stt/faster-whisper | stt         |   0.0499 | WER=0.0499                   |
| stt/openai         | stt         |   0.0655 | WER=0.0655                   |
| tts/azure          | tts         | nan      | MOS 1-5 (escucha manual)     |
| tts/elevenlabs     | tts         | nan      | MOS 1-5 (escucha manual)     |
| tts/google         | tts         | nan      | MOS 1-5 (escucha manual)     |
| tts/openai         | tts         | nan      | MOS 1-5 (escucha manual)     |
| tts/piper          | tts         | nan      | MOS 1-5 (escucha manual)     |


---

# Dimensión 3: Costo (USD por llamada, estimado)

| servicio           |   costo_usd | categoria   |
|--------------------|-------------|-------------|
| llm/anthropic      |    0.005728 | llm         |
| llm/google         |    0.000779 | llm         |
| llm/groq           |    0.000226 | llm         |
| llm/ollama         |    0        | llm         |
| llm/openai         |    0.001979 | llm         |
| stt/assemblyai     |    0.001064 | stt         |
| stt/azure          |    0.004938 | stt         |
| stt/deepgram       |    0.001271 | stt         |
| stt/faster-whisper |    0        | stt         |
| stt/openai         |    0.001774 | stt         |
| tts/azure          |    0.00273  | tts         |
| tts/elevenlabs     |    0.05118  | tts         |
| tts/google         |    0.00273  | tts         |
| tts/openai         |    0.10236  | tts         |
| tts/piper          |    0        | tts         |


---

# Dimensión: Privacidad y gobernanza

| servicio           |   privacidad_1_5 |
|--------------------|------------------|
| llm/anthropic      |                4 |
| llm/google         |                3 |
| llm/groq           |                4 |
| llm/ollama         |                5 |
| llm/openai         |                3 |
| stt/assemblyai     |                3 |
| stt/azure          |                3 |
| stt/deepgram       |                3 |
| stt/faster-whisper |                5 |
| stt/openai         |                3 |
| tts/azure          |                3 |
| tts/elevenlabs     |                3 |
| tts/google         |                3 |
| tts/openai         |                3 |
| tts/piper          |                5 |


---

# Dimensión: Customización

| servicio           |   customizacion_1_5 |
|--------------------|---------------------|
| llm/anthropic      |                   5 |
| llm/google         |                   4 |
| llm/groq           |                   3 |
| llm/ollama         |                   4 |
| llm/openai         |                   5 |
| stt/assemblyai     |                   4 |
| stt/azure          |                   4 |
| stt/deepgram       |                   4 |
| stt/faster-whisper |                   3 |
| stt/openai         |                   3 |
| tts/azure          |                   4 |
| tts/elevenlabs     |                   5 |
| tts/google         |                   4 |
| tts/openai         |                   4 |
| tts/piper          |                   2 |


---

# Dimensión: Integración

| servicio           |   integracion_1_5 |
|--------------------|-------------------|
| llm/anthropic      |                 5 |
| llm/google         |                 4 |
| llm/groq           |                 4 |
| llm/ollama         |                 3 |
| llm/openai         |                 5 |
| stt/assemblyai     |                 4 |
| stt/azure          |                 4 |
| stt/deepgram       |                 4 |
| stt/faster-whisper |                 3 |
| stt/openai         |                 5 |
| tts/azure          |                 4 |
| tts/elevenlabs     |                 4 |
| tts/google         |                 4 |
| tts/openai         |                 5 |
| tts/piper          |                 2 |


---

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

