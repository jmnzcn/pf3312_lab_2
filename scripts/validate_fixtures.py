"""Valida fixtures mínimos de results/ (CI, sin corrida de benchmarks)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_RESULTS = ROOT / "tests" / "fixtures" / "results"
sys.path.insert(0, str(ROOT))

os.environ["BENCHMARK_RESULTS_DIR"] = str(FIXTURE_RESULTS)
os.environ["BENCHMARK_PROJECT_ROOT"] = str(ROOT)

from scripts.validate_results import validate_all  # noqa: E402


def main() -> int:
    errors, infos = validate_all()
    for msg in infos:
        print(msg)
    for msg in errors:
        print(f"[ERROR] {msg}")
    if errors:
        print(f"\nValidación fixtures FALLÓ · {len(errors)} error(es)")
        return 1
    print(f"\nOK validación fixtures · {len(infos)} aviso(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
