"""Benchmark LLM local con Ollama (Llama 3.2 3B por defecto).

Requisitos previos:
    - Instalar Ollama: https://ollama.com/download
    - `ollama pull llama3.2:3b`  (o el modelo declarado en OLLAMA_MODEL)
    - Servidor levantado en http://localhost:11434

Costo: 0 USD por llamada (offline). El "costo real" se reporta como infraestructura:
VRAM/RAM/energía, lo cual se documenta a mano en el reporte PDF.
"""
from __future__ import annotations

import os
import time

import ollama
from dotenv import load_dotenv

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.metrics import elapsed_ms
from common.prompts import LLM_PROMPTS, PromptSpec


load_dotenv()


class OllamaBenchmark(Benchmark):
    category = "llm"
    provider = "ollama"
    deployment = "local"

    def __init__(self, model: str | None = None) -> None:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.client = ollama.Client(host=host)
        # Warm-up: la primera llamada de un modelo no cargado en VRAM es muy
        # lenta. Se hace una llamada de calentamiento para evitar contaminar
        # la primera medición.
        try:
            self.client.generate(model=self.model, prompt="hola", options={"num_predict": 1})
            print(f"[INFO] Ollama warm-up OK ({self.model})")
        except Exception as exc:
            print(f"[WARN] Ollama warm-up falló ({self.model}): {exc}")

    def run_single(self, test_input: PromptSpec, run_id: int) -> BenchmarkResult:
        start = time.perf_counter()
        ttft_ms: float | None = None
        output_chunks: list[str] = []
        eval_count = 0
        prompt_eval_count = 0

        stream = self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": test_input["content"]}],
            stream=True,
        )
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if content:
                if ttft_ms is None:
                    ttft_ms = elapsed_ms(start)
                output_chunks.append(content)
            if chunk.get("done"):
                eval_count = chunk.get("eval_count", 0)
                prompt_eval_count = chunk.get("prompt_eval_count", 0)

        total_ms = elapsed_ms(start)
        output = "".join(output_chunks)

        return BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input["id"],
            run_id=run_id,
            latency_ms=total_ms,
            ttft_ms=ttft_ms,
            input_size=prompt_eval_count,
            output_size=eval_count,
            input_unit="tokens",
            output_unit="tokens",
            cost_usd=0.0,  # offline
            **llm_output_fields(output),
        )


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="llm", factory=OllamaBenchmark, test_inputs=LLM_PROMPTS)
