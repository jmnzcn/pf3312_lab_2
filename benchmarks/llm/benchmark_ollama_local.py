"""LLM local con Ollama (modelo por defecto: llama3.2:3b)."""
from __future__ import annotations

import os
import time

import ollama
from dotenv import load_dotenv

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.benchmark_errors import mark_empty_llm
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
        # Primera llamada con modelo frío tarda mucho; se descarta del cronometraje
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

        result = BenchmarkResult(
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
        return mark_empty_llm(result, output)


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="llm", factory=OllamaBenchmark, test_inputs=LLM_PROMPTS)
