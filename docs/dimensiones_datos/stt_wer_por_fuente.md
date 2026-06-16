# STT: WER por fuente de audio

| provider       | audio_source                 |   wer_prom |   llamadas |
|----------------|------------------------------|------------|------------|
| assemblyai     | common_voice_central_america |     0.1    |         10 |
| assemblyai     | common_voice_noisy           |     0      |         10 |
| assemblyai     | fleurs_human                 |     0.0333 |         15 |
| assemblyai     | fleurs_human_concat          |     0.0103 |          5 |
| assemblyai     | synthetic_noisy_long         |     0.0103 |          5 |
| assemblyai     | synthetic_piper              |     0.0801 |         20 |
| assemblyai     | synthetic_piper_long         |     0.018  |          5 |
| azure          | common_voice_central_america |     0.1    |         10 |
| azure          | common_voice_noisy           |     0      |         10 |
| azure          | fleurs_human                 |     0.0434 |         15 |
| azure          | fleurs_human_concat          |     0.0309 |          5 |
| azure          | synthetic_noisy_long         |     0.0309 |          5 |
| azure          | synthetic_piper              |     0.141  |         20 |
| azure          | synthetic_piper_long         |     0.036  |          5 |
| deepgram       | common_voice_central_america |     0.1    |         10 |
| deepgram       | common_voice_noisy           |     0.05   |         10 |
| deepgram       | fleurs_human                 |     0.0333 |         15 |
| deepgram       | fleurs_human_concat          |     0.0103 |          5 |
| deepgram       | synthetic_noisy_long         |     0.0103 |          5 |
| deepgram       | synthetic_piper              |     0.1165 |         20 |
| deepgram       | synthetic_piper_long         |     0.036  |          5 |
| faster-whisper | common_voice_central_america |     0.1    |         10 |
| faster-whisper | common_voice_noisy           |     0      |         10 |
| faster-whisper | fleurs_human                 |     0.0434 |         15 |
| faster-whisper | fleurs_human_concat          |     0.0206 |          5 |
| faster-whisper | synthetic_noisy_long         |     0.0206 |          5 |
| faster-whisper | synthetic_piper              |     0.0795 |         20 |
| faster-whisper | synthetic_piper_long         |     0.009  |          5 |
| openai         | common_voice_central_america |     0.1    |         10 |
| openai         | common_voice_noisy           |     0      |         10 |
| openai         | fleurs_human                 |     0.0535 |         15 |
| openai         | fleurs_human_concat          |     0.0309 |          5 |
| openai         | synthetic_noisy_long         |     0.0309 |          5 |
| openai         | synthetic_piper              |     0.1213 |         20 |
| openai         | synthetic_piper_long         |     0.009  |          5 |

![WER por fuente de audio (STT)](graficos_generados/stt_wer_por_fuente.png)

*Figura: WER promedio por proveedor y tipo de audio (Piper sintético vs FLEURS humano vs Common Voice). Barras más bajas = mejor transcripción.*

