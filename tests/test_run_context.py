import json

import common.run_context as rc


def _reset_batch_state(tmp_path, monkeypatch):
    monkeypatch.setenv("BENCHMARK_RESULTS_DIR", str(tmp_path))
    monkeypatch.setattr(rc, "_current_batch_id", None)


def _manifest_file(tmp_path):
    return tmp_path / "run_manifest.json"


def test_start_run_batch_reuses_active_batch(tmp_path, monkeypatch):
    _reset_batch_state(tmp_path, monkeypatch)
    first = rc.start_run_batch(runs_per_input=5, note="full pipeline")
    second = rc.start_run_batch(runs_per_input=5, note="llm run_all")
    assert first == second
    manifest = json.loads(_manifest_file(tmp_path).read_text(encoding="utf-8"))
    assert manifest["note"] == "full pipeline"


def test_start_run_batch_force_creates_new_id(tmp_path, monkeypatch):
    _reset_batch_state(tmp_path, monkeypatch)
    monkeypatch.setattr(rc, "_current_batch_id", "2026-01-01T00:00:00Z")
    second = rc.start_run_batch(note="b", force=True)
    assert second != "2026-01-01T00:00:00Z"


def test_ensure_run_batch_reuses_existing(tmp_path, monkeypatch):
    _reset_batch_state(tmp_path, monkeypatch)
    parent = rc.start_run_batch(runs_per_input=5, note="full pipeline")
    child = rc.ensure_run_batch(note="stt run_all")
    assert parent == child
    manifest = json.loads(_manifest_file(tmp_path).read_text(encoding="utf-8"))
    assert manifest["note"] == "stt run_all"
    assert manifest["runs_per_input"] == 5


def test_e2e_does_not_overwrite_runs_per_input(tmp_path, monkeypatch):
    _reset_batch_state(tmp_path, monkeypatch)
    rc.start_run_batch(runs_per_input=5, note="full pipeline")
    rc.ensure_run_batch(runs_per_input=3, note="e2e pipeline")
    manifest = json.loads(_manifest_file(tmp_path).read_text(encoding="utf-8"))
    assert manifest["runs_per_input"] == 5
    assert manifest["note"] == "e2e pipeline"
