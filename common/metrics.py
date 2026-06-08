"""Métricas y helpers: cronómetro, WER, estimaciones de costo."""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

import jiwer


@contextmanager
def stopwatch() -> Iterator[dict]:
    """Mide tiempo en milisegundos.

    Uso:
        with stopwatch() as sw:
            ... código a medir ...
        print(sw["elapsed_ms"])
    """
    state: dict = {"elapsed_ms": None, "start": time.perf_counter()}
    try:
        yield state
    finally:
        state["elapsed_ms"] = (time.perf_counter() - state["start"]) * 1000.0


def elapsed_ms(start_perf: float) -> float:
    return (time.perf_counter() - start_perf) * 1000.0


def compute_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate normalizado (minúsculas, sin puntuación)."""
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


# === Estimaciones de costo ===


def estimate_llm_cost_usd(
    input_tokens: int,
    output_tokens: int,
    input_rate_per_million: float,
    output_rate_per_million: float,
) -> float:
    """USD = (in_tokens * in_rate + out_tokens * out_rate) / 1_000_000."""
    return (
        input_tokens * input_rate_per_million
        + output_tokens * output_rate_per_million
    ) / 1_000_000.0


def estimate_stt_cost_usd(audio_seconds: float, rate_per_minute: float) -> float:
    return (audio_seconds / 60.0) * rate_per_minute


def estimate_tts_cost_usd(num_characters: int, rate_per_million_chars: float) -> float:
    return (num_characters / 1_000_000.0) * rate_per_million_chars
