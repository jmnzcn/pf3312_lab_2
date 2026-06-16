"""Rutas del proyecto (sobrescribibles vía env para tests/CI)."""
from __future__ import annotations

import os
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parent.parent


def project_root() -> Path:
    return Path(os.environ.get("BENCHMARK_PROJECT_ROOT", _PKG_ROOT))


def results_dir() -> Path:
    return Path(os.environ.get("BENCHMARK_RESULTS_DIR", project_root() / "results"))


def docs_dir() -> Path:
    return Path(os.environ.get("BENCHMARK_DOCS_DIR", project_root() / "docs"))


def manifest_path() -> Path:
    return results_dir() / "run_manifest.json"


def e2e_csv_path() -> Path:
    return results_dir() / "e2e_results.csv"


def results_raw_dir() -> Path:
    return results_dir() / "raw"
