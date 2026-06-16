"""Valida integridad de results/ tras una corrida."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from analysis.aggregate import E2E_CSV, load_e2e_df, slice_latest_batch
from common.paths import results_dir
from benchmarks.pipeline.scenarios import E2E_AUDIO_IDS, PIPELINE_SCENARIOS
from common.benchmark_config import category_row_count, runs_per_input
from common.benchmark_registry import BENCHMARK_REGISTRY, providers_for_category
from common.run_context import load_manifest


def _latest_batch_slice(category: str, *, dedupe: bool = True) -> pd.DataFrame:
    path = results_dir() / f"{category}_results.csv"
    if not path.exists():
        return pd.DataFrame()
    return slice_latest_batch(pd.read_csv(path), dedupe=dedupe)


def _duplicate_keys(df: pd.DataFrame, keys: list[str]) -> int:
    if df.empty:
        return 0
    work = df.copy()
    for col in keys:
        if col not in work.columns:
            work[col] = ""
        work[col] = work[col].fillna("").astype(str)
    return int(work.duplicated(subset=keys, keep=False).sum())


def validate_category(category: str, *, runs: int) -> list[str]:
    issues: list[str] = []
    expected_per_provider = category_row_count(category, runs=runs)
    df = _latest_batch_slice(category)
    if df.empty:
        issues.append(f"{category}: sin filas exitosas en la última corrida")
        return issues

    dupes = _duplicate_keys(_latest_batch_slice(category, dedupe=False), ["provider", "model", "test_id", "run_id"])
    if dupes:
        issues.append(
            f"{category}: {dupes} filas duplicadas (mismo provider/model/test_id/run_id); "
            "ejecute scripts/reset_results.py antes de re-correr"
        )

    present = set(df["provider"].astype(str))
    registered = set(providers_for_category(category))
    unknown = present - registered
    if unknown:
        issues.append(f"{category}: proveedores no registrados en benchmark_registry: {sorted(unknown)}")

    for provider in sorted(present):
        sub = df[df["provider"].astype(str) == provider]
        n = len(sub)
        if n > expected_per_provider:
            issues.append(
                f"{category}/{provider}: {n} filas > esperado {expected_per_provider} "
                f"({runs} runs × inputs)"
            )
        elif n < expected_per_provider:
            issues.append(
                f"[INFO] {category}/{provider}: {n}/{expected_per_provider} filas "
                "(proveedor parcial o sin API key)"
            )

    missing = registered - present
    if missing:
        issues.append(f"[INFO] {category}: sin datos para {sorted(missing)} (omitido o sin credenciales)")

    return issues


def validate_e2e(*, runs: int) -> list[str]:
    issues: list[str] = []
    df = load_e2e_df()
    if df.empty:
        issues.append("e2e: sin turnos exitosos en results/e2e_results.csv")
        return issues

    dupes = _duplicate_keys(load_e2e_df(dedupe=False), ["escenario", "test_id", "run_id"])
    if dupes:
        issues.append(f"e2e: {dupes} turnos duplicados en el último batch")

    expected_audios = set(E2E_AUDIO_IDS)
    found_audios = set(df["test_id"].astype(str))
    missing_audios = expected_audios - found_audios
    if missing_audios:
        issues.append(f"e2e: faltan audios {sorted(missing_audios)} en el último batch")

    for scenario in PIPELINE_SCENARIOS:
        sub = df[df["escenario"] == scenario.nombre]
        if sub.empty:
            issues.append(f"[INFO] e2e: escenario '{scenario.nombre}' sin turnos exitosos")
            continue
        n = len(sub)
        expected = len(E2E_AUDIO_IDS) * runs
        if n > expected:
            issues.append(f"e2e/{scenario.nombre}: {n} turnos > esperado {expected}")

    return issues


def validate_all() -> tuple[list[str], list[str]]:
    manifest = load_manifest()
    runs = int(manifest.get("runs_per_input") or runs_per_input())
    batch = manifest.get("run_batch_id", "n/d")

    errors: list[str] = []
    infos: list[str] = []

    print(f"Validando corrida `{batch}` · {runs} runs/input · {len(BENCHMARK_REGISTRY)} benchmarks registrados")

    for category in ("llm", "stt", "tts"):
        for msg in validate_category(category, runs=runs):
            if msg.startswith("[INFO]"):
                infos.append(msg)
            else:
                errors.append(msg)

    for msg in validate_e2e(runs=runs):
        if msg.startswith("[INFO]"):
            infos.append(msg)
        else:
            errors.append(msg)

    if not E2E_CSV.exists():
        infos.append("[INFO] e2e: results/e2e_results.csv ausente (corra run_e2e)")

    return errors, infos


def main() -> int:
    errors, infos = validate_all()
    for msg in infos:
        print(msg)
    for msg in errors:
        print(f"[ERROR] {msg}")
    if errors:
        print(f"\nValidación FALLÓ · {len(errors)} error(es)")
        return 1
    print(f"\nOK validación · {len(infos)} aviso(s) informativo(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
