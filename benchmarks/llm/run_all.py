"""Ejecuta todos los benchmarks de LLM disponibles."""

from __future__ import annotations



import sys



from common.prompts import LLM_PROMPTS

from common.runner import run_category_benchmarks

from common.run_context import ensure_run_batch





def main(runs: int = 5) -> None:

    from benchmarks.llm.benchmark_anthropic import AnthropicBenchmark

    from benchmarks.llm.benchmark_gemini import GeminiBenchmark

    from benchmarks.llm.benchmark_groq import GroqBenchmark

    from benchmarks.llm.benchmark_ollama_local import OllamaBenchmark

    from benchmarks.llm.benchmark_openai import OpenAIBenchmark



    ensure_run_batch(runs_per_input=runs, note="llm run_all")

    factories = [

        ("openai", OpenAIBenchmark),

        ("anthropic", AnthropicBenchmark),

        ("gemini", GeminiBenchmark),

        ("groq", GroqBenchmark),

        ("ollama", OllamaBenchmark),

    ]

    run_category_benchmarks("llm", factories, LLM_PROMPTS, runs=runs, input_label="prompts")





if __name__ == "__main__":

    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5

    main(runs=runs)


