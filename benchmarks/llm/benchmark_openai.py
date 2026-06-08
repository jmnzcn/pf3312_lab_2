"""Benchmark OpenAI GPT-4o vía API.

Mide TTFT (tiempo al primer token) y latencia total con streaming.
Precios verificar en: https://openai.com/api/pricing/
"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.metrics import elapsed_ms, estimate_llm_cost_usd
from common.prompts import LLM_PROMPTS, PromptSpec


load_dotenv()


# Verificar tasas vigentes antes de correr el benchmark final.
INPUT_RATE_PER_MILLION = 2.50  # USD/M input tokens (gpt-4o)
OUTPUT_RATE_PER_MILLION = 10.00  # USD/M output tokens (gpt-4o)


class OpenAIBenchmark(Benchmark):
    category = "llm"
    provider = "openai"
    model = "gpt-4o"
    deployment = "cloud"

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta OPENAI_API_KEY en .env")
        self.client = OpenAI(api_key=api_key)
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
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                if ttft_ms is None:
                    ttft_ms = elapsed_ms(start)
                output_chunks.append(chunk.choices[0].delta.content)
            if getattr(chunk, "usage", None) is not None:
                usage = chunk.usage

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

    run_benchmark_main(category="llm", factory=OpenAIBenchmark, test_inputs=LLM_PROMPTS)
