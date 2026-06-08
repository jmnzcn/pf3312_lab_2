# Guía: 5 audios de voz humana (opcional si usás FLEURS)

**Recomendado (sin grabar):**

```powershell
python scripts/download_common_voice_samples.py
```

Eso descarga `g1_fleurs.wav` … `g5_fleurs.wav` desde Google FLEURS (`es_419`).

**Alternativa manual:** grabá estos archivos con el texto exacto de
`reference_transcriptions.json` (`source: human_recorded`).

## Formato

- WAV, mono, 16 kHz, 16-bit (Audacity: Proyecto → 16000 Hz → mono → exportar WAV)
- Ambiente silencioso, micrófono estable
- Leé natural, como si hablaras con el agente (interacción), sin corregirte en voz alta

## Guion (leer tal cual)

1. **g1_interaccion_saludo.wav**  
   Hola Max, ¿me ayudás con una rutina corta de calentamiento antes de entrenar?

2. **g2_interaccion_cambio_agente.wav**  
   Quiero cambiar al agente de entretenimiento y que me expliques qué expresiones tiene disponibles.

3. **g3_interaccion_limites_gpu.wav**  
   Si mi tarjeta gráfica aguanta cincuenta mil triángulos, ¿puedo mostrar al mismo tiempo el gimnasio y el educativo?

4. **g4_interaccion_json_voz.wav**  
   Dictame en voz alta un resumen de tres puntos sobre latencia, costo y privacidad del pipeline del agente.

5. **g5_interaccion_cierre_cr.wav**  
   Diay mae, gracias por la sesión. Apaguemos el agente y guardemos la configuración para la próxima clase.

## Después de grabar

```powershell
python -m benchmarks.stt.run_all 5
```

Los benchmarks usan todos los `.wav` que existan; los `g*` se suman a los `a*` (Piper).
