# Benchmarking de Servicios Cognitivos para Agentes Virtuales (PF-3312, Proyecto 2)

Banco de pruebas reproducible que evalúa **quince servicios cognitivos** —cinco
LLM, cinco STT y cinco TTS— bajo las seis dimensiones definidas en el enunciado
del Proyecto 2 del curso PF-3312: latencia empírica, precisión y calidad, costo y
escalabilidad, privacidad y gobernanza, customización, y facilidad de integración.

**Autor:** Ney Fred Jiménez Campos · Carné B03230
**Curso:** PF-3312 Laboratorio de Agentes Virtuales Inteligentes · UCR, I Ciclo 2026

## Servicios evaluados

| Categoría | Cloud (alta gama) | Cloud (bajo costo / rápido) | Local / offline |
|-----------|-------------------|-----------------------------|-----------------|
| LLM       | OpenAI GPT-4o, Anthropic Claude Sonnet 4.6 | Google Gemini Flash, Groq Llama 3.3 70B | Ollama + Llama 3.2 3B |
| STT       | Deepgram Nova-3, OpenAI Whisper, Azure Speech | AssemblyAI Best | faster-whisper large-v3 (int8_float16) |
| TTS       | ElevenLabs Multilingual v2, OpenAI gpt-4o-mini-tts | Azure Neural TTS, Google Cloud Neural2 | Piper TTS (es_ES-davefx-medium) |

Cada servicio se ejecuta **5 veces por input estandarizado** y persiste sus
métricas en `results/*.csv` para luego generar tablas y gráficos comparativos.

## Requisitos previos

- **Python 3.11+** (probado en 3.13).
- **Git**.
- **FFmpeg** en PATH (lo necesita `faster-whisper`/`soundfile` para algunos
  formatos de audio).
- Para los modelos locales:
  - **Ollama** instalado y corriendo (`https://ollama.com/download`). Hacer
    `ollama pull llama3.2:3b` antes del primer run.
  - **CUDA** opcional pero recomendado para `faster-whisper` (4 GB VRAM bastan
    con `int8_float16`).
  - **Piper TTS** binario y modelo en español (instrucciones detalladas en el
    header de `benchmarks/tts/benchmark_piper_local.py`).

## Setup paso a paso

```powershell
# 1. Clonar el repo
git clone <URL_DEL_REPO>
cd lab_entregable_2

# 2. Crear y activar un entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate    # Linux / macOS

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env         # Windows
# cp .env.example .env         # Linux / macOS
# Editar .env y rellenar las API keys que tengás
```

Los servicios cuyas keys no estén configuradas se **saltan automáticamente**
con un warning. Esto significa que podés empezar el benchmark con dos o tres
proveedores y completar el resto a medida que vayás obteniendo las keys.

## Audios STT (sintéticos + voz humana)

```powershell
# Sintéticos controlados (Piper) — ya en data/test_audio/a1..a5 si los generaste
python scripts/generate_stt_audio_piper.py

# Voz humana sin grabar (Google FLEURS es_419) — 5 clips + actualiza el catálogo
pip install datasets
python scripts/download_common_voice_samples.py
```

## Cómo correr los benchmarks

### Todo de una

```powershell
python -m run_all 5            # 5 = runs por input (default)
```

### Por categoría

```powershell
python -m benchmarks.llm.run_all 5
python -m benchmarks.stt.run_all 5
python -m benchmarks.tts.run_all 5
```

### Un solo proveedor (útil para depurar)

```powershell
python -m benchmarks.llm.benchmark_openai
python -m benchmarks.stt.benchmark_deepgram
python -m benchmarks.tts.benchmark_elevenlabs
```

## Generar tablas, gráficos e informe

```powershell
# Pipeline completo (tablas + gráficos + 6 dimensiones + calidad LLM + informe.md)
python scripts/run_analysis.py

# O paso a paso:
python -m analysis.generate_tables
python -m analysis.generate_charts
python -m analysis.generate_six_dimensions
python -m analysis.evaluate_llm_quality
python -m analysis.merge_informe
```

### Corrida limpia (recomendado antes del PDF)

```powershell
python scripts/reset_results.py   # archiva CSV viejos + nuevo run_batch_id
python -m run_all 5
python scripts/run_analysis.py
```

### Tests

```powershell
pip install pytest
pytest tests/ -q
```

### Evaluación cualitativa y PDF

- `data/tts_mos_scores.json` — MOS TTS (inteligibilidad WER + naturalidad)
- `data/llm_quality_notes.json` — coherencia/instrucciones LLM
- `python scripts/score_tts_inteligibilidad.py` — recalcular MOS inteligibilidad
- `python scripts/export_pdf.py` — PDF con Pandoc (si está instalado)

### Publicar en GitHub

```powershell
git init
git add .
git commit -m "PF-3312 Proyecto 2: benchmarking 15 servicios"
git remote add origin https://github.com/TU_USUARIO/lab_entregable_2.git
git push -u origin main
```

**No subir:** `.env`, `secrets/`, `models/`, audios grandes en `data/test_audio/`.

## Estructura del proyecto

```text
lab_entregable_2/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run_all.py                    # corre las 3 categorías en secuencia
├── common/
│   ├── base.py, cli.py, runner.py, run_context.py, piper_config.py, pricing.py
│   ├── metrics.py, prompts.py, audio_samples.py, results.py
├── scripts/
│   ├── run_analysis.py, reset_results.py, capture_hardware.py
│   ├── score_tts_inteligibilidad.py, export_pdf.py, render_pipeline.py
│   ├── generate_stt_audio_piper.py, download_common_voice_samples.py
├── benchmarks/
│   ├── llm/                      # 5 scripts + run_all.py
│   ├── stt/                      # 5 scripts + run_all.py
│   └── tts/                      # 5 scripts + run_all.py
├── data/
│   ├── test_audio/               # audios .wav (no versionados)
│   └── reference_transcriptions.json
├── results/                      # CSV + JSON con métricas crudas
│   ├── llm_results.csv
│   ├── stt_results.csv
│   ├── tts_results.csv
│   ├── raw/                      # dump JSON por proveedor
│   └── tts_outputs/              # MP3 generados por los benchmarks TTS
├── analysis/
│   ├── generate_tables.py, generate_charts.py, generate_six_dimensions.py
│   ├── generate_pipeline_cost.py, generate_local_resources.py
│   ├── evaluate_llm_quality.py, merge_informe.py, dimensions_catalog.py
├── .github/workflows/test.yml    # CI pytest
└── docs/
    ├── informe.md, pipeline.puml, informe_template.md
    ├── tablas_generadas/, graficos_generados/, dimensiones_generadas/
```

## Cómo extender (agregar un nuevo proveedor)

Cada benchmark sigue el mismo patrón. Por ejemplo, para agregar Cohere LLM:

1. Crear `benchmarks/llm/benchmark_cohere.py`.
2. Heredar de `Benchmark` y definir `category`, `provider`, `model`, `deployment`.
3. Implementar `run_single(test_input, run_id) -> BenchmarkResult` midiendo
   con `time.perf_counter()` o `stopwatch()` de `common/metrics`.
4. Agregar el script al `run_all.py` de la categoría.

El método `run` de la clase base se encarga de iterar inputs × runs y de
capturar errores en el propio `BenchmarkResult` sin romper el batch.

## Notas sobre Privacidad y Gobernanza (Dimensión 4)

Esta dimensión es cualitativa y se documenta a mano en `docs/informe.md`.
Resumen recomendado a verificar al momento del análisis:

- **OpenAI**: opt-out de entrenamiento en cuentas API por default; ZDR
  disponible en planes Enterprise.
- **Anthropic**: no entrena con datos de API por default.
- **Google Gemini**: free tier puede usar prompts para entrenar; pay-tier
  no.
- **Groq**: no entrena con prompts.
- **Ollama / faster-whisper / Piper**: 100% offline, control total.
- **Azure Speech**: opt-in para "Improvements"; default no almacena.
- **Deepgram / AssemblyAI / ElevenLabs / Google TTS**: revisar términos
  vigentes; políticas suelen ser pay-tier sin retención.

## Entregables del proyecto

1. **Reporte PDF** (`docs/informe.md` exportado a PDF) con introducción,
   metodología, análisis comparativo por categoría, diagrama UML del pipeline
   y recomendaciones.
2. **Repositorio GitHub** con este código, los `requirements.txt`,
   `.env.example` y datos de prueba reproducibles.

## Licencia

Material académico (UCR, I Ciclo 2026). Los servicios evaluados pertenecen
a sus respectivos proveedores; los créditos y términos de uso se documentan
en el reporte.
