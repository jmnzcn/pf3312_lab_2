"""Ejecuta todos los benchmarks de TTS disponibles."""

from __future__ import annotations



import sys



from common.audio_samples import TTS_TEXTS

from common.runner import run_category_benchmarks

from common.run_context import ensure_run_batch





def main(runs: int = 5) -> None:

    from benchmarks.tts.benchmark_azure_tts import AzureTTSBenchmark

    from benchmarks.tts.benchmark_elevenlabs import ElevenLabsBenchmark

    from benchmarks.tts.benchmark_google_tts import GoogleTTSBenchmark

    from benchmarks.tts.benchmark_openai_tts import OpenAITTSBenchmark

    from benchmarks.tts.benchmark_piper_local import PiperBenchmark



    ensure_run_batch(runs_per_input=runs, note="tts run_all")

    factories = [

        ("openai-tts", OpenAITTSBenchmark),

        ("elevenlabs", ElevenLabsBenchmark),

        ("azure-tts", AzureTTSBenchmark),

        ("google-tts", GoogleTTSBenchmark),

        ("piper", PiperBenchmark),

    ]

    run_category_benchmarks("tts", factories, TTS_TEXTS, runs=runs, input_label="textos", log_prefix=">>")





if __name__ == "__main__":

    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    main(runs=runs)


