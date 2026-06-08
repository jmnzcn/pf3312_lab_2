"""Ejecuta los tres runners (LLM + STT + TTS) en secuencia."""
from __future__ import annotations

import sys

from benchmarks.llm import run_all as llm_runner
from benchmarks.stt import run_all as stt_runner
from benchmarks.tts import run_all as tts_runner
from common.run_context import ensure_run_batch


def main(runs: int = 5) -> None:
    ensure_run_batch(runs_per_input=runs, note="full pipeline")
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(root / "scripts" / "capture_hardware.py")], check=False)
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


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(runs=runs)
