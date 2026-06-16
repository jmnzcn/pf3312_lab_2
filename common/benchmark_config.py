"""Conteos de inputs y runs para análisis y filtrado de CSV."""
from __future__ import annotations

import json
from pathlib import Path

from common.audio_samples import REFERENCE_FILE, TTS_TEXTS
from common.prompts import LLM_PROMPTS
from common.run_context import load_manifest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def runs_per_input(default: int = 5) -> int:
    manifest = load_manifest()
    raw = manifest.get("runs_per_input")
    if raw is None:
        return default
    return int(raw)


def stt_input_count() -> int:
    if not REFERENCE_FILE.exists():
        raise FileNotFoundError(
            f"Falta catálogo STT: {REFERENCE_FILE.relative_to(PROJECT_ROOT)}"
        )
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    return len(data.get("samples", []))


def llm_input_count() -> int:
    return len(LLM_PROMPTS)


def tts_input_count() -> int:
    return len(TTS_TEXTS)


def category_row_count(category: str, *, runs: int | None = None) -> int:
    r = runs if runs is not None else runs_per_input()
    if category == "stt":
        return stt_input_count() * r
    if category == "llm":
        return llm_input_count() * r
    if category == "tts":
        return tts_input_count() * r
    raise ValueError(f"Categoría desconocida: {category}")
