"""Escenarios de pipeline compartidos entre E2E y análisis de costo."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PipelineScenario:
    nombre: str
    stt: str
    llm: str
    tts: str


PIPELINE_SCENARIOS: tuple[PipelineScenario, ...] = (
    PipelineScenario("Demo rápida nube", "deepgram", "groq", "google"),
    PipelineScenario("Calidad premium", "assemblyai", "openai", "elevenlabs"),
    PipelineScenario("Privacidad offline", "faster-whisper", "ollama", "piper"),
    PipelineScenario("Stack Azure", "azure", "openai", "azure"),
)

# Cinco audios para E2E: corto, medio, FLEURS, ruido y largo
E2E_AUDIO_IDS: tuple[str, ...] = (
    "a1_saludo_corto",
    "a2_oracion_media",
    "g1_fleurs",
    "c1_cv_noisy",
    "l1_fleurs_largo",
)

E2E_AUDIO_RATIONALE = (
    "Cinco audios del catálogo: saludos Piper (corto/medio), FLEURS limpio, "
    "Common Voice con ruido y un turno largo."
)


def scenario_dicts() -> list[dict[str, str]]:
    return [
        {"escenario": s.nombre, "stt": s.stt, "llm": s.llm, "tts": s.tts}
        for s in PIPELINE_SCENARIOS
    ]
