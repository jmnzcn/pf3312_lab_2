"""Agrega tablas y gráficos a partir de los CSV de results/."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.pipeline_steps import FULL_ANALYSIS_STEPS, OPTIONAL_STEPS

STEPS = FULL_ANALYSIS_STEPS


def _run_step(
    py: str,
    mod: str,
    root: Path,
    *,
    optional: bool,
    extra_args: list[str] | None = None,
) -> bool:
    extra_args = extra_args or []
    if mod.startswith("scripts."):
        script = root / "scripts" / f"{mod.split('.', 1)[1]}.py"
        proc = subprocess.run([py, str(script), *extra_args], cwd=root)
    else:
        proc = subprocess.run([py, "-m", mod, *extra_args], cwd=root)
    if proc.returncode == 0:
        return True
    if optional:
        print(f"[WARN] Paso opcional omitido ({mod}), código {proc.returncode}")
        return False
    raise subprocess.CalledProcessError(proc.returncode, proc.args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de análisis sobre results/*.csv.")
    parser.add_argument(
        "--with-optional",
        action="store_true",
        help=(
            "Recalcula MOS de inteligibilidad TTS con Whisper en CPU "
            "(lento: ~225 audios). Sin este flag se reutiliza data/tts_mos_scores.json."
        ),
    )
    args = parser.parse_args()

    py = sys.executable
    for mod in STEPS:
        optional = mod in OPTIONAL_STEPS
        extra: list[str] = []
        if mod == "scripts.score_tts_inteligibilidad" and args.with_optional:
            extra = ["--force"]
        print(f"\n--- python -m {mod}" + (" (opcional)" if optional else "") + " ---")
        _run_step(py, mod, ROOT, optional=optional, extra_args=extra)
    print("\nOK pipeline de análisis completo.")


if __name__ == "__main__":
    main()
