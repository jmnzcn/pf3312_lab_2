"""Benchmark Google Gemini Flash vía google-genai SDK.

Precios verificar en: https://ai.google.dev/pricing
Gemini 2.5 Flash tiene tier gratuito generoso para el benchmarking.
"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from google import genai

from common.base import Benchmark, BenchmarkResult, llm_output_fields
from common.metrics import elapsed_ms, estimate_llm_cost_usd
from common.prompts import LLM_PROMPTS, PromptSpec


load_dotenv()

# Rate público de Gemini 2.5 Flash (pay-as-you-go). El tier gratuito no cobra.
INPUT_RATE_PER_MILLION = 0.30
OUTPUT_RATE_PER_MILLION = 2.50


class GeminiBenchmark(Benchmark):
    category = "llm"
    provider = "google"
    model = "gemini-2.5-flash"
    deployment = "cloud"

    def __init__(self, model: str | None = None) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("Falta GOOGLE_API_KEY en .env")
        self.client = genai.Client(api_key=api_key)
        if model:
            self.model = model

    def run_single(self, test_input: PromptSpec, run_id: int) -> BenchmarkResult:
        start = time.perf_counter()
        ttft_ms: float | None = None
        output_chunks: list[str] = []
        usage = None

        stream = self.client.models.generate_content_stream(
            model=self.model,
            contents=test_input["content"],
        )
        for chunk in stream:
            if chunk.text:
                if ttft_ms is None:
                    ttft_ms = elapsed_ms(start)
                output_chunks.append(chunk.text)
            if getattr(chunk, "usage_metadata", None):
                usage = chunk.usage_metadata

        total_ms = elapsed_ms(start)
        output = "".join(output_chunks)

        input_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
        output_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0
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

    run_benchmark_main(category="llm", factory=GeminiBenchmark, test_inputs=LLM_PROMPTS)
