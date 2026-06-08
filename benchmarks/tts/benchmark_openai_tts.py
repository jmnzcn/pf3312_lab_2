"""Benchmark OpenAI TTS (gpt-4o-mini-tts)."""
from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from common.audio_samples import TTS_TEXTS
from common.base import Benchmark, BenchmarkResult
from common.metrics import elapsed_ms, estimate_tts_cost_usd


load_dotenv()

# gpt-4o-mini-tts pricing (verificar en openai.com/api/pricing)
RATE_PER_MILLION_CHARS = 600.0  # USD/M chars aprox (15 USD/1M tokens audio output)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "tts_outputs"


class OpenAITTSBenchmark(Benchmark):
    category = "tts"
    provider = "openai"
    model = "gpt-4o-mini-tts"
    deployment = "cloud"

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta OPENAI_API_KEY en .env")
        self.client = OpenAI(api_key=api_key)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def run_single(self, test_input: dict, run_id: int) -> BenchmarkResult:
        text = test_input["text"]
        out_file = OUTPUT_DIR / f"{self.provider}_{test_input['id']}_run{run_id}.mp3"

        start = time.perf_counter()
        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice="alloy",
            input=text,
            response_format="mp3",
        ) as response:
            response.stream_to_file(str(out_file))
        total_ms = elapsed_ms(start)

        cost = estimate_tts_cost_usd(len(text), RATE_PER_MILLION_CHARS)

        return BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input["id"],
            run_id=run_id,
            latency_ms=total_ms,
            input_size=len(text),
            output_size=out_file.stat().st_size,
            input_unit="chars",
            output_unit="bytes",
            cost_usd=cost,
            output_preview=str(out_file.name),
        )


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="tts", factory=OpenAITTSBenchmark, test_inputs=TTS_TEXTS)
