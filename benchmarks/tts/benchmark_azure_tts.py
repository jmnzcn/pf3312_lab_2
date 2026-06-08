"""Benchmark Azure Text-to-Speech Neural."""
from __future__ import annotations

import os
import time
from pathlib import Path

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from common.audio_samples import TTS_TEXTS
from common.base import Benchmark, BenchmarkResult
from common.metrics import elapsed_ms, estimate_tts_cost_usd


load_dotenv()

# Neural TTS standard: 16 USD/M chars (verificar precio actual).
RATE_PER_MILLION_CHARS = 16.0
VOICE_NAME = "es-CR-MariaNeural"  # Voz en español Costa Rica

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "tts_outputs"


class AzureTTSBenchmark(Benchmark):
    category = "tts"
    provider = "azure"
    model = VOICE_NAME
    deployment = "cloud"

    def __init__(self) -> None:
        key = os.getenv("AZURE_SPEECH_KEY")
        region = os.getenv("AZURE_SPEECH_REGION", "westus")
        if not key:
            raise RuntimeError("Falta AZURE_SPEECH_KEY en .env")
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        self.speech_config.speech_synthesis_voice_name = VOICE_NAME
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio24Khz48KBitRateMonoMp3
        )
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def run_single(self, test_input: dict, run_id: int) -> BenchmarkResult:
        text = test_input["text"]
        out_file = OUTPUT_DIR / f"{self.provider}_{test_input['id']}_run{run_id}.mp3"

        audio_output = speechsdk.audio.AudioOutputConfig(filename=str(out_file))
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_output,
        )

        start = time.perf_counter()
        result = synthesizer.speak_text_async(text).get()
        total_ms = elapsed_ms(start)

        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError(f"Azure TTS error: {result.reason}")

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

    run_benchmark_main(category="tts", factory=AzureTTSBenchmark, test_inputs=TTS_TEXTS)
