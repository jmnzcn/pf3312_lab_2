"""Groq API con Llama 3.3 70B."""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from groq import Groq

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.benchmark_errors import mark_empty_llm
from common.metrics import elapsed_ms, estimate_llm_cost_usd
from common.prompts import LLM_PROMPTS, PromptSpec


load_dotenv()

# Rate público de Llama 3.3 70B Versatile en Groq.
from common.rates import (
    GROQ_LLAMA33_INPUT_PER_M,
    GROQ_LLAMA33_OUTPUT_PER_M,
)

INPUT_RATE_PER_MILLION = GROQ_LLAMA33_INPUT_PER_M
OUTPUT_RATE_PER_MILLION = GROQ_LLAMA33_OUTPUT_PER_M


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
            if getattr(chunk, "usage", None):
                usage = chunk.usage
            elif getattr(chunk, "x_groq", None) and getattr(chunk.x_groq, "usage", None):
                usage = chunk.x_groq.usage

        total_ms = elapsed_ms(start)
        output = "".join(output_chunks)

        input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
        notes = ""
        if (input_tokens == 0 and output_tokens == 0) and output:
            notes = "usage_no_reportado_en_stream"
        cost = estimate_llm_cost_usd(
            input_tokens,
            output_tokens,
            INPUT_RATE_PER_MILLION,
            OUTPUT_RATE_PER_MILLION,
        )

        result = BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input["id"],
            run_id=run_id,
            notes=notes,
            latency_ms=total_ms,
            ttft_ms=ttft_ms,
            input_size=input_tokens,
            output_size=output_tokens,
            input_unit="tokens",
            output_unit="tokens",
            cost_usd=cost,
            **llm_output_fields(output),
        )
        return mark_empty_llm(result, output)


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="llm", factory=GroqBenchmark, test_inputs=LLM_PROMPTS)
