# Resumen — 6 dimensiones

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*
## Cobertura de dimensiones en este repo

| Dimensión | Fuente en el proyecto |
|-----------|------------------------|
| 1 Latencia | `results/*_results.csv` (automático) |
| 2 Precisión | WER en STT (automático); LLM/TTS cualitativo |
| 3 Costo | CSV (estimado por rates en cada script) |
| 4 Privacidad | `analysis/dimensions_catalog.py` (1-5, revisar políticas) |
| 5 Customización | catálogo 1-5 |
| 6 Integración | catálogo 1-5 |

## Servicios con datos de benchmark
- **LLM**: 5 filas en matriz; CSV=sí
- **STT**: 5 filas en matriz; CSV=sí
- **TTS**: 5 filas en matriz; CSV=sí

## Mejores por dimensión (solo filas con datos)

- Menor latencia: **tts/google** (301.4 ms)
- Menor WER (STT): **stt/assemblyai** (0.0825)
- Menor costo/llamada: **llm/ollama** ($0.0)
- Mayor Privacidad (catálogo): **llm/ollama** (5/5)
- Mayor Customización (catálogo): **llm/anthropic** (5/5)
- Mayor Integración (catálogo): **llm/anthropic** (5/5)
