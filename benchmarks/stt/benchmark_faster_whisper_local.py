"""Benchmark STT local con faster-whisper.

Requisitos:
    - GPU NVIDIA con CUDA (opcional pero muy recomendado).
    - El primer run descarga el modelo desde HuggingFace y lo cachea.

Tip 4 GB VRAM:
    - large-v3 con compute_type=int8_float16 → cabe ajustado (~3 GB).
    - Si se queda sin memoria, bajar a medium o usar compute_type=int8.
"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from faster_whisper import WhisperModel

from common.audio_samples import AudioSample, load_audio_samples
from common.base import Benchmark, BenchmarkResult
from common.metrics import compute_wer, elapsed_ms


load_dotenv()


class FasterWhisperBenchmark(Benchmark):
    category = "stt"
    provider = "faster-whisper"
    deployment = "local"

    def __init__(self) -> None:
        self.model = os.getenv("FASTER_WHISPER_MODEL", "large-v3")
        compute_type = os.getenv("FASTER_WHISPER_COMPUTE_TYPE", "int8_float16")
        device = "cuda"
        try:
            self.whisper = WhisperModel(self.model, device=device, compute_type=compute_type)
            self.device = device
            print(f"[INFO] faster-whisper en {device} ({self.model}, {compute_type})")
        except Exception as exc:
            self.whisper = WhisperModel(self.model, device="cpu", compute_type="int8")
            self.device = "cpu"
            print(f"[WARN] faster-whisper fallback CPU: {exc}")

    def run_single(self, test_input: AudioSample, run_id: int) -> BenchmarkResult:
        if not test_input.exists():
            raise FileNotFoundError(f"Audio no encontrado: {test_input.path}")
        duration = test_input.load_duration()

        start = time.perf_counter()
        segments, info = self.whisper.transcribe(
            str(test_input.path),
            language="es",
            beam_size=5,
            vad_filter=True,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        total_ms = elapsed_ms(start)

        wer = compute_wer(test_input.reference_text, text)

        return BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input.id,
            run_id=run_id,
            notes=f"device={self.device}",
            latency_ms=total_ms,
            input_size=int(duration * 100),
            output_size=len(text),
            input_unit="seconds_x100",
            output_unit="chars",
            cost_usd=0.0,
            quality_metric=wer,
            quality_metric_name="WER",
            output_preview=text[:200],
        )


if __name__ == "__main__":
    from common.cli import load_stt_samples_or_exit, run_benchmark_main

    run_benchmark_main(
        category="stt",
        factory=FasterWhisperBenchmark,
        test_inputs_factory=load_stt_samples_or_exit,
    )
