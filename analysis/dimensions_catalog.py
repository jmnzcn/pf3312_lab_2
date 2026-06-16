"""Puntajes 1–5 (privacidad, customización, integración) por servicio."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualitativeScores:
    privacidad: int
    customizacion: int
    integracion: int


# Clave: "categoria/proveedor". Criterio cualitativo del proyecto (mayo 2026).
QUALITATIVE: dict[str, QualitativeScores] = {
    "llm/openai": QualitativeScores(3, 5, 5),
    "llm/anthropic": QualitativeScores(4, 5, 5),
    "llm/google": QualitativeScores(3, 4, 4),
    "llm/groq": QualitativeScores(4, 3, 4),
    "llm/ollama": QualitativeScores(5, 4, 3),
    "stt/openai": QualitativeScores(3, 3, 5),
    "stt/deepgram": QualitativeScores(3, 4, 4),
    "stt/assemblyai": QualitativeScores(3, 4, 4),
    "stt/azure": QualitativeScores(3, 4, 4),
    "stt/faster-whisper": QualitativeScores(5, 3, 3),
    "tts/openai": QualitativeScores(3, 4, 5),
    "tts/elevenlabs": QualitativeScores(3, 5, 4),
    "tts/azure": QualitativeScores(3, 4, 4),
    "tts/google": QualitativeScores(3, 4, 4),
    "tts/piper": QualitativeScores(5, 2, 2),
}


def validate_qualitative_catalog() -> None:
    """Falla si el catálogo cualitativo no coincide con BENCHMARK_REGISTRY."""
    from common.benchmark_registry import BENCHMARK_REGISTRY

    registered = {f"{s.category}/{s.provider}" for s in BENCHMARK_REGISTRY}
    documented = set(QUALITATIVE)
    missing = sorted(registered - documented)
    extra = sorted(documented - registered)
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"sin puntajes cualitativos: {missing}")
        if extra:
            parts.append(f"entradas huérfanas en QUALITATIVE: {extra}")
        raise RuntimeError("dimensions_catalog desalineado con benchmark_registry: " + "; ".join(parts))


def service_ids() -> list[str]:
    validate_qualitative_catalog()
    from common.benchmark_registry import BENCHMARK_REGISTRY

    return [f"{s.category}/{s.provider}" for s in BENCHMARK_REGISTRY]
