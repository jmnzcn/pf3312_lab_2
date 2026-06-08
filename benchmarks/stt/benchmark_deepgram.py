"""Benchmark Deepgram Nova-3 (modelo más reciente al 2026).

SDK: deepgram-sdk >= 6.0 (API rediseñada respecto a 3.x/5.x).
"""
from __future__ import annotations

import os
import time

from deepgram import DeepgramClient
from dotenv import load_dotenv

from common.audio_samples import AudioSample, load_audio_samples
from common.base import Benchmark, BenchmarkResult
from common.metrics import compute_wer, elapsed_ms, estimate_stt_cost_usd


load_dotenv()

RATE_PER_MINUTE = 0.0043  # Nova-3 pre-recorded (verificar en deepgram.com/pricing)


class DeepgramBenchmark(Benchmark):
    category = "stt"
    provider = "deepgram"
    model = "nova-3"
    deployment = "cloud"

    def __init__(self) -> None:
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise RuntimeError("Falta DEEPGRAM_API_KEY en .env")
        self.client = DeepgramClient(api_key=api_key)

    def run_single(self, test_input: AudioSample, run_id: int) -> BenchmarkResult:
        if not test_input.exists():
            raise FileNotFoundError(f"Audio no encontrado: {test_input.path}")
        duration = test_input.load_duration()
        audio_bytes = test_input.path.read_bytes()

        start = time.perf_counter()
        response = self.client.listen.v1.media.transcribe_file(
            request=audio_bytes,
            model=self.model,
            language="es",
            smart_format=True,
            punctuate=True,
        )
        total_ms = elapsed_ms(start)
        text = response.results.channels[0].alternatives[0].transcript

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
        factory=DeepgramBenchmark,
        test_inputs_factory=load_stt_samples_or_exit,
    )
