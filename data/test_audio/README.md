# Audios de prueba para STT

Los benchmarks de STT esperan encontrar archivos `.wav` aquí con los nombres
declarados en `data/reference_transcriptions.json`. Cada audio debe ir
acompañado de su transcripción exacta de referencia para que se pueda
calcular el WER (Word Error Rate).

## Cómo generar los audios

Tenés tres opciones (de menos a más esfuerzo):

1. **Grabarlos vos mismo** con cualquier app de grabación. Asegúrese de
   leer el texto exactamente como aparece en `reference_transcriptions.json`.
   Exporte como WAV 16 kHz mono, 16-bit. En Windows, Audacity funciona bien.

2. **Sintetizar los audios** con un TTS comercial (por ejemplo, ElevenLabs o
   Google TTS) y guardarlos aquí. Cuidado: esto **sesga el WER hacia 0**
   porque la voz es muy clara; el resultado servirá para comparar
   proveedores entre sí, pero no será representativo de voz humana real.

3. **Voz humana sin grabar** — script automático (FLEURS `es_419`):

   ```powershell
   pip install datasets
   python scripts/download_common_voice_samples.py
   ```

   Descarga 5 clips de voz humana leída en español latinoamericano, los guarda
   como `g1_fleurs.wav` … `g5_fleurs.wav` y actualiza `reference_transcriptions.json`
   con la transcripción real (CC BY 4.0).

   > *Nota:* Mozilla Common Voice ya no está en Hugging Face; requiere registro en
   > [Mozilla Data Collective](https://datacollective.mozillafoundation.org/). FLEURS
   > cumple el mismo rol metodológico (voz humana + ground truth para WER).

## Formato esperado

- Codec: WAV 16-bit PCM
- Sample rate: 16 kHz (recomendado) o 44.1 kHz
- Canales: mono
- Duración: el catálogo incluye 1 audio corto (~5s), 1 medio (~15s) y 3
  parecidos para tener al menos 5 inputs distintos para promediar.

## Si falta algún audio

Los scripts de STT detectan automáticamente los archivos faltantes y los
saltan con un warning. Es decir, podés correr el benchmark con 2 audios
disponibles y luego completar con los otros 3 sin romper nada.
