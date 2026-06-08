"""Clases base y schemas para los benchmarks.

Cada proveedor (OpenAI, Anthropic, etc.) implementa una subclase de Benchmark
y solo necesita definir `run_single`. El método `run` itera sobre los inputs
de prueba y los runs solicitados, capturando errores en el propio result.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Iterable, Optional


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class BenchmarkResult:
    """Schema único para todos los resultados (LLM, STT y TTS).

    Los campos opcionales que no apliquen a una categoría se dejan en None.
    """
    timestamp: str = field(default_factory=_utcnow)
    category: str = ""                 # "llm" | "stt" | "tts"
    provider: str = ""                 # "openai" | "anthropic" | ...
    model: str = ""                    # "gpt-4o" | "claude-3-5-sonnet" | ...
    deployment: str = "cloud"          # "cloud" | "local"
    test_id: str = ""                  # identificador del input de prueba
    run_id: int = 0                    # 1..N
    run_batch_id: str = ""             # corrida agrupada (ISO UTC)
    notes: str = ""                    # metadata (ej. device=cpu)

    # Métricas de tiempo
    latency_ms: float = 0.0            # tiempo total end-to-end
    ttft_ms: Optional[float] = None    # solo LLM streaming: tiempo al primer token

    # Tamaños
    input_size: int = 0                # tokens (LLM), segundos*100 (STT), chars (TTS)
    output_size: int = 0
    input_unit: str = ""               # "tokens" | "seconds_x100" | "chars"
    output_unit: str = ""

    # Costo estimado en USD (None si no aplica o se desconoce el rate)
    cost_usd: Optional[float] = None

    # Métrica de calidad (WER para STT; None para los demás por defecto)
    quality_metric: Optional[float] = None
    quality_metric_name: str = ""

    # Output completo (JSON raw) y preview truncado para CSV
    output_text: str = ""
    output_preview: str = ""

    # Errores capturados durante la ejecución
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def llm_output_fields(text: str) -> dict[str, str]:
    """Texto completo para results/raw/ y preview corto para CSV."""
    return {"output_text": text, "output_preview": text[:200]}


class Benchmark(ABC):
    """Clase base para todos los benchmarks.

    Subclases deben definir:
      - category, provider, model, deployment a nivel de clase.
      - run_single(test_input, run_id) -> BenchmarkResult.
    """

    category: str = "abstract"
    provider: str = "abstract"
    model: str = "abstract"
    deployment: str = "cloud"

    def name(self) -> str:
        return f"{self.category}/{self.provider}/{self.model}"

    @abstractmethod
    def run_single(self, test_input: Any, run_id: int) -> BenchmarkResult:
        """Ejecuta UNA llamada al servicio y devuelve el resultado."""
        ...

    def run(
        self,
        test_inputs: Iterable[Any],
        runs_per_input: int = 5,
    ) -> list[BenchmarkResult]:
        """Ejecuta el benchmark sobre todos los inputs, N veces cada uno."""
        results: list[BenchmarkResult] = []
        for test in test_inputs:
            for run_id in range(1, runs_per_input + 1):
                try:
                    result = self.run_single(test, run_id)
                except Exception as exc:  # noqa: BLE001 - captura amplia a propósito
                    result = BenchmarkResult(
                        category=self.category,
                        provider=self.provider,
                        model=self.model,
                        deployment=self.deployment,
                        test_id=_test_id(test),
                        run_id=run_id,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                results.append(result)
        return results


def _test_id(test: Any) -> str:
    if isinstance(test, dict) and "id" in test:
        return str(test["id"])
    if hasattr(test, "id"):
        return str(getattr(test, "id"))
    return str(test)[:50]
