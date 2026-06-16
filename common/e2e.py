"""Dataclass y CSV para resultados E2E."""
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from common.paths import e2e_csv_path, results_raw_dir
from common.run_context import current_batch_id

E2E_HEADERS = [
    "timestamp",
    "run_batch_id",
    "escenario",
    "stt_provider",
    "llm_provider",
    "tts_provider",
    "test_id",
    "run_id",
    "stt_latency_ms",
    "llm_latency_ms",
    "llm_ttft_ms",
    "tts_latency_ms",
    "total_latency_ms",
    "overhead_ms",
    "stt_cost_usd",
    "llm_cost_usd",
    "tts_cost_usd",
    "total_cost_usd",
    "transcript_preview",
    "llm_response_preview",
    "notes",
    "error",
]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class E2ETurnResult:
    escenario: str
    stt_provider: str
    llm_provider: str
    tts_provider: str
    test_id: str
    run_id: int
    stt_latency_ms: float = 0.0
    llm_latency_ms: float = 0.0
    llm_ttft_ms: float | None = None
    tts_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    overhead_ms: float = 0.0
    stt_cost_usd: float | None = None
    llm_cost_usd: float | None = None
    tts_cost_usd: float | None = None
    total_cost_usd: float | None = None
    transcript: str = ""
    llm_response: str = ""
    notes: str = ""
    error: str | None = None
    timestamp: str = field(default_factory=_utcnow)
    run_batch_id: str = ""

    def finalize(self) -> None:
        serial = self.stt_latency_ms + self.llm_latency_ms + self.tts_latency_ms
        self.overhead_ms = max(0.0, self.total_latency_ms - serial)
        costs = [c for c in (self.stt_cost_usd, self.llm_cost_usd, self.tts_cost_usd) if c is not None]
        self.total_cost_usd = sum(costs) if costs else None
        if not self.run_batch_id:
            self.run_batch_id = current_batch_id() or ""

    def to_row(self) -> dict:
        self.finalize()
        return {
            "timestamp": self.timestamp,
            "run_batch_id": self.run_batch_id,
            "escenario": self.escenario,
            "stt_provider": self.stt_provider,
            "llm_provider": self.llm_provider,
            "tts_provider": self.tts_provider,
            "test_id": self.test_id,
            "run_id": self.run_id,
            "stt_latency_ms": round(self.stt_latency_ms, 2),
            "llm_latency_ms": round(self.llm_latency_ms, 2),
            "llm_ttft_ms": round(self.llm_ttft_ms, 2) if self.llm_ttft_ms is not None else "",
            "tts_latency_ms": round(self.tts_latency_ms, 2),
            "total_latency_ms": round(self.total_latency_ms, 2),
            "overhead_ms": round(self.overhead_ms, 2),
            "stt_cost_usd": self.stt_cost_usd if self.stt_cost_usd is not None else "",
            "llm_cost_usd": self.llm_cost_usd if self.llm_cost_usd is not None else "",
            "tts_cost_usd": self.tts_cost_usd if self.tts_cost_usd is not None else "",
            "total_cost_usd": self.total_cost_usd if self.total_cost_usd is not None else "",
            "transcript_preview": self.transcript.replace("\n", " ")[:240],
            "llm_response_preview": self.llm_response.replace("\n", " ")[:240],
            "notes": self.notes,
            "error": self.error or "",
        }


def append_e2e_results(results: Iterable[E2ETurnResult]) -> Path:
    """Anexa turnos E2E al CSV y guarda un JSON del batch en results/raw/."""
    csv_path = e2e_csv_path()
    raw_dir = results_raw_dir()
    raw_dir.mkdir(parents=True, exist_ok=True)
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=E2E_HEADERS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        payload = []
        for raw in results:
            row = raw.to_row()
            writer.writerow(row)
            payload.append(asdict(raw))
    if payload:
        batch = payload[-1].get("run_batch_id") or "manual"
        safe = str(batch).replace(":", "").replace("-", "")
        out = raw_dir / f"e2e_{safe}.json"
        import json

        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return csv_path


def e2e_llm_prompt(transcript: str) -> dict:
    """Prompt mínimo para el turno conversacional a partir de la transcripción STT."""
    content = (
        f"Transcripción de voz del usuario: «{transcript.strip()}»\n\n"
        "Responde en español como agente virtual útil, en máximo tres oraciones."
    )
    return {
        "id": "e2e_turn",
        "title": "Turno conversacional E2E",
        "content": content,
        "expected_tokens": 120,
    }
