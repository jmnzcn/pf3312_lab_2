import pandas as pd

from analysis.aggregate import filter_latest_batch, stt_sample_count, stt_wer_by_source
from common.benchmark_config import category_row_count


def test_stt_sample_count_reads_catalog():
    assert stt_sample_count() == 14


def test_filter_latest_batch_tail_uses_dynamic_stt_count():
    n = category_row_count("stt")
    rows = []
    for i in range(n + 3):
        rows.append(
            {
                "provider": "deepgram",
                "model": "nova",
                "timestamp": f"2026-06-08T00:00:{i:02d}Z",
                "error": "",
                "latency_ms": i,
                "category": "stt",
                "test_id": f"t{i % 14}",
                "run_id": (i % 5) + 1,
            }
        )
    out = filter_latest_batch(pd.DataFrame(rows))
    assert len(out) == n


def test_filter_latest_batch_by_run_batch_id():
    df = pd.DataFrame(
        [
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-01-01T00:00:00Z", "error": "", "latency_ms": 1, "category": "llm", "timestamp": "2026-01-01T00:00:00Z", "test_id": "p1", "run_id": 1},
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 2, "category": "llm", "timestamp": "2026-06-08T00:00:00Z", "test_id": "p1", "run_id": 1},
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 3, "category": "llm", "timestamp": "2026-06-08T00:00:01Z", "test_id": "p2", "run_id": 1},
        ]
    )
    out = filter_latest_batch(df)
    assert (out["run_batch_id"] == "2026-06-08T00:00:00Z").all()
    assert len(out) == 2


def test_filter_latest_batch_dedupes_rerun_same_key():
    df = pd.DataFrame(
        [
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 1, "category": "llm", "timestamp": "2026-06-08T00:00:00Z", "test_id": "p1", "run_id": 1},
            {"provider": "openai", "model": "m1", "run_batch_id": "2026-06-08T00:00:00Z", "error": "", "latency_ms": 99, "category": "llm", "timestamp": "2026-06-08T00:00:01Z", "test_id": "p1", "run_id": 1},
        ]
    )
    out = filter_latest_batch(df)
    assert len(out) == 1
    assert out.iloc[0]["latency_ms"] == 99


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
