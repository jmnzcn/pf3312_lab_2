# Herramientas locales

## Piper TTS

Descargar el binario de Piper para Windows y colocarlo en:

```text
tools/piper/piper/piper.exe
```

Configurar en `.env`:

```env
PIPER_BIN=tools/piper/piper/piper.exe
PIPER_CWD=tools/piper/piper
PIPER_MODEL_PATH=models/piper/es_ES-davefx-medium.onnx
```

El modelo ONNX se descarga aparte en `models/piper/` (ver `benchmarks/tts/benchmark_piper_local.py`).
