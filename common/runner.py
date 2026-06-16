"""Orquesta los run_all de LLM, STT y TTS (varios proveedores por categoría)."""
from __future__ import annotations

import traceback
from typing import Callable, Iterable, TypeVar

from common.base import Benchmark
from common.results import append_results_csv, dump_results_json

T = TypeVar("T")


def safe_factory(name: str, factory: Callable[[], Benchmark]) -> Benchmark | None:
    """Instancia el benchmark; devuelve None si falla import, key o binario."""
    try:
        return factory()
    except Exception as exc:
        # Sin API key, import roto o binario ausente: se omite el proveedor
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
    """Ejecuta cada proveedor de la categoría y escribe results/."""
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
