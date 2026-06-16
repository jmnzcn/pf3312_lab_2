"""Cronómetro, WER y fórmulas de costo usadas en los benchmarks."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

import jiwer


@contextmanager
def stopwatch() -> Iterator[dict]:
    """Devuelve elapsed_ms al salir del bloque with."""
    state: dict = {"elapsed_ms": None, "start": time.perf_counter()}
    try:
        yield state
    finally:
        state["elapsed_ms"] = (time.perf_counter() - state["start"]) * 1000.0


def elapsed_ms(start_perf: float) -> float:
    return (time.perf_counter() - start_perf) * 1000.0


def compute_wer(reference: str, hypothesis: str) -> float:
    """WER con normalización: minúsculas, sin puntuación, espacios colapsados."""
    transform = jiwer.Compose(
        [
            jiwer.ToLowerCase(),
            jiwer.RemovePunctuation(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.ReduceToListOfListOfWords(),
        ]
    )
    return jiwer.wer(
        reference,
        hypothesis,
        reference_transform=transform,
        hypothesis_transform=transform,
    )


# Costos estimados (USD)


def estimate_llm_cost_usd(
    input_tokens: int,
    output_tokens: int,
    input_rate_per_million: float,
    output_rate_per_million: float,
) -> float:
    """Costo LLM = (tokens_entrada × tarifa_in + tokens_salida × tarifa_out) / 1e6."""
    return (
        input_tokens * input_rate_per_million
        + output_tokens * output_rate_per_million
    ) / 1_000_000.0


def estimate_stt_cost_usd(audio_seconds: float, rate_per_minute: float) -> float:
    return (audio_seconds / 60.0) * rate_per_minute


def estimate_tts_cost_usd(num_characters: int, rate_per_million_chars: float) -> float:
    return (num_characters / 1_000_000.0) * rate_per_million_chars
