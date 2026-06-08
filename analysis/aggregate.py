"""Carga y agregación de CSV con filtro de última corrida/modelo."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from common.run_context import load_manifest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"


def _success_mask(df: pd.DataFrame) -> pd.Series:
    if "error" not in df.columns:
        return pd.Series(True, index=df.index)
    return df["error"].isna() | (df["error"] == "")


def filter_latest_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Conserva la corrida más reciente; tolera CSV legacy sin run_batch_id."""
    if df.empty:
        return df
    df = df.copy()
    ok = df[_success_mask(df)]
    if ok.empty:
        return ok

    if "run_batch_id" in ok.columns and ok["run_batch_id"].astype(str).str.len().gt(0).any():
        bid = ok["run_batch_id"].astype(str).max()
        return ok[ok["run_batch_id"].astype(str) == bid]

    ok["ts"] = pd.to_datetime(ok["timestamp"], utc=True, errors="coerce")
    chunks: list[pd.DataFrame] = []
    for provider, grp in ok.groupby("provider"):
        models = grp.groupby("model")["ts"].max()
        best_model = models.idxmax()
        sub = grp[grp["model"] == best_model].sort_values("ts")
        # Heurística: último bloque de corridas (máx. 5 inputs × 5 runs = 25; STT 10×5=50)
        tail_n = 50 if grp["category"].iloc[0] == "stt" else 25
        chunks.append(sub.tail(tail_n))
    return pd.concat(chunks, ignore_index=True) if chunks else ok


def load_category_df(category: str, *, latest_only: bool = True) -> pd.DataFrame:
    path = RESULTS_DIR / f"{category}_results.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = df[_success_mask(df)]
    if latest_only:
        df = filter_latest_batch(df)
    if not df.empty:
        df["servicio"] = df["category"] + "/" + df["provider"]
    return df


def aggregate_category(df: pd.DataFrame, category: str) -> pd.DataFrame:
    if df.empty:
        return df
    agg = (
        df.groupby(["provider", "model", "deployment"])
        .agg(
            llamadas=("latency_ms", "count"),
            latencia_ms_prom=("latency_ms", "mean"),
            latencia_ms_std=("latency_ms", "std"),
            latencia_ms_p95=("latency_ms", lambda s: s.quantile(0.95)),
            ttft_ms_prom=("ttft_ms", "mean"),
            costo_usd_prom=("cost_usd", "mean"),
            calidad_prom=("quality_metric", "mean"),
        )
        .reset_index()
    )
    agg["categoria"] = category
    if category != "llm":
        agg = agg.drop(columns=["ttft_ms_prom"], errors="ignore")
    if category != "stt":
        agg = agg.drop(columns=["calidad_prom"], errors="ignore")
    return agg


def stt_source_map() -> dict[str, str]:
    import json

    if not REFERENCE_FILE.exists():
        return {}
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    return {s["id"]: s.get("source", "unknown") for s in data.get("samples", [])}


def stt_wer_by_source(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "test_id" not in df.columns:
        return pd.DataFrame()
    src_map = stt_source_map()
    df = df.copy()
    df["audio_source"] = df["test_id"].map(src_map).fillna("unknown")
    return (
        df.groupby(["provider", "audio_source"])
        .agg(wer_prom=("quality_metric", "mean"), llamadas=("quality_metric", "count"))
        .reset_index()
        .round(4)
    )


def build_category_matrix_5x6(category: str, master: pd.DataFrame) -> pd.DataFrame:
    """5 proveedores × 6 dimensiones para una categoría."""
    sub = master[master["categoria"] == category].copy()
    if sub.empty:
        return sub
    cols = [
        "proveedor",
        "latencia_ms",
        "ttft_ms",
        "wer",
        "costo_usd",
        "privacidad_1_5",
        "customizacion_1_5",
        "integracion_1_5",
        "precision_resumen",
    ]
    present = [c for c in cols if c in sub.columns]
    return sub[present]


def analysis_meta_line() -> str:
    m = load_manifest()
    if not m:
        return "*Análisis sin manifiesto de corrida (CSV legacy filtrado por heurística).*"
    return (
        f"*Corrida: `{m.get('run_batch_id', 'n/d')}` · "
        f"runs/input: {m.get('runs_per_input', 'n/d')} · "
        f"Python {m.get('python', 'n/d')}*"
    )
