"""Lee los CSV de results/ y se queda con la última corrida."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from common.benchmark_config import category_row_count, runs_per_input, stt_input_count
from common.paths import e2e_csv_path, project_root, results_dir
from common.run_context import load_manifest

PROJECT_ROOT = project_root()
RESULTS_DIR = results_dir()
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"


def _success_mask(df: pd.DataFrame) -> pd.Series:
    if "error" not in df.columns:
        return pd.Series(True, index=df.index)
    return df["error"].isna() | (df["error"] == "")


def stt_sample_count() -> int:
    return stt_input_count()


def filter_latest_batch(df: pd.DataFrame) -> pd.DataFrame:
    """Se queda con la corrida más reciente (tolera CSV viejos sin run_batch_id)."""
    if df.empty:
        return df
    df = df.copy()
    ok = df[_success_mask(df)]
    if ok.empty:
        return ok

    if "run_batch_id" in ok.columns and ok["run_batch_id"].astype(str).str.len().gt(0).any():
        bid = ok["run_batch_id"].astype(str).max()
        ok = ok[ok["run_batch_id"].astype(str) == bid]
        return dedupe_run_rows(ok)

    ok["ts"] = pd.to_datetime(ok["timestamp"], utc=True, errors="coerce")
    chunks: list[pd.DataFrame] = []
    for provider, grp in ok.groupby("provider"):
        models = grp.groupby("model")["ts"].max()
        best_model = models.idxmax()
        sub = grp[grp["model"] == best_model].sort_values("ts")
        cat = str(grp["category"].iloc[0])
        tail_n = category_row_count(cat)
        chunks.append(sub.tail(tail_n))
    merged = pd.concat(chunks, ignore_index=True) if chunks else ok
    return dedupe_run_rows(merged)


def dedupe_run_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Si se re-corrió sin reset, conserva la fila más reciente por (provider, model, test_id, run_id)."""
    if df.empty:
        return df
    out = df.copy()
    for col in ("test_id", "run_id"):
        if col not in out.columns:
            out[col] = ""
        out[col] = out[col].fillna("").astype(str)
    out["ts"] = pd.to_datetime(out.get("timestamp"), utc=True, errors="coerce")
    return (
        out.sort_values("ts")
        .drop_duplicates(subset=["provider", "model", "test_id", "run_id"], keep="last")
        .reset_index(drop=True)
    )


E2E_CSV = e2e_csv_path()


def load_e2e_df(*, latest_only: bool = True, dedupe: bool = True) -> pd.DataFrame:
    """Carga turnos E2E exitosos; opcionalmente último batch sin duplicados."""
    csv_path = e2e_csv_path()
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    ok = df[_success_mask(df)].copy()
    if ok.empty:
        return ok
    if latest_only and "run_batch_id" in ok.columns and ok["run_batch_id"].notna().any():
        bid = ok["run_batch_id"].astype(str).max()
        ok = ok[ok["run_batch_id"].astype(str) == bid]
    for col in (
        "stt_latency_ms",
        "llm_latency_ms",
        "tts_latency_ms",
        "overhead_ms",
        "total_latency_ms",
        "stt_cost_usd",
        "llm_cost_usd",
        "tts_cost_usd",
        "total_cost_usd",
    ):
        if col in ok.columns:
            ok[col] = pd.to_numeric(ok[col], errors="coerce")
    if latest_only and dedupe:
        for col in ("escenario", "test_id", "run_id"):
            if col not in ok.columns:
                ok[col] = ""
            ok[col] = ok[col].fillna("").astype(str)
        ok["ts"] = pd.to_datetime(ok.get("timestamp"), utc=True, errors="coerce")
        ok = (
            ok.sort_values("ts")
            .drop_duplicates(subset=["escenario", "test_id", "run_id"], keep="last")
            .reset_index(drop=True)
        )
    return ok


def load_e2e_batch_df(*, latest_only: bool = True, dedupe: bool = True) -> pd.DataFrame:
    """Todos los turnos E2E del último batch (incluye filas con error)."""
    csv_path = e2e_csv_path()
    if not csv_path.exists():
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    if df.empty:
        return df
    if latest_only and "run_batch_id" in df.columns and df["run_batch_id"].notna().any():
        bid = df["run_batch_id"].astype(str).max()
        df = df[df["run_batch_id"].astype(str) == bid].copy()
    if dedupe:
        for col in ("escenario", "test_id", "run_id"):
            if col not in df.columns:
                df[col] = ""
            df[col] = df[col].fillna("").astype(str)
        df["ts"] = pd.to_datetime(df.get("timestamp"), utc=True, errors="coerce")
        df = (
            df.sort_values("ts")
            .drop_duplicates(subset=["escenario", "test_id", "run_id"], keep="last")
            .reset_index(drop=True)
        )
    return df


def slice_latest_batch(df: pd.DataFrame, *, dedupe: bool = True) -> pd.DataFrame:
    """Filas exitosas del batch más reciente; opcionalmente sin deduplicar."""
    if df.empty:
        return df
    ok = df[_success_mask(df)].copy()
    if ok.empty:
        return ok
    if "run_batch_id" in ok.columns and ok["run_batch_id"].astype(str).str.len().gt(0).any():
        bid = ok["run_batch_id"].astype(str).max()
        ok = ok[ok["run_batch_id"].astype(str) == bid]
        return dedupe_run_rows(ok) if dedupe else ok
    return filter_latest_batch(ok) if dedupe else ok


def load_category_df(category: str, *, latest_only: bool = True) -> pd.DataFrame:
    path = results_dir() / f"{category}_results.csv"
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


def stt_wer_narrative(wer_src: pd.DataFrame) -> str:
    """Texto breve sobre WER por fuente de audio (Piper, FLEURS, ruido, etc.)."""
    if wer_src.empty:
        return ""

    mean_by_src = (
        wer_src.groupby("audio_source")["wer_prom"].mean().sort_values().round(4)
    )
    labels = {
        "fleurs_human": "voz humana FLEURS (limpio)",
        "fleurs_human_concat": "FLEURS concatenado largo (~30-40 s)",
        "synthetic_piper": "audio sintético Piper",
        "synthetic_piper_long": "Piper monólogo largo",
        "common_voice_noisy": "Common Voice con ruido de fondo audible (SNR bajo)",
        "common_voice_long": "Common Voice limpio largo",
        "common_voice_central_america": "CV América central (proxy acento CR)",
        "synthetic_noisy_long": "ruido sintético sobre turno largo",
    }
    bits: list[str] = []
    for src, wer in mean_by_src.items():
        label = labels.get(str(src), str(src))
        bits.append(f"{label} ~{wer:.2f}")

    body = (
        "El WER promedio por tipo de audio fue: "
        + "; ".join(bits)
        + ". "
    )
    if "fleurs_human" in mean_by_src.index and "synthetic_piper" in mean_by_src.index:
        ratio = mean_by_src["synthetic_piper"] / max(mean_by_src["fleurs_human"], 1e-6)
        body += (
            f"Con audio sintético (Piper) el error suele ser unas {ratio:.0f} veces mayor que con voz humana (FLEURS). "
        )
    if "common_voice_noisy" in mean_by_src.index and "fleurs_human" in mean_by_src.index:
        body += (
            "Los clips con ruido (Common Voice *noisy*) suelen fallar más que FLEURS limpio. "
        )
    body += (
        "Las tablas generales de STT mezclan todas las fuentes; antes de comparar "
        "proveedores, revisar este desglose."
    )
    return body


MATRIX_DISPLAY_COLS = {
    "servicio": "Servicio",
    "proveedor": "Prov.",
    "latencia_ms": "Lat. (ms)",
    "ttft_ms": "TTFT",
    "wer": "WER",
    "costo_usd": "USD",
    "privacidad_1_5": "Priv.",
    "customizacion_1_5": "Cust.",
    "integracion_1_5": "Integr.",
    "precision_resumen": "Precisión",
}


def format_matrix_for_display(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "precision_resumen" in out.columns:
        out["precision_resumen"] = out["precision_resumen"].replace(
            "Coherencia (revisión manual)",
            "Coherencia (cual.)",
        )
    return out.rename(columns={k: v for k, v in MATRIX_DISPLAY_COLS.items() if k in out.columns})


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
    return format_matrix_for_display(sub[present])


def analysis_meta_line() -> str:
    m = load_manifest()
    if not m:
        return "*Sin manifiesto de corrida; usamos heurística sobre el CSV.*"
    parts = [
        f"*Corrida: `{m.get('run_batch_id', 'n/d')}`",
        f"runs/input: {m.get('runs_per_input', runs_per_input())}",
        f"Python {m.get('python', 'n/d')}",
    ]
    if m.get("catalog_fingerprint"):
        parts.append(f"catálogo: `{m['catalog_fingerprint']}` ({m.get('stt_sample_count', 'n/d')} audios)")
    return " · ".join(parts) + "*"


def e2e_analysis_meta_line() -> str:
    """Cabecera de tablas E2E: usa e2e_batch_id, no el batch LLM/STT/TTS."""
    m = load_manifest()
    batch_df = load_e2e_batch_df(latest_only=True, dedupe=False)
    bid = "n/d"
    if m and m.get("e2e_batch_id"):
        bid = str(m["e2e_batch_id"])
    elif not batch_df.empty and "run_batch_id" in batch_df.columns:
        bid = str(batch_df["run_batch_id"].astype(str).max())
    parts = [
        f"*Corrida E2E: `{bid}`",
        f"runs/input: {m.get('runs_per_input', runs_per_input()) if m else runs_per_input()}",
    ]
    if m:
        parts.append(f"Python {m.get('python', 'n/d')}")
        if m.get("catalog_fingerprint"):
            parts.append(
                f"catálogo: `{m['catalog_fingerprint']}` ({m.get('stt_sample_count', 'n/d')} audios)"
            )
    return " · ".join(parts) + "*"
