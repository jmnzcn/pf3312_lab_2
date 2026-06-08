"""Regenera tablas, gráficos, dimensiones, calidad LLM e integra informe."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STEPS = [
    "scripts.render_pipeline",
    "analysis.generate_tables",
    "analysis.generate_charts",
    "analysis.generate_six_dimensions",
    "analysis.generate_local_resources",
    "analysis.generate_pipeline_cost",
    "scripts.score_tts_inteligibilidad",
    "analysis.evaluate_llm_quality",
    "analysis.merge_informe",
]


def _run_step(py: str, mod: str, root: Path) -> None:
    if mod.startswith("scripts."):
        script = root / "scripts" / f"{mod.split('.', 1)[1]}.py"
        subprocess.run([py, str(script)], cwd=root, check=True)
    else:
        subprocess.run([py, "-m", mod], cwd=root, check=True)


def main() -> None:
    py = sys.executable
    for mod in STEPS:
        print(f"\n--- python -m {mod} ---")
        _run_step(py, mod, ROOT)
    print("\nOK pipeline de análisis completo.")


if __name__ == "__main__":
    main()
