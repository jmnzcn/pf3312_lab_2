"""Smoke del pipeline de análisis con fixtures mínimos (sin corrida de benchmarks)."""
from __future__ import annotations

import importlib
import os
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_RESULTS = Path(__file__).parent / "fixtures" / "results"

from analysis.pipeline_steps import SMOKE_ANALYSIS_STEPS

ANALYSIS_MODULES = list(SMOKE_ANALYSIS_STEPS)


@pytest.fixture
def fixture_results_env(tmp_path, monkeypatch):
    results = tmp_path / "results"
    docs = tmp_path / "docs"
    shutil.copytree(FIXTURE_RESULTS, results)
    shutil.copytree(ROOT / "docs", docs)

    monkeypatch.setenv("BENCHMARK_RESULTS_DIR", str(results))
    monkeypatch.setenv("BENCHMARK_DOCS_DIR", str(docs))
    monkeypatch.setenv("BENCHMARK_PROJECT_ROOT", str(tmp_path))

    return tmp_path


def test_analysis_modules_import():
    for mod_name in ANALYSIS_MODULES:
        importlib.import_module(mod_name)


def test_generate_six_dimensions_smoke(fixture_results_env, tmp_path):
    import analysis.generate_six_dimensions as gsd

    importlib.reload(gsd)
    gsd.main()
    out = Path(os.environ["BENCHMARK_DOCS_DIR"]) / "dimensiones_datos" / "matriz_6_dimensiones.md"
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "llm/" in text
    assert "tts_outputs" not in text
