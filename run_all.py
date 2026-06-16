"""Corre LLM, STT, TTS y el pipeline E2E en secuencia."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from benchmarks.llm import run_all as llm_runner
from benchmarks.pipeline import run_e2e as e2e_runner
from benchmarks.stt import run_all as stt_runner
from benchmarks.tts import run_all as tts_runner
from common.run_context import start_run_batch

ROOT = Path(__file__).resolve().parent


def main(runs: int = 5, *, skip_e2e: bool = False) -> None:
    start_run_batch(runs_per_input=runs, note="full pipeline", force=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "capture_hardware.py")], check=False)
    print("=" * 60)
    print(f"LLM benchmarks ({runs} runs por prompt)")
    print("=" * 60)
    llm_runner.main(runs=runs)

    print("\n" + "=" * 60)
    print(f"STT benchmarks ({runs} runs por audio)")
    print("=" * 60)
    stt_runner.main(runs=runs)

    print("\n" + "=" * 60)
    print(f"TTS benchmarks ({runs} runs por texto)")
    print("=" * 60)
    tts_runner.main(runs=runs)

    if skip_e2e:
        print("\n[SKIP] Pipeline E2E (--skip-e2e)")
        return

    print("\n" + "=" * 60)
    print(f"Pipeline E2E ({runs} runs por audio × escenario)")
    print("=" * 60)
    e2e_runner.main(runs=runs, new_batch=False)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark completo LLM + STT + TTS + E2E")
    parser.add_argument("runs", nargs="?", type=int, default=5, help="repeticiones por input (default 5)")
    parser.add_argument(
        "--skip-e2e",
        action="store_true",
        help="omitir pipeline end-to-end (solo benchmarks por categoría)",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    main(runs=args.runs, skip_e2e=args.skip_e2e)
