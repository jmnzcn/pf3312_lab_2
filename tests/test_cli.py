import json
import sys
from pathlib import Path

import pytest

import common.run_context as rc
from common.base import Benchmark, BenchmarkResult
from common.cli import load_stt_samples_or_exit, run_benchmark_main


class _FakeBench(Benchmark):
    category = "llm"
    provider = "fake"
    model = "fake-model"
    deployment = "cloud"

    def run_single(self, test_input: dict, run_id: int) -> BenchmarkResult:
        return BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            test_id=test_input["id"],
            run_id=run_id,
            latency_ms=1.0,
            output_text=f'{{"agentes":[{{"nombre":"A","estilo":"realista","rol":"x","expresiones":["a"]}},{{"nombre":"B","estilo":"cartoon","rol":"y","expresiones":["b"]}},{{"nombre":"C","estilo":"caricaturesco","rol":"z","expresiones":["c"]}}]}}',
            output_preview="preview",
        )


def test_run_benchmark_main_writes_raw_with_output_text(tmp_path, monkeypatch):
    monkeypatch.setattr(rc, "MANIFEST_PATH", tmp_path / "run_manifest.json")
    monkeypatch.setattr(rc, "_current_batch_id", None)
    results_dir = tmp_path / "results"
    raw_dir = results_dir / "raw"
    monkeypatch.setattr("common.results.RESULTS_DIR", results_dir)
    monkeypatch.setattr("common.results.RAW_DIR", raw_dir)

    run_benchmark_main(
        category="llm",
        factory=_FakeBench,
        test_inputs=[{"id": "p3_json_estricto"}],
        argv=["test", "1"],
    )

    raw = json.loads((raw_dir / "llm_fake.json").read_text(encoding="utf-8"))
    assert raw[0]["output_text"]
    assert "agentes" in raw[0]["output_text"]


def test_load_stt_samples_or_exit_when_empty(monkeypatch):
    monkeypatch.setattr("common.audio_samples.load_audio_samples", lambda: [])
    with pytest.raises(SystemExit) as exc:
        load_stt_samples_or_exit()
    assert exc.value.code == 0
