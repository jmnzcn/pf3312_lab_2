"""Clase base Benchmark y el dataclass de resultados."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from common.benchmark_errors import format_exception


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class BenchmarkResult:
    """Una fila de resultado (LLM, STT o TTS). Campos que no apliquen quedan en None."""
    timestamp: str = field(default_factory=_utcnow)
    category: str = ""
    provider: str = ""
    model: str = ""
    deployment: str = "cloud"
    test_id: str = ""
    run_id: int = 0
    run_batch_id: str = ""
    notes: str = ""

    latency_ms: float = 0.0
    ttft_ms: Optional[float] = None  # solo LLM en streaming

    input_size: int = 0
    output_size: int = 0
    input_unit: str = ""
    output_unit: str = ""

    cost_usd: Optional[float] = None

    quality_metric: Optional[float] = None
    quality_metric_name: str = ""

    output_text: str = ""
    output_preview: str = ""

    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def llm_output_fields(text: str) -> dict[str, str]:
    """Texto completo para results/raw/ y preview corto para CSV."""
    return {"output_text": text, "output_preview": text[:200]}


def stt_output_fields(text: str) -> dict[str, str]:
    """Transcripción completa para E2E/raw; preview truncado para CSV."""
    return {"output_text": text, "output_preview": text[:200]}


class Benchmark(ABC):
    """Subclases implementan run_single(); run() itera inputs y runs."""

    category: str = "abstract"
    provider: str = "abstract"
    model: str = "abstract"
    deployment: str = "cloud"

    def name(self) -> str:
        return f"{self.category}/{self.provider}/{self.model}"

    @abstractmethod
    def run_single(self, test_input: Any, run_id: int) -> BenchmarkResult:
        """Una llamada al proveedor."""
        ...

    def run(
        self,
        test_inputs: Iterable[Any],
        runs_per_input: int = 5,
    ) -> list[BenchmarkResult]:
        """Corre todos los inputs N veces."""
        results: list[BenchmarkResult] = []
        for test in test_inputs:
            for run_id in range(1, runs_per_input + 1):
                try:
                    result = self.run_single(test, run_id)
                except Exception as exc:
                    # Un proveedor caído no debe tumbar el resto del batch
                    result = BenchmarkResult(
                        category=self.category,
                        provider=self.provider,
                        model=self.model,
                        deployment=self.deployment,
                        test_id=_test_id(test),
                        run_id=run_id,
                        error=format_exception(exc),
                        notes=format_exception(exc),
                    )
                results.append(result)
        return results


def _test_id(test: Any) -> str:
    if isinstance(test, dict) and "id" in test:
        return str(test["id"])
    if hasattr(test, "id"):
        return str(getattr(test, "id"))
    return str(test)[:50]
