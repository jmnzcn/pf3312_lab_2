"""Benchmark AssemblyAI (Universal-3 Pro + fallback Universal-2)."""
from __future__ import annotations

import os
import time

import assemblyai as aai
from dotenv import load_dotenv

from common.audio_samples import AudioSample, load_audio_samples
from common.base import Benchmark, BenchmarkResult
from common.metrics import compute_wer, elapsed_ms, estimate_stt_cost_usd


load_dotenv()

RATE_PER_MINUTE = 0.0036  # AssemblyAI Best model (verificar en assemblyai.com/pricing)


class AssemblyAIBenchmark(Benchmark):
    category = "stt"
    provider = "assemblyai"
    model = "universal-3-pro"
    deployment = "cloud"

    def __init__(self) -> None:
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta ASSEMBLYAI_API_KEY en .env")
        aai.settings.api_key = api_key
        self.config = aai.TranscriptionConfig(
            language_code="es",
            speech_models=["universal-3-pro", "universal-2"],
        )

    def run_single(self, test_input: AudioSample, run_id: int) -> BenchmarkResult:
        if not test_input.exists():
            raise FileNotFoundError(f"Audio no encontrado: {test_input.path}")
        duration = test_input.load_duration()

        transcriber = aai.Transcriber()

        start = time.perf_counter()
        transcript = transcriber.transcribe(str(test_input.path), config=self.config)
        total_ms = elapsed_ms(start)

        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"AssemblyAI error: {transcript.error}")
        text = transcript.text or ""

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
        factory=AssemblyAIBenchmark,
        test_inputs_factory=load_stt_samples_or_exit,
    )
