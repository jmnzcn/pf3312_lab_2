"""Los 15 benchmarks del proyecto (run_all, E2E y validación)."""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Callable

from common.base import Benchmark


@dataclass(frozen=True)
class BenchmarkSpec:
    category: str
    provider: str
    module: str
    class_name: str
    log_label: str = ""

    @property
    def label(self) -> str:
        return self.log_label or self.provider

    def lazy_factory(self) -> Callable[[], Benchmark]:
        module_path = self.module
        class_name = self.class_name

        def _factory() -> Benchmark:
            mod = import_module(module_path)
            cls = getattr(mod, class_name)
            return cls()

        return _factory


BENCHMARK_REGISTRY: tuple[BenchmarkSpec, ...] = (
    BenchmarkSpec("llm", "openai", "benchmarks.llm.benchmark_openai", "OpenAIBenchmark"),
    BenchmarkSpec("llm", "anthropic", "benchmarks.llm.benchmark_anthropic", "AnthropicBenchmark"),
    BenchmarkSpec("llm", "google", "benchmarks.llm.benchmark_gemini", "GeminiBenchmark", log_label="gemini"),
    BenchmarkSpec("llm", "groq", "benchmarks.llm.benchmark_groq", "GroqBenchmark"),
    BenchmarkSpec("llm", "ollama", "benchmarks.llm.benchmark_ollama_local", "OllamaBenchmark"),
    BenchmarkSpec("stt", "deepgram", "benchmarks.stt.benchmark_deepgram", "DeepgramBenchmark"),
    BenchmarkSpec("stt", "openai", "benchmarks.stt.benchmark_openai_whisper", "OpenAIWhisperBenchmark", log_label="openai-whisper"),
    BenchmarkSpec("stt", "assemblyai", "benchmarks.stt.benchmark_assemblyai", "AssemblyAIBenchmark"),
    BenchmarkSpec("stt", "azure", "benchmarks.stt.benchmark_azure", "AzureSpeechBenchmark"),
    BenchmarkSpec("stt", "faster-whisper", "benchmarks.stt.benchmark_faster_whisper_local", "FasterWhisperBenchmark"),
    BenchmarkSpec("tts", "openai", "benchmarks.tts.benchmark_openai_tts", "OpenAITTSBenchmark", log_label="openai-tts"),
    BenchmarkSpec("tts", "elevenlabs", "benchmarks.tts.benchmark_elevenlabs", "ElevenLabsBenchmark"),
    BenchmarkSpec("tts", "azure", "benchmarks.tts.benchmark_azure_tts", "AzureTTSBenchmark", log_label="azure-tts"),
    BenchmarkSpec("tts", "google", "benchmarks.tts.benchmark_google_tts", "GoogleTTSBenchmark", log_label="google-tts"),
    BenchmarkSpec("tts", "piper", "benchmarks.tts.benchmark_piper_local", "PiperBenchmark"),
)


def category_specs(category: str) -> list[BenchmarkSpec]:
    return [s for s in BENCHMARK_REGISTRY if s.category == category]


def providers_for_category(category: str) -> list[str]:
    return [s.provider for s in category_specs(category)]


def factory_pairs(category: str) -> list[tuple[str, Callable[[], Benchmark]]]:
    return [(s.label, s.lazy_factory()) for s in category_specs(category)]


def factory_by_provider(category: str) -> dict[str, Callable[[], Benchmark]]:
    return {s.provider: s.lazy_factory() for s in category_specs(category)}
