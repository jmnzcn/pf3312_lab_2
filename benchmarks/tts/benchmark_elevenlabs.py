"""Benchmark ElevenLabs Multilingual v2.

Voz por defecto: Rachel (multilingual). Cambiar VOICE_ID si querés otra.
Precios: https://elevenlabs.io/pricing
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

from common.audio_samples import TTS_TEXTS
from common.base import Benchmark, BenchmarkResult
from common.metrics import elapsed_ms, estimate_tts_cost_usd


load_dotenv()

# Tier "Creator": 0.30 USD por 1000 chars ~ 300 USD/M chars (verificar precio actual).
RATE_PER_MILLION_CHARS = 300.0
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel (multilingual)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "tts_outputs"


class ElevenLabsBenchmark(Benchmark):
    category = "tts"
    provider = "elevenlabs"
    model = "eleven_multilingual_v2"
    deployment = "cloud"

    def __init__(self) -> None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("Falta ELEVENLABS_API_KEY en .env")
        self.client = ElevenLabs(api_key=api_key)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def run_single(self, test_input: dict, run_id: int) -> BenchmarkResult:
        text = test_input["text"]
        out_file = OUTPUT_DIR / f"{self.provider}_{test_input['id']}_run{run_id}.mp3"

        start = time.perf_counter()
        audio_stream = self.client.text_to_speech.convert(
            voice_id=VOICE_ID,
            model_id=self.model,
            text=text,
            output_format="mp3_44100_128",
        )
        with out_file.open("wb") as fh:
            for chunk in audio_stream:
                if chunk:
                    fh.write(chunk)
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

    run_benchmark_main(category="tts", factory=ElevenLabsBenchmark, test_inputs=TTS_TEXTS)
