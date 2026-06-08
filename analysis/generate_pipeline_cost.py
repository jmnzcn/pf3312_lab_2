"""Estima costo de un turno conversacional (STT + LLM + TTS)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from tabulate import tabulate

from analysis.aggregate import load_category_df

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "docs" / "tablas_generadas"

SCENARIOS = [
    {
        "escenario": "Demo rápida nube",
        "llm": "groq",
        "stt": "deepgram",
        "tts": "google",
    },
    {
        "escenario": "Calidad premium",
        "llm": "openai",
        "stt": "assemblyai",
        "tts": "elevenlabs",
    },
    {
        "escenario": "Privacidad offline",
        "llm": "ollama",
        "stt": "faster-whisper",
        "tts": "piper",
    },
    {
        "escenario": "Stack Azure",
        "llm": "openai",
        "stt": "azure",
        "tts": "azure",
    },
]


def _mean_cost(df: pd.DataFrame, provider: str) -> float:
    sub = df[df["provider"] == provider]
    if sub.empty:
        return 0.0
    return float(sub["cost_usd"].mean())


def _mean_latency(df: pd.DataFrame, provider: str) -> float:
    sub = df[df["provider"] == provider]
    if sub.empty:
        return 0.0
    return float(sub["latency_ms"].mean())


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    llm = load_category_df("llm")
    stt = load_category_df("stt")
    tts = load_category_df("tts")
    rows = []
    for sc in SCENARIOS:
        cost = (
            _mean_cost(llm, sc["llm"])
            + _mean_cost(stt, sc["stt"])
            + _mean_cost(tts, sc["tts"])
        )
        lat = (
            _mean_latency(llm, sc["llm"])
            + _mean_latency(stt, sc["stt"])
            + _mean_latency(tts, sc["tts"])
        )
        rows.append(
            {
                "escenario": sc["escenario"],
                "llm": sc["llm"],
                "stt": sc["stt"],
                "tts": sc["tts"],
                "costo_usd_turno": round(cost, 6),
                "latencia_ms_turno": round(lat, 1),
            }
        )
    body = tabulate(rows, headers="keys", tablefmt="github", showindex=False)
    content = (
        "# Costo estimado por turno conversacional (STT + LLM + TTS)\n\n"
        "*Promedio de costo/latencia por llamada en la última corrida filtrada.*\n\n"
        f"{body}\n"
    )
    out = OUT_DIR / "costo_pipeline.md"
    out.write_text(content, encoding="utf-8")
    print(f"OK {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
