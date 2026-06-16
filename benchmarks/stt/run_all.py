"""Corre todos los benchmarks STT que tengan API key."""
from __future__ import annotations

import sys

from common.audio_samples import load_audio_samples
from common.benchmark_registry import factory_pairs
from common.runner import run_category_benchmarks
from common.run_context import ensure_run_batch


def main(runs: int = 5) -> None:
    samples = [s for s in load_audio_samples() if s.exists()]
    if not samples:
        print("[WARN] No hay audios en data/test_audio/. Ver data/test_audio/README.md")
        return

    ensure_run_batch(runs_per_input=runs, note="stt run_all")
    run_category_benchmarks(
        "stt",
        factory_pairs("stt"),
        samples,
        runs=runs,
        input_label="audios",
    )


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(runs=runs)
