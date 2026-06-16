# Benchmarking de Servicios Cognitivos · PF-3312, Proyecto 2

**Autor:** Ney Fred Jiménez Campos (B03230)  
**Curso:** PF-3312 Laboratorio de Agentes Virtuales Inteligentes  
**Profesor:** Dr. Alexander Barquero  
**UCR · Posgrado en Computación e Informática · I Ciclo 2026**  
**Repositorio:** https://github.com/jmnzcn/pf3312_lab_2

Benchmark de quince servicios de voz (STT, LLM y TTS) para un agente conversacional.
Cada proveedor se midió en las seis dimensiones del enunciado: latencia, precisión, costo,
privacidad, customización e integración.

En nube hay desde opciones premium hasta las más baratas; en local corrí Ollama,
faster-whisper y Piper para comparar un despliegue sin APIs. El repositorio trae los CSV
de la corrida, las tablas derivadas y los audios de prueba, de modo que se puede revisar
todo sin volver a gastar créditos, o repetir la medición con el mismo código.

## Los quince servicios

LLM: OpenAI GPT-4o, Anthropic Claude Sonnet 4.6, Google Gemini Flash, Groq Llama 3.3 70B,
Ollama con Llama 3.2 3B.

STT: Deepgram Nova-3, OpenAI Whisper, Azure Speech, AssemblyAI Universal, faster-whisper
large-v3.

TTS: ElevenLabs, OpenAI gpt-4o-mini-tts, Azure Neural (`es-CR`), Google Neural2, Piper
(`es_ES-davefx-medium`).

Protocolo: cinco ejecuciones por input (cinco prompts en LLM, cinco textos en TTS, catorce
audios en STT). Además medí el flujo completo STT → LLM → TTS en cuatro stacks, con cinco
audios por escenario (`results/e2e_results.csv`).

## Qué trae el repositorio

Código en `benchmarks/` (`llm`, `stt`, `tts`, `pipeline`) y entrada única en `run_all.py`.
Prompts, textos TTS y catálogo STT en `common/` y `data/reference_transcriptions.json`.

Los catorce WAV (~7 MB) están en `data/test_audio/` con SHA-256 en el JSON de referencia
(`python scripts/hash_stt_audio.py --verify`). Puntuaciones cualitativas en
`data/llm_quality_notes.json` y `data/tts_mos_scores.json`.

Resultados: `results/llm_results.csv`, `stt_results.csv`, `tts_results.csv`,
`e2e_results.csv`, `run_manifest.json`, más `hardware_snapshot.json` y
`network_speedtest.json`.

Tras correr `python scripts/run_analysis.py` se actualizan `docs/dimensiones_datos/`
(matrices, WER por fuente, calidad LLM, MOS, apéndice de inputs) y
`docs/graficos_generados/` (latencias, costos, heatmaps, diagrama del pipeline, gráfico
E2E). El UML está en `docs/pipeline.puml`.

Hay un boceto C# para Unity en `examples/UnityPipelineClient.cs` y pruebas en `tests/`.

No van en Git (nunca hagas `git add` de esto):

- `.env` y cualquier copia con keys (`secrets/`, JSON de cuenta GCP en `GOOGLE_APPLICATION_CREDENTIALS`)
- Solo se sube `.env.example`, vacío, como plantilla
- `models/`, binario Piper (`tools/piper/`), `results/raw/`, `results/tts_outputs/`

Antes de `git push`, revisá con `git status` que no aparezca `.env` ni archivos en `secrets/`.
`python scripts/bootstrap.py` también avisa si `.env` quedó trackeado por error.

## Requisitos

Python 3.11+ (lo desarrollé en 3.13), Git, FFmpeg y un `.env` copiado de `.env.example`.
Para los tres proveedores locales hace falta Ollama (`llama3.2:3b`), GPU recomendable para
faster-whisper y Piper configurado con las variables `PIPER_*` del ejemplo.

Sin API key de un proveedor cloud, ese script se omite y el resto continúa.

## Cómo correrlo

```powershell
git clone https://github.com/jmnzcn/pf3312_lab_2.git
cd pf3312_lab_2

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# completar keys

python scripts/bootstrap.py
```

Solo revisar tablas y gráficos a partir de los CSV ya incluidos:

```powershell
python scripts/run_analysis.py
```

Corrida completa (gasta APIs y tarda bastante en local):

```powershell
python -m run_all 5
python scripts/validate_results.py
python scripts/dedupe_results.py      # si re-corriste inputs sin reset_results
python scripts/run_analysis.py
```

Otras combinaciones que usé:

```powershell
python -m run_all 5 --skip-e2e
python -m benchmarks.pipeline.run_e2e 5
python scripts/reset_results.py
python scripts/run_analysis.py --with-optional
python scripts/smoke_analysis.py
python -m pytest tests/ -q
```

El flag `--with-optional` recalcula MOS de inteligibilidad TTS con Whisper en CPU; tarda
porque pasa por muchos audios sintetizados.

Para regenerar audios desde cero: `data/test_audio/README.md`.

## Criterios por dimensión

Latencia: tiempo por llamada; en LLM también mido TTFT con streaming.

Precisión: WER en STT (`jiwer`); en LLM revisé respuestas a mano y el JSON del prompt p3;
en TTS MOS por inteligibilidad (round-trip) y naturalidad por escucha.

Costo: USD por llamada con tarifas en `common/rates.py`; consumo de RAM/VRAM documentado
en `docs/dimensiones_datos/recursos_locales.md`.

Privacidad, customización e integración: escala 1–5 en `analysis/dimensions_catalog.py`.

Textos exactos de prompts y audios: `docs/dimensiones_datos/appendix_inputs.md`.

## Carpetas (vista rápida)

```text
run_all.py
benchmarks/
common/
analysis/
data/
results/
docs/dimensiones_datos/
docs/graficos_generados/
docs/pipeline.puml
examples/
scripts/
tests/
```

## Entrega del curso

PDF en Mediación Virtual y el código en [github.com/jmnzcn/pf3312_lab_2](https://github.com/jmnzcn/pf3312_lab_2)
con CSV, audios, `docs/dimensiones_datos/` y `docs/graficos_generados/`.

Material académico UCR. Los servicios son de sus proveedores; FLEURS, Common Voice y el
resto de datasets citados llevan su propia licencia.

## Nota de uso de herramientas de IA

Durante la elaboración de este documento se utilizaron herramientas de inteligencia
artificial generativa, específicamente ChatGPT (OpenAI) y Claude (Anthropic), como apoyo
en tareas de organización de ideas, revisión de redacción y reformulación de párrafos.
Todo el contenido, los argumentos, las decisiones de diseño y la selección de fuentes
son de autoría propia. Las herramientas se usaron como asistentes de escritura, no como
generadores de contenido académico.
