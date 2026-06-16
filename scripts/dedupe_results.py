"""Quita filas duplicadas en results/*.csv (misma corrida, mismo input/run)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from analysis.aggregate import dedupe_run_rows
from common.paths import e2e_csv_path, results_dir


def _dedupe_frame(df, *, category: str | None = None):
    if df.empty:
        return df
    import pandas as pd

    if category == "e2e" or (
        "escenario" in df.columns and "provider" not in df.columns
    ):
        out = df.copy()
        for col in ("escenario", "test_id", "run_id"):
            if col not in out.columns:
                out[col] = ""
            out[col] = out[col].fillna("").astype(str)
        out["ts"] = pd.to_datetime(out.get("timestamp"), utc=True, errors="coerce")
        if "run_batch_id" in out.columns:
            parts = []
            for _, grp in out.groupby("run_batch_id", sort=False):
                parts.append(
                    grp.sort_values("ts")
                    .drop_duplicates(subset=["escenario", "test_id", "run_id"], keep="last")
                )
            return pd.concat(parts, ignore_index=True) if parts else out
        return out.sort_values("ts").drop_duplicates(
            subset=["escenario", "test_id", "run_id"], keep="last"
        ).reset_index(drop=True)

    if "run_batch_id" not in df.columns:
        return dedupe_run_rows(df)
    parts = []
    for _, grp in df.groupby("run_batch_id", sort=False):
        parts.append(dedupe_run_rows(grp))
    return pd.concat(parts, ignore_index=True) if parts else df


def dedupe_file(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    import pandas as pd

    df = pd.read_csv(path)
    before = len(df)
    category = None
    name = path.name
    if name == "e2e_results.csv":
        category = "e2e"
    clean = _dedupe_frame(df, category=category)
    if len(clean) < before:
        clean.to_csv(path, index=False, lineterminator="\n")
    return before, len(clean)


def main() -> int:
    targets = [
        results_dir() / "llm_results.csv",
        results_dir() / "stt_results.csv",
        results_dir() / "tts_results.csv",
        e2e_csv_path(),
    ]
    total_removed = 0
    for path in targets:
        before, after = dedupe_file(path)
        removed = before - after
        if removed:
            print(f"OK {path.name}: {before} → {after} filas (-{removed})")
            total_removed += removed
        elif before:
            print(f"OK {path.name}: sin duplicados ({before} filas)")
    if total_removed:
        print(f"\nListo. Se eliminaron {total_removed} fila(s) redundante(s).")
    else:
        print("\nNada que deduplicar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
