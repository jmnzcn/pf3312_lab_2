"""Registro de audios de prueba para STT y textos para TTS.

Convención:
    - Los audios viven en `data/test_audio/` y se nombran como `<id>.wav`.
    - Las transcripciones de referencia están en `data/reference_transcriptions.json`.
    - Los textos para TTS están definidos directamente aquí (no hay que crearlos
      como audio).

Para STT necesitás al menos 3 audios cortos (3-10s) y 1 medio (30-60s) en español
con su transcripción exacta de referencia para poder calcular WER.

Si no querés grabar, podés:
    - Tomar audios CC0 de Mozilla Common Voice (español): https://commonvoice.mozilla.org/es/datasets
    - Sintetizar audios con un TTS y usar el texto original como referencia (ojo:
      esto sesga la métrica WER porque la voz será muy clara).

Si un audio listado abajo no existe en disco, los benchmarks de STT lo saltan
con un warning.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import soundfile as sf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_AUDIO_DIR = PROJECT_ROOT / "data" / "test_audio"
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"


@dataclass
class AudioSample:
    id: str
    path: Path
    reference_text: str
    language: str = "es-CR"
    duration_sec: Optional[float] = None

    def exists(self) -> bool:
        return self.path.exists()

    def load_duration(self) -> float:
        if self.duration_sec is None and self.exists():
            with sf.SoundFile(str(self.path)) as snd:
                self.duration_sec = len(snd) / snd.samplerate
        return self.duration_sec or 0.0


def load_audio_samples() -> list[AudioSample]:
    """Carga el catálogo desde reference_transcriptions.json."""
    if not REFERENCE_FILE.exists():
        return []
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    samples: list[AudioSample] = []
    for entry in data.get("samples", []):
        samples.append(
            AudioSample(
                id=entry["id"],
                path=TEST_AUDIO_DIR / entry["file"],
                reference_text=entry["reference_text"],
                language=entry.get("language", "es-CR"),
            )
        )
    return samples


# === Textos para TTS ===
# Reusamos algunos prompts cortos como texto a sintetizar. Para TTS no medimos
# WER, sino latencia y costo. La naturalidad/inteligibilidad se evalúa
# cualitativamente escuchando los outputs en results/tts_outputs/.

TTS_TEXTS = [
    {
        "id": "t1_saludo_corto",
        "text": "Hola, ¿cómo estás? Soy un agente virtual de prueba.",
    },
    {
        "id": "t2_oracion_media",
        "text": (
            "Bienvenido al sistema de evaluación comparativa. "
            "Hoy compararemos cinco proveedores de síntesis de voz "
            "bajo seis dimensiones técnicas distintas."
        ),
    },
    {
        "id": "t3_parrafo_largo",
        "text": (
            "El benchmarking de servicios cognitivos para agentes virtuales "
            "requiere evaluar latencia, precisión, costo, privacidad, "
            "flexibilidad de personalización y facilidad de integración. "
            "Cada categoría —reconocimiento de voz, modelos de lenguaje y "
            "síntesis de voz— responde de manera distinta bajo esas dimensiones, "
            "por lo cual la decisión arquitectónica debe sustentarse en datos "
            "empíricos y no en percepciones generales."
        ),
    },
    {
        "id": "t4_terminos_tecnicos",
        "text": (
            "El agente virtual procesa audio a dieciséis kilohertz, calcula "
            "latencia al primer token y sintetiza respuestas con lip-sync."
        ),
    },
    {
        "id": "t5_dialogo_cr",
        "text": (
            "Mae, ¿podés explicarme en pocas palabras cómo elegir entre Groq, "
            "OpenAI y un modelo local para el tutor virtual?"
        ),
    },
]
