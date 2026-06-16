# Guía: audios de voz humana

Los **14 `.wav` del benchmark ya están en el repositorio** (`data/test_audio/`).
Los comandos siguientes sirven para **regenerar** clips equivalentes o ampliar el
catálogo; si cambiás un archivo, ejecutá `python scripts/hash_stt_audio.py --write`.

**Recomendado (sin grabar):**

```powershell
python scripts/download_common_voice_samples.py
```

Eso descarga `g1_fleurs.wav`, `g2_fleurs.wav` y `g4_fleurs.wav` desde Google FLEURS (`es_419`).

**Common Voice con ruido / validación débil (robustez):**

```powershell
python scripts/download_common_voice_noisy.py
```

Descarga `c1_cv_noisy.wav` y `c3_cv_noisy.wav` desde Common Voice 23.0 (es, espejo HF).
Filtra por **SNR estimado bajo** (ruido de fondo audible), no solo votos negativos.
Corpus oficial completo: [Mozilla Data Collective](https://datacollective.mozillafoundation.org/) (registro).

**Audios largos (30–45 s)** — turnos que no existen como frase única en CV/FLEURS:

```powershell
python scripts/download_long_stt_samples.py
```

Genera `l1_fleurs_largo` (concatena g2+g4; el clip actual en disco puede ser legacy
g2+g4+g3), `l2_piper_largo` (~44 s) y `l4_noisy_largo` (ruido rosa sobre l1).
Opcional: `l3_cv_largo` si el scan encuentra un clip CV limpio ≥18 s (poco frecuente).

**Acento centroamericano (proxy CR)** — Common Voice no etiqueta «Costa Rica» de forma
aislada; usa el bucket **América central**:

```powershell
python scripts/download_cv_centroamerica_samples.py
```

Genera `r1_cv_centroamerica.wav` (~11 s) y `r2_cv_centroamerica_largo.wav` (~32 s).

**Alternativa manual:** grabá los archivos con el texto exacto de
`reference_transcriptions.json` (`source: human_recorded`).

## Catálogo activo (14 audios)

| Prefijo | Cantidad | Origen |
|---------|----------|--------|
| `a*` | 4 | Piper sintético (`generate_stt_audio_piper.py`) |
| `g*` | 3 | FLEURS voz humana (g1, g2, g4) |
| `c*` | 2 | CV ruidoso (c1, c3) |
| `l*` | 3 | Largos (l1, l2, l4; l3 opcional) |
| `r*` | 2 | CV América central |

## Formato

- WAV, mono, 16 kHz, 16-bit (Audacity: Proyecto → 16000 Hz → mono → exportar WAV)
- Ambiente silencioso, micrófono estable
- Leé natural, como si hablaras con el agente (interacción), sin corregirte en voz alta

## Después de generar o grabar

```powershell
python -m benchmarks.stt.run_all 5
```

Los benchmarks usan todos los `.wav` declarados en `reference_transcriptions.json` que
existan en esta carpeta.
