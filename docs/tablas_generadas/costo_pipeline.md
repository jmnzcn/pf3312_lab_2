# Costo estimado por turno conversacional (STT + LLM + TTS)

*Promedio de costo/latencia por llamada en la última corrida filtrada.*

| escenario          | llm    | stt            | tts        |   costo_usd_turno |   latencia_ms_turno |
|--------------------|--------|----------------|------------|-------------------|---------------------|
| Demo rápida nube   | groq   | deepgram       | google     |          0.0036   |              1283.9 |
| Calidad premium    | openai | assemblyai     | elevenlabs |          0.053406 |              8148.5 |
| Privacidad offline | ollama | faster-whisper | piper      |          0        |             44963.6 |
| Stack Azure        | openai | azure          | azure      |          0.00741  |              5676.5 |
