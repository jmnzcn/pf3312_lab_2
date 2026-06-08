# Plantilla — secciones con INCLUDE para `merge_informe`

Reemplazar bloques en `docs/informe.md` y ejecutar:

```powershell
python scripts/run_analysis.py
```

## Marcadores

### 3.0 Resumen transversal
<!-- INCLUDE: dimensiones_generadas/resumen_ejecutivo.md -->

### 3.0.1 Matriz maestra
<!-- INCLUDE: dimensiones_generadas/matriz_6_dimensiones.md -->

### 3.0.2 Matrices 5×6 por categoría
<!-- INCLUDE: dimensiones_generadas/matriz_5x6_llm.md -->
<!-- INCLUDE: dimensiones_generadas/matriz_5x6_stt.md -->
<!-- INCLUDE: dimensiones_generadas/matriz_5x6_tts.md -->

### 3.0.3 STT — WER por fuente
<!-- INCLUDE: dimensiones_generadas/stt_wer_por_fuente.md -->

### 3.0.4 LLM — calidad
<!-- INCLUDE: dimensiones_generadas/llm_calidad.md -->

### 3.0.5 TTS — MOS
<!-- INCLUDE: dimensiones_generadas/tts_mos.md -->

### 3.1 LLM
<!-- INCLUDE: tablas_generadas/tabla_llm.md -->

### 3.2 STT
<!-- INCLUDE: tablas_generadas/tabla_stt.md -->

### 3.3 TTS
<!-- INCLUDE: tablas_generadas/tabla_tts.md -->
