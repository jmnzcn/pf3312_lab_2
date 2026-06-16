"""Punto de entrada para correr un solo benchmark desde la línea de comandos."""
from __future__ import annotations

import sys
from typing import Callable, Iterable, TypeVar

from common.base import Benchmark
from common.results import append_results_csv, dump_results_json
from common.run_context import ensure_run_batch
from common.runner import safe_factory

T = TypeVar("T")


def load_stt_samples_or_exit() -> list:
    """Carga audios STT que existan en disco; termina sin error si no hay ninguno."""
    from common.audio_samples import load_audio_samples

    samples = [s for s in load_audio_samples() if s.exists()]
    if not samples:
        print("⚠ No hay audios en data/test_audio/. Ver README de esa carpeta.")
        raise SystemExit(0)
    return samples


def run_benchmark_main(
    *,
    category: str,
    factory: Callable[[], Benchmark],
    test_inputs: Iterable[T] | None = None,
    test_inputs_factory: Callable[[], Iterable[T]] | None = None,
    argv: list[str] | None = None,
    default_runs: int = 5,
) -> None:
    """Corre un solo proveedor: N repeticiones por input y guarda en results/."""
    if test_inputs_factory is not None:
        inputs = list(test_inputs_factory())
    elif test_inputs is not None:
        inputs = list(test_inputs)
    else:
        raise ValueError("Indicá test_inputs o test_inputs_factory")

    runs = int((argv or sys.argv)[1]) if len(argv or sys.argv) > 1 else default_runs
    ensure_run_batch(runs_per_input=runs, note=f"single:{category}")

    bench = safe_factory(category, factory)
    if bench is None:
        raise SystemExit(0)
    results = bench.run(inputs, runs_per_input=runs)
    append_results_csv(category, results)
    dump_results_json(category, bench.provider, results)
    ok = sum(1 for r in results if not r.error)
    print(f"OK · {ok}/{len(results)} exitosas · {bench.name()}")
