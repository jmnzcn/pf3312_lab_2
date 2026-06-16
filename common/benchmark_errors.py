"""Formatea errores de benchmarks y del pipeline E2E."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from common.base import BenchmarkResult
    from common.e2e import E2ETurnResult


def _short(value: object, *, max_len: int = 200) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ").strip()
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def format_exception(exc: BaseException, *, max_len: int = 480) -> str:
    """Resume una excepción; incluye status_code y body si el SDK los expone."""
    parts = [f"{type(exc).__name__}: {_short(exc)}"]
    for attr in ("status_code", "code", "message", "reason", "type"):
        if hasattr(exc, attr):
            val = getattr(exc, attr)
            if val not in (None, ""):
                parts.append(f"{attr}={_short(val)}")
    body = getattr(exc, "body", None)
    if body not in (None, ""):
        parts.append(f"body={_short(body)}")
    if exc.__cause__ is not None:
        parts.append(f"cause={format_exception(exc.__cause__, max_len=160)}")
    return " · ".join(parts)[:max_len]


def stage_error(stage: str, provider: str, detail: str) -> str:
    return f"{stage}/{provider}: {detail}"


def provider_error(provider: str, detail: str, *, stage: str = "") -> str:
    if stage:
        return stage_error(stage, provider, detail)
    return f"{provider}: {detail}"


def mark_empty_output(
    result: BenchmarkResult,
    *,
    stage: str,
    label: str,
    detail: str = "",
) -> BenchmarkResult:
    """Marca error cuando el proveedor devolvió salida vacía."""
    extra = detail or "sin salida del proveedor"
    result.error = stage_error(stage, result.provider, f"{label} vacía · {extra}")
    if not result.notes:
        result.notes = extra
    return result


def mark_empty_stt(result: BenchmarkResult, text: str, *, detail: str = "") -> BenchmarkResult:
    if (text or "").strip():
        return result
    return mark_empty_output(
        result,
        stage="stt",
        label="transcripción",
        detail=detail or "sin texto reconocido",
    )


def mark_empty_llm(result: BenchmarkResult, output: str, *, detail: str = "") -> BenchmarkResult:
    if (output or "").strip():
        return result
    return mark_empty_output(
        result,
        stage="llm",
        label="respuesta",
        detail=detail or "stream sin tokens de salida",
    )


def mark_tts_output(
    result: BenchmarkResult,
    out_file: Path,
    *,
    detail: str = "",
) -> BenchmarkResult:
    size = out_file.stat().st_size if out_file.exists() else 0
    if size > 0:
        return result
    extra = detail or f"archivo={out_file.name} · bytes={size}"
    return mark_empty_output(result, stage="tts", label="audio", detail=extra)


def fail_e2e_stage(
    turn: E2ETurnResult,
    *,
    stage: str,
    provider: str,
    detail: str,
    notes: str = "",
    wall_start: float,
    elapsed_ms_fn,
) -> E2ETurnResult:
    turn.error = stage_error(stage, provider, detail)
    if notes:
        turn.notes = notes
    turn.total_latency_ms = elapsed_ms_fn(wall_start)
    return turn


def e2e_exception_stage(turn: E2ETurnResult, scenario) -> tuple[str, str]:
    """Deduce etapa y proveedor según qué campos del turno ya se llenaron."""
    if turn.llm_latency_ms or turn.llm_response:
        return "tts", scenario.tts
    if turn.stt_latency_ms or turn.transcript:
        return "llm", scenario.llm
    return "stt", scenario.stt
