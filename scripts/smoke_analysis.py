"""Smoke del pipeline de análisis para CI (fixtures en tests/fixtures/results)."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.pipeline_steps import SMOKE_ANALYSIS_STEPS
FIXTURE_RESULTS = ROOT / "tests" / "fixtures" / "results"


def _patch_paths() -> dict[str, str]:
    """Variables de entorno para redirigir results/docs sin tocar el repo."""
    tmp = ROOT / ".pytest_smoke_work"
    if tmp.exists():
        shutil.rmtree(tmp)
    results = tmp / "results"
    docs = tmp / "docs"
    shutil.copytree(FIXTURE_RESULTS, results)
    shutil.copytree(ROOT / "docs", docs)
    return {
        "BENCHMARK_RESULTS_DIR": str(results),
        "BENCHMARK_DOCS_DIR": str(docs),
        "BENCHMARK_PROJECT_ROOT": str(tmp),
    }


def main() -> int:
    env = {**os.environ, **_patch_paths()}
    py = sys.executable
    for mod in SMOKE_ANALYSIS_STEPS:
        proc = subprocess.run([py, "-m", mod], cwd=ROOT, env=env)
        if proc.returncode != 0:
            print(f"[ERROR] falló {mod}")
            return proc.returncode
    print("OK smoke analysis")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
