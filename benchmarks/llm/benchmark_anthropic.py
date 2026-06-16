"""Anthropic Claude Sonnet (claude-sonnet-4-6 por defecto)."""
from __future__ import annotations

import os
import time

import anthropic
from dotenv import load_dotenv

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.benchmark_errors import mark_empty_llm
from common.metrics import elapsed_ms, estimate_llm_cost_usd
from common.rates import ANTHROPIC_SONNET4_INPUT_PER_M, ANTHROPIC_SONNET4_OUTPUT_PER_M
from common.prompts import LLM_PROMPTS, PromptSpec


load_dotenv()

INPUT_RATE_PER_MILLION = ANTHROPIC_SONNET4_INPUT_PER_M
OUTPUT_RATE_PER_MILLION = ANTHROPIC_SONNET4_OUTPUT_PER_M


class AnthropicBenchmark(Benchmark):
    category = "llm"
    provider = "anthropic"
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    deployment = "cloud"

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Falta ANTHROPIC_API_KEY en .env")
        self.client = anthropic.Anthropic(api_key=api_key)
        if model:
            self.model = model

    def run_single(self, test_input: PromptSpec, run_id: int) -> BenchmarkResult:
        start = time.perf_counter()
        ttft_ms: float | None = None
        output_chunks: list[str] = []
        input_tokens = 0
        output_tokens = 0

        with self.client.messages.stream(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": test_input["content"]}],
        ) as stream:
            for chunk in stream.text_stream:
                if ttft_ms is None:
                    ttft_ms = elapsed_ms(start)
                output_chunks.append(chunk)
            final = stream.get_final_message()
            input_tokens = final.usage.input_tokens
            output_tokens = final.usage.output_tokens

        total_ms = elapsed_ms(start)
        output = "".join(output_chunks)

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

    run_benchmark_main(category="llm", factory=AnthropicBenchmark, test_inputs=LLM_PROMPTS)
