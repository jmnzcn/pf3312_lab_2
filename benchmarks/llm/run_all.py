"""Corre todos los benchmarks LLM que tengan API key."""
from __future__ import annotations

import sys

from common.benchmark_registry import factory_pairs
from common.prompts import LLM_PROMPTS
from common.runner import run_category_benchmarks
from common.run_context import ensure_run_batch


def main(runs: int = 5) -> None:
    ensure_run_batch(runs_per_input=runs, note="llm run_all")
    run_category_benchmarks(
        "llm",
        factory_pairs("llm"),
        LLM_PROMPTS,
        runs=runs,
        input_label="prompts",
    )


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(runs=runs)
