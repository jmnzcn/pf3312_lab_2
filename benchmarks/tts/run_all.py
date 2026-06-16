"""Corre todos los benchmarks TTS que tengan API key."""
from __future__ import annotations

import sys

from common.audio_samples import TTS_TEXTS
from common.benchmark_registry import factory_pairs
from common.runner import run_category_benchmarks
from common.run_context import ensure_run_batch


def main(runs: int = 5) -> None:
    ensure_run_batch(runs_per_input=runs, note="tts run_all")
    run_category_benchmarks(
        "tts",
        factory_pairs("tts"),
        TTS_TEXTS,
        runs=runs,
        input_label="textos",
        log_prefix=">>",
    )


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(runs=runs)
