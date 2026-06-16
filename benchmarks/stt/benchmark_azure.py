"""STT con Azure Speech."""
from __future__ import annotations

import os
import time

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

from common.audio_samples import AudioSample, load_audio_samples
from common.azure_speech import cancellation_message, speech_result_error
from common.base import Benchmark, BenchmarkResult, stt_output_fields
from common.benchmark_errors import mark_empty_stt
from common.metrics import compute_wer, elapsed_ms, estimate_stt_cost_usd


load_dotenv()

from common.rates import AZURE_STT_USD_PER_MIN

RATE_PER_MINUTE = AZURE_STT_USD_PER_MIN


class AzureSpeechBenchmark(Benchmark):
    category = "stt"
    provider = "azure"
    model = "speech-recognition-standard"
    deployment = "cloud"

    def __init__(self) -> None:
        key = os.getenv("AZURE_SPEECH_KEY")
        region = os.getenv("AZURE_SPEECH_REGION", "westus")
        if not key:
            raise RuntimeError("Falta AZURE_SPEECH_KEY en .env")
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        self.speech_config.speech_recognition_language = os.getenv(
            "AZURE_SPEECH_LANGUAGE", "es-CR"
        )

    def run_single(self, test_input: AudioSample, run_id: int) -> BenchmarkResult:
        if not test_input.exists():
            raise FileNotFoundError(f"Audio no encontrado: {test_input.path}")
        duration = test_input.load_duration()

        audio_config = speechsdk.AudioConfig(filename=str(test_input.path))
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
        )

        results_text: list[str] = []
        done = {"v": False}
        cancel_info: dict[str, str] = {}

        def stopped(_evt):
            done["v"] = True

        def recognized(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                results_text.append(evt.result.text)

        def canceled(evt):
            cancel_info["msg"] = cancellation_message(
                evt.result, prefix="Azure STT canceled"
            )
            done["v"] = True

        recognizer.recognized.connect(recognized)
        recognizer.session_stopped.connect(stopped)
        recognizer.canceled.connect(canceled)

        start = time.perf_counter()
        max_wait = max(120.0, duration * 3.0 + 30.0)
        deadline = time.perf_counter() + max_wait
        recognizer.start_continuous_recognition()
        while not done["v"]:
            if time.perf_counter() > deadline:
                recognizer.stop_continuous_recognition()
                raise TimeoutError(
                    f"Azure STT sin respuesta tras {max_wait:.0f}s "
                    f"(audio {duration:.1f}s)"
                )
            time.sleep(0.05)
        recognizer.stop_continuous_recognition()
        total_ms = elapsed_ms(start)

        text = " ".join(results_text).strip()
        wer = compute_wer(test_input.reference_text, text) if text else None
        cost = estimate_stt_cost_usd(duration, RATE_PER_MINUTE)

        detail = cancel_info.get("msg", "sesión finalizada sin RecognizedSpeech")
        result = BenchmarkResult(
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
            **stt_output_fields(text),
            notes=detail if not text else "",
        )
        return mark_empty_stt(result, text, detail=detail)


if __name__ == "__main__":
    from common.cli import load_stt_samples_or_exit, run_benchmark_main

    run_benchmark_main(
        category="stt",
        factory=AzureSpeechBenchmark,
        test_inputs_factory=load_stt_samples_or_exit,
    )
