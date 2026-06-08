"""Persistencia de resultados de benchmark en CSV/JSON."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from common.base import BenchmarkResult
from common.run_context import current_batch_id


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
RAW_DIR = RESULTS_DIR / "raw"
ARCHIVE_DIR = RESULTS_DIR / "archive"


CSV_HEADERS = [
    "timestamp",
    "run_batch_id",
    "category",
    "provider",
    "model",
    "deployment",
    "test_id",
    "run_id",
    "latency_ms",
    "ttft_ms",
    "input_size",
    "output_size",
    "input_unit",
    "output_unit",
    "cost_usd",
    "quality_metric",
    "quality_metric_name",
    "output_preview",
    "notes",
    "error",
]


def ensure_dirs() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def _stamp_result(result: BenchmarkResult) -> BenchmarkResult:
    if not result.run_batch_id:
        batch = current_batch_id()
        if batch:
            result.run_batch_id = batch
    return result


def append_results_csv(category: str, results: Iterable[BenchmarkResult]) -> Path:
    """Anexa resultados al CSV maestro de una categoría."""
    ensure_dirs()
    csv_path = RESULTS_DIR / f"{category}_results.csv"
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_HEADERS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        for raw in results:
            r = _stamp_result(raw)
            row = r.to_dict()
            preview = row.get("output_preview") or ""
            row["output_preview"] = preview.replace("\n", " ").replace("\r", " ")[:240]
            writer.writerow(row)
    return csv_path


def dump_results_json(category: str, provider: str, results: Iterable[BenchmarkResult]) -> Path:
    """Dump completo (sin truncar) por proveedor en results/raw/."""
    ensure_dirs()
    out_path = RAW_DIR / f"{category}_{provider}.json"
    payload = [_stamp_result(r).to_dict() for r in results]
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def archive_results_csv() -> list[Path]:
    """Mueve CSV actuales a results/archive/ con timestamp."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    moved: list[Path] = []
    batch = current_batch_id() or "manual"
    for category in ("llm", "stt", "tts"):
        src = RESULTS_DIR / f"{category}_results.csv"
        if not src.exists():
            continue
        safe = batch.replace(":", "").replace("-", "")
        dst = ARCHIVE_DIR / f"{category}_results_{safe}.csv"
        src.replace(dst)
        moved.append(dst)
    return moved
