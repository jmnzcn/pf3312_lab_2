import json

import pandas as pd

from analysis.aggregate import dedupe_run_rows, slice_latest_batch
from analysis.evaluate_llm_quality import _load_llm_outputs, _quality_reading_paragraph, evaluate_json_prompt
from scripts.validate_results import _duplicate_keys, validate_category


def test_dedupe_run_rows_keeps_latest():
    df = pd.DataFrame(
        [
            {"provider": "openai", "model": "m", "test_id": "p1", "run_id": 1, "timestamp": "2026-06-08T00:00:00Z", "error": ""},
            {"provider": "openai", "model": "m", "test_id": "p1", "run_id": 1, "timestamp": "2026-06-08T00:00:01Z", "error": ""},
        ]
    )
    out = dedupe_run_rows(df)
    assert len(out) == 1


def test_slice_latest_batch_detects_duplicates_before_dedupe():
    df = pd.DataFrame(
        [
            {"provider": "openai", "model": "m", "test_id": "p1", "run_id": 1, "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "timestamp": "2026-06-08T00:00:00Z", "category": "llm"},
            {"provider": "openai", "model": "m", "test_id": "p1", "run_id": 1, "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "timestamp": "2026-06-08T00:00:01Z", "category": "llm"},
        ]
    )
    raw = slice_latest_batch(df, dedupe=False)
    assert _duplicate_keys(raw, ["provider", "model", "test_id", "run_id"]) == 2


def test_load_llm_outputs_filters_by_manifest_batch(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    batch_a = "2026-06-08T00:00:00Z"
    batch_b = "2026-06-09T00:00:00Z"
    payload = [
        {"provider": "openai", "test_id": "p3_json_estricto", "run_batch_id": batch_a, "output_text": "{}", "error": None},
        {"provider": "groq", "test_id": "p3_json_estricto", "run_batch_id": batch_b, "output_text": "{}", "error": None},
    ]
    (raw_dir / "llm_openai.json").write_text(json.dumps([payload[0]]), encoding="utf-8")
    (raw_dir / "llm_groq.json").write_text(json.dumps([payload[1]]), encoding="utf-8")

    monkeypatch.setattr("analysis.evaluate_llm_quality.RAW_DIR", raw_dir)
    monkeypatch.setattr(
        "analysis.evaluate_llm_quality.load_manifest",
        lambda: {"run_batch_id": batch_a},
    )
    rows = _load_llm_outputs()
    assert len(rows) == 1
    assert rows[0]["provider"] == "openai"


def test_quality_reading_paragraph_is_dynamic():
    json_rows = [
        {"provider": "anthropic", "tasa_json": 1.0},
        {"provider": "ollama", "tasa_json": 0.4},
    ]
    notes = {"providers": [{"provider": "openai", "coherencia_1_5": 5}]}
    text = _quality_reading_paragraph(json_rows, notes)
    assert "anthropic" in text
    assert "ollama (40%)" in text
    assert "openai 5/5" in text
    assert "2/5" not in text
