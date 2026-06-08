"""Evalúa calidad LLM: JSON válido en p3 y resumen automático."""
from __future__ import annotations

import json
import re
from pathlib import Path

from tabulate import tabulate

from analysis.aggregate import analysis_meta_line, load_category_df

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "docs" / "dimensiones_generadas"
NOTES_FILE = PROJECT_ROOT / "data" / "llm_quality_notes.json"
RAW_DIR = PROJECT_ROOT / "results" / "raw"

REQUIRED_AGENT_KEYS = {"nombre", "estilo", "rol", "expresiones"}
VALID_ESTILOS = {"realista", "caricaturesco", "cartoon"}


def _extract_json(text: str) -> dict | list | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for pattern in (r"\{[\s\S]*\}", r"\[[\s\S]*\]"):
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                continue
    return None


def _agents_from_payload(obj: dict | list | None) -> list[dict]:
    if obj is None:
        return []
    if isinstance(obj, list):
        return [a for a in obj if isinstance(a, dict)]
    if isinstance(obj, dict):
        if "agentes" in obj and isinstance(obj["agentes"], list):
            return [a for a in obj["agentes"] if isinstance(a, dict)]
        if REQUIRED_AGENT_KEYS <= set(obj.keys()):
            return [obj]
    return []


def _valid_p3_json(text: str, *, output_size: int = 0) -> bool:
    obj = _extract_json(text)
    agents = _agents_from_payload(obj)
    if agents:
        if len(agents) != 3:
            return False
        for agent in agents:
            if not REQUIRED_AGENT_KEYS <= set(agent.keys()):
                return False
            if agent.get("estilo") not in VALID_ESTILOS:
                return False
            if not isinstance(agent.get("expresiones"), list) or not agent["expresiones"]:
                return False
        return True
    # Previews truncados a ~200 chars: heurística si el JSON completo fue largo
    stripped = text.strip()
    if output_size >= 120 and stripped.startswith("{") and '"agentes"' in stripped:
        return all(k in stripped for k in ('"nombre"', '"estilo"', '"rol"', '"expresiones"'))
    if output_size >= 120 and stripped.startswith("["):
        return all(k in stripped for k in ('"nombre"', '"estilo"', '"rol"', '"expresiones"'))
    return False


def _load_llm_outputs() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(RAW_DIR.glob("llm_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows.extend(data)
    return rows


def _response_text(row: dict) -> str:
    return str(row.get("output_text") or row.get("output_preview") or "")


def evaluate_json_prompt(records: list[dict]) -> list[dict]:
    sub = [r for r in records if r.get("test_id") == "p3_json_estricto" and not r.get("error")]
    by_provider: dict[str, list[dict]] = {}
    for row in sub:
        by_provider.setdefault(row["provider"], []).append(row)

    rows: list[dict] = []
    for provider in sorted(by_provider):
        items = by_provider[provider]
        valid = 0
        for row in items:
            text = _response_text(row)
            size = int(row.get("output_size") or 0)
            has_full = bool(row.get("output_text"))
            if _valid_p3_json(text, output_size=size if not has_full else 0):
                valid += 1
        rows.append(
            {
                "provider": provider,
                "llamadas": len(items),
                "json_valido": valid,
                "tasa_json": round(valid / len(items), 2) if items else 0,
            }
        )
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = _load_llm_outputs()
    df = load_category_df("llm", latest_only=True)
    lines = [analysis_meta_line(), ""]
    if not records:
        lines.append("*Sin datos LLM para evaluar.*")
    else:
        json_rows = evaluate_json_prompt(records)
        lines.append("## Prompt p3_json_estricto — cumplimiento de esquema JSON\n")
        lines.append(tabulate(json_rows, headers="keys", tablefmt="github", showindex=False))
        notes_filled = False
        if NOTES_FILE.exists():
            notes = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
            notes_filled = any(
                p.get("coherencia_1_5") is not None for p in notes.get("providers", [])
            )
        if notes_filled:
            lines.append(
                "\n*Coherencia global en p1/p2/p4/p5: `data/llm_quality_notes.json`.*"
            )
        else:
            lines.append(
                "\n*Coherencia global en p1/p2/p4/p5: completar en "
                "`data/llm_quality_notes.json` (escala 1–5 por proveedor).*"
            )
        if NOTES_FILE.exists():
            notes = json.loads(NOTES_FILE.read_text(encoding="utf-8"))
            if notes.get("providers"):
                lines.append("\n## Notas cualitativas (archivo)\n")
                lines.append(tabulate(notes["providers"], headers="keys", tablefmt="github", showindex=False))

    out = OUT_DIR / "llm_calidad.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
