"""Benchmark OpenAI Whisper API (whisper-1)."""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from common.audio_samples import AudioSample, load_audio_samples
from common.base import Benchmark, BenchmarkResult
from common.metrics import compute_wer, elapsed_ms, estimate_stt_cost_usd


load_dotenv()

RATE_PER_MINUTE = 0.006  # USD/min (whisper-1)


class OpenAIWhisperBenchmark(Benchmark):
    category = "stt"
    provider = "openai"
    model = "whisper-1"
    deployment = "cloud"

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta OPENAI_API_KEY en .env")
        self.client = OpenAI(api_key=api_key)

    def run_single(self, test_input: AudioSample, run_id: int) -> BenchmarkResult:
        if not test_input.exists():
            raise FileNotFoundError(f"Audio no encontrado: {test_input.path}")
        duration = test_input.load_duration()

        start = time.perf_counter()
        with test_input.path.open("rb") as fh:
            transcription = self.client.audio.transcriptions.create(
                model=self.model,
                file=fh,
                language="es",
                response_format="text",
            )
        total_ms = elapsed_ms(start)
        text = transcription if isinstance(transcription, str) else getattr(transcription, "text", "")

        wer = compute_wer(test_input.reference_text, text)
        cost = estimate_stt_cost_usd(duration, RATE_PER_MINUTE)

        return BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input.id,
            run_id=run_id,
            latency_ms=total_ms,
            input_size=int(duration * 100),
            output_size=len(text),
            input_unit="seconds_x100",
            output_unit="chars",
            cost_usd=cost,
            quality_metric=wer,
            quality_metric_name="WER",
            output_preview=text[:200],
        )


if __name__ == "__main__":
    from common.cli import load_stt_samples_or_exit, run_benchmark_main

    run_benchmark_main(
        category="stt",
        factory=OpenAIWhisperBenchmark,
        test_inputs_factory=load_stt_samples_or_exit,
    )
