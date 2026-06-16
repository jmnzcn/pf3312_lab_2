"""Google Cloud TTS (Neural2 / WaveNet). Requiere GOOGLE_APPLICATION_CREDENTIALS."""
from __future__ import annotations

import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import texttospeech

from common.audio_samples import TTS_TEXTS
from common.base import Benchmark, BenchmarkResult
from common.benchmark_errors import mark_tts_output
from common.metrics import elapsed_ms, estimate_tts_cost_usd


load_dotenv()

# Neural2 standard: 16 USD/M chars (verificar precio actual).
from common.rates import GOOGLE_TTS_USD_PER_M_CHARS

RATE_PER_MILLION_CHARS = GOOGLE_TTS_USD_PER_M_CHARS
LANGUAGE_CODE = "es-ES"
VOICE_NAME = "es-ES-Neural2-A"

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "tts_outputs"


class GoogleTTSBenchmark(Benchmark):
    category = "tts"
    provider = "google"
    model = VOICE_NAME
    deployment = "cloud"

    def __init__(self) -> None:
        creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds:
            raise RuntimeError(
                "Falta GOOGLE_APPLICATION_CREDENTIALS en .env (ruta al JSON de GCP)."
            )
        self.client = texttospeech.TextToSpeechClient()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def run_single(self, test_input: dict, run_id: int) -> BenchmarkResult:
        text = test_input["text"]
        out_file = OUTPUT_DIR / f"{self.provider}_{test_input['id']}_run{run_id}.mp3"

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=LANGUAGE_CODE,
            name=VOICE_NAME,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
        )

        start = time.perf_counter()
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        total_ms = elapsed_ms(start)

        out_file.write_bytes(response.audio_content)
        cost = estimate_tts_cost_usd(len(text), RATE_PER_MILLION_CHARS)

        result = BenchmarkResult(
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
        return mark_tts_output(result, out_file)


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="tts", factory=GoogleTTSBenchmark, test_inputs=TTS_TEXTS)
