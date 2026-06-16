# Audios de prueba para STT

Los **14 archivos `.wav` de esta carpeta están versionados en Git** como copia
canónica usada en el benchmark (≈ 7 MB en total). Cualquier clon del repositorio
puede correr STT y E2E sin descargar nada extra.

Cada audio va acompañado de su transcripción exacta en
`data/reference_transcriptions.json` (incluye `sha256` por archivo para verificar
integridad). Los scripts de descarga/generación documentan el origen, pero **no
sustituyen** los bytes del repo si querés reproducir las mismas métricas.

## Catálogo (14 audios)

| Grupo | IDs | Origen | Licencia |
|-------|-----|--------|----------|
| Sintéticos Piper | `a1`, `a2`, `a4`, `a5` | `scripts/generate_stt_audio_piper.py` | Generado localmente |
| FLEURS humano | `g1`, `g2`, `g4` | `scripts/download_common_voice_samples.py` | CC BY 4.0 |
| CV ruidoso | `c1`, `c3` | `scripts/download_common_voice_noisy.py` | CC0 |
| Largos | `l1`, `l2`, `l4` | `scripts/download_long_stt_samples.py` | CC BY 4.0 / sintético |
| CV centroamérica | `r1`, `r2` | `scripts/download_cv_centroamerica_samples.py` | CC0 |

Ver `GUIA_GRABACION.md` para regenerar o ampliar el catálogo.

## Formato

- Codec: WAV 16-bit PCM
- Sample rate: 16 kHz (recomendado) o 44.1 kHz
- Canales: mono
- Duración: clips cortos (~5 s), medios (~11–16 s) y largos (~30–45 s)

## Verificar integridad

```powershell
python scripts/hash_stt_audio.py --verify
```

Tras regenerar un WAV a propósito, actualizá el manifiesto:

```powershell
python scripts/hash_stt_audio.py --write
```

## Si falta algún audio

Los benchmarks detectan archivos faltantes y los saltan con un warning. Podés
correr con los disponibles y completar después sin romper nada.
