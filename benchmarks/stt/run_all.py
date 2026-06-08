"""Ejecuta todos los benchmarks de STT disponibles."""

from __future__ import annotations



import sys



from common.audio_samples import load_audio_samples

from common.runner import run_category_benchmarks

from common.run_context import ensure_run_batch





def main(runs: int = 5) -> None:

    from benchmarks.stt.benchmark_assemblyai import AssemblyAIBenchmark

    from benchmarks.stt.benchmark_azure import AzureSpeechBenchmark

    from benchmarks.stt.benchmark_deepgram import DeepgramBenchmark

    from benchmarks.stt.benchmark_faster_whisper_local import FasterWhisperBenchmark

    from benchmarks.stt.benchmark_openai_whisper import OpenAIWhisperBenchmark



    samples = [s for s in load_audio_samples() if s.exists()]

    if not samples:

        print("[WARN] No hay audios en data/test_audio/. Ver data/test_audio/README.md")

        return



    ensure_run_batch(runs_per_input=runs, note="stt run_all")

    factories = [

        ("openai-whisper", OpenAIWhisperBenchmark),

        ("deepgram", DeepgramBenchmark),

        ("assemblyai", AssemblyAIBenchmark),

        ("azure", AzureSpeechBenchmark),

        ("faster-whisper", FasterWhisperBenchmark),

    ]

    run_category_benchmarks("stt", factories, samples, runs=runs, input_label="audios")





if __name__ == "__main__":

    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    main(runs=runs)


