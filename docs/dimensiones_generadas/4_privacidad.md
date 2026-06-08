# Dimensión — Privacidad y gobernanza

| servicio           |   privacidad_1_5 | nota_privacidad                                                            |
|--------------------|------------------|----------------------------------------------------------------------------|
| llm/anthropic      |                4 | Política API: no entrena con prompts por defecto.                          |
| llm/google         |                3 | Gemini API pay-tier distinto del free; revisar retención en consola.       |
| llm/groq           |                4 | Inferencia acelerada; política de no entrenamiento en API.                 |
| llm/ollama         |                5 | 100 % local; datos no salen del equipo.                                    |
| llm/openai         |                3 | API: datos no usados para entrenar por defecto; retención limitada. Cloud. |
| stt/assemblyai     |                3 | Cloud; políticas según plan.                                               |
| stt/azure          |                3 | Azure Cognitive Services; datos en región elegida.                         |
| stt/deepgram       |                3 | Cloud; opciones enterprise para retención cero.                            |
| stt/faster-whisper |                5 | Offline local; sin envío a terceros.                                       |
| stt/openai         |                3 | Audio enviado a cloud OpenAI; política API estándar.                       |
| tts/azure          |                3 | Región Azure; cumplimiento enterprise.                                     |
| tts/elevenlabs     |                3 | Cloud; clonación de voz implica datos biométricos de voz.                  |
| tts/google         |                3 | GCP; cuenta de servicio; datos en proyecto Google.                         |
| tts/openai         |                3 | Cloud OpenAI; mismas consideraciones que LLM API.                          |
| tts/piper          |                5 | Offline; sin telemetría de contenido.                                      |
