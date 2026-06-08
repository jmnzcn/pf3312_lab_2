"""Utilidades compartidas para runners de benchmarks."""
from __future__ import annotations

import traceback
from typing import Callable, Iterable, TypeVar

from common.base import Benchmark
from common.results import append_results_csv, dump_results_json

T = TypeVar("T")


def safe_factory(name: str, factory: Callable[[], Benchmark]) -> Benchmark | None:
    try:
        return factory()
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] {name} no disponible: {exc}")
        return None


def run_category_benchmarks(
    category: str,
    factories: list[tuple[str, Callable[[], Benchmark]]],
    test_inputs: Iterable[T],
    *,
    runs: int,
    input_label: str,
    log_prefix: str = ">>",
) -> int:
    inputs = list(test_inputs)
    if not inputs:
        print(f"[WARN] Sin inputs para {category.upper()}")
        return 0

    total = 0
    for name, factory in factories:
        bench = safe_factory(name, factory)
        if bench is None:
            continue
        print(f"{log_prefix} {bench.name()} ({runs} runs x {len(inputs)} {input_label})")
        try:
            results = bench.run(inputs, runs_per_input=runs)
        except Exception:
            traceback.print_exc()
            continue
        append_results_csv(category, results)
        dump_results_json(category, bench.provider, results)
        ok = sum(1 for r in results if not r.error)
        print(f"  OK {ok}/{len(results)} llamadas exitosas")
        total += len(results)

    print(f"\nTotal {category.upper()}: {total} filas en results/{category}_results.csv")
    return total
