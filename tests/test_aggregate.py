import pandas as pd

from analysis.aggregate import filter_latest_batch, stt_wer_by_source


def test_filter_latest_batch_by_run_batch_id():
    df = pd.DataFrame(
        [
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-01-01T00:00:00Z", "error": "", "latency_ms": 1, "category": "llm", "timestamp": "2026-01-01T00:00:00Z"},
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 2, "category": "llm", "timestamp": "2026-06-08T00:00:00Z"},
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 3, "category": "llm", "timestamp": "2026-06-08T00:00:01Z"},
        ]
    )
    out = filter_latest_batch(df)
    assert (out["run_batch_id"] == "2026-06-08T00:00:00Z").all()
    assert len(out) == 2


def test_stt_wer_by_source_groups_samples():
    df = pd.DataFrame(
        [
            {"provider": "deepgram", "test_id": "a1_saludo_corto", "quality_metric": 0.10},
            {"provider": "deepgram", "test_id": "g1_fleurs", "quality_metric": 0.02},
        ]
    )
    out = stt_wer_by_source(df)
    sources = set(out["audio_source"])
    assert "synthetic_piper" in sources
    assert "fleurs_human" in sources
    deepgram = out[out["provider"] == "deepgram"]
    assert len(deepgram) == 2


def test_filter_latest_batch_by_model():
    df = pd.DataFrame(
        [
            {"provider": "anthropic", "model": "old", "timestamp": "2026-01-01T00:00:00Z", "error": "x", "latency_ms": 1, "category": "llm"},
            {"provider": "anthropic", "model": "new", "timestamp": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 2, "category": "llm", "test_id": "p1", "run_id": 1},
            {"provider": "anthropic", "model": "new", "timestamp": "2026-06-08T00:00:01Z", "error": "", "latency_ms": 3, "category": "llm", "test_id": "p1", "run_id": 2},
        ]
    )
    out = filter_latest_batch(df)
    assert (out["model"] == "new").all()
    assert len(out) == 2
