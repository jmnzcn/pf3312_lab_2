# Dimensión — Integración

| servicio           |   integracion_1_5 | nota_integracion                                         |
|--------------------|-------------------|----------------------------------------------------------|
| llm/anthropic      |                 5 | SDK Python maduro; streaming de mensajes.                |
| llm/google         |                 4 | SDK google-genai; integración GCP opcional.              |
| llm/groq           |                 4 | API compatible OpenAI-style; muy simple para prototipos. |
| llm/ollama         |                 3 | HTTP local; sin SLA cloud; ideal dev/offline.            |
| llm/openai         |                 5 | SDK oficial Python; streaming SSE; amplia documentación. |
| stt/assemblyai     |                 4 | SDK Python; API REST clara.                              |
| stt/azure          |                 4 | SDK Azure; buen fit .NET/Unity vía REST.                 |
| stt/deepgram       |                 4 | SDK v6, streaming WebSocket fuerte.                      |
| stt/faster-whisper |                 3 | Librería Python; requiere GPU/CPU tuning.                |
| stt/openai         |                 5 | Whisper API simple; mismo ecosistema que GPT.            |
| tts/azure          |                 4 | SDK + SSML; integración Unity vía plugin o REST.         |
| tts/elevenlabs     |                 4 | API REST; SDK; orientado a producto de voz.              |
| tts/google         |                 4 | Cliente google-cloud-texttospeech; GCP setup.            |
| tts/openai         |                 5 | API unificada OpenAI; fácil desde Python.                |
| tts/piper          |                 2 | CLI/subprocess; sin SDK cloud; manual en Unity.          |
