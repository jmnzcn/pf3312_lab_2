"""Benchmark Groq con Llama 3.3 70B.

Groq es API gratuita y conocida por TTFT extremadamente bajos (decenas de ms).
Precios: https://groq.com/pricing
"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from groq import Groq

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.metrics import elapsed_ms, estimate_llm_cost_usd
from common.prompts import LLM_PROMPTS, PromptSpec


load_dotenv()

# Rate público de Llama 3.3 70B Versatile en Groq.
INPUT_RATE_PER_MILLION = 0.59
OUTPUT_RATE_PER_MILLION = 0.79


class GroqBenchmark(Benchmark):
    category = "llm"
    provider = "groq"
    model = "llama-3.3-70b-versatile"
    deployment = "cloud"

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("Falta GROQ_API_KEY en .env")
        self.client = Groq(api_key=api_key)
        if model:
            self.model = model

    def run_single(self, test_input: PromptSpec, run_id: int) -> BenchmarkResult:
        start = time.perf_counter()
        ttft_ms: float | None = None
        output_chunks: list[str] = []
        usage = None

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": test_input["content"]}],
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                if ttft_ms is None:
                    ttft_ms = elapsed_ms(start)
                output_chunks.append(chunk.choices[0].delta.content)
            if getattr(chunk, "x_groq", None) and getattr(chunk.x_groq, "usage", None):
                usage = chunk.x_groq.usage

        total_ms = elapsed_ms(start)
        output = "".join(output_chunks)

        input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        cost = estimate_llm_cost_usd(
            input_tokens,
            output_tokens,
            INPUT_RATE_PER_MILLION,
            OUTPUT_RATE_PER_MILLION,
        )

        return BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input["id"],
            run_id=run_id,
            latency_ms=total_ms,
            ttft_ms=ttft_ms,
            input_size=input_tokens,
            output_size=output_tokens,
            input_unit="tokens",
            output_unit="tokens",
            cost_usd=cost,
            **llm_output_fields(output),
        )


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="llm", factory=GroqBenchmark, test_inputs=LLM_PROMPTS)
