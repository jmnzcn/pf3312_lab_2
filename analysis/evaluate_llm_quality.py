"""Revisa si el LLM cumple el JSON del prompt p3."""
from __future__ import annotations

import json
import re
from pathlib import Path

from tabulate import tabulate

from analysis.aggregate import load_category_df
from common.run_context import load_manifest

from common.paths import docs_dir, project_root, results_dir

PROJECT_ROOT = project_root()
OUT_DIR = docs_dir() / "dimensiones_datos"
NOTES_FILE = PROJECT_ROOT / "data" / "llm_quality_notes.json"
RAW_DIR = results_dir() / "raw"

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
    # Si el JSON completo no cabe en el preview, se infiere por longitud
    stripped = text.strip()
    if output_size >= 120 and stripped.startswith("{") and '"agentes"' in stripped:
        return all(k in stripped for k in ('"nombre"', '"estilo"', '"rol"', '"expresiones"'))
    if output_size >= 120 and stripped.startswith("["):
        return all(k in stripped for k in ('"nombre"', '"estilo"', '"rol"', '"expresiones"'))
    return False


def _load_llm_outputs() -> list[dict]:
    manifest = load_manifest()
    batch_id = str(manifest.get("run_batch_id") or "")
    rows: list[dict] = []
    for path in sorted(RAW_DIR.glob("llm_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for row in data:
            if batch_id and str(row.get("run_batch_id") or "") != batch_id:
                continue
            rows.append(row)
    return rows


def _quality_reading_paragraph(json_rows: list[dict], notes: dict | None) -> str:
    if not json_rows:
        return ""
    by_rate = {r["provider"]: r["tasa_json"] for r in json_rows}
    perfect = [p for p, t in sorted(by_rate.items()) if t >= 1.0]
    weak = [p for p, t in sorted(by_rate.items()) if t < 1.0]
    bits: list[str] = []
    if perfect:
        bits.append(
            ", ".join(perfect) + " cumplieron el JSON en todas las repeticiones"
        )
    if weak:
        details = ", ".join(f"{p} ({by_rate[p]:.0%})" for p in weak)
        bits.append(f"con menor cumplimiento: {details}")
    coherencia_bits: list[str] = []
    if notes and notes.get("providers"):
        for row in notes["providers"]:
            prov = row.get("provider") or row.get("proveedor")
            score = row.get("coherencia_1_5")
            if prov and score is not None:
                coherencia_bits.append(f"{prov} {score}/5")
    if coherencia_bits:
        bits.append("coherencia manual p1/p2/p4/p5: " + ", ".join(coherencia_bits))
    if not bits:
        return ""
    return (
        "\nEn p3_json_estricto, "
        + "; ".join(bits)
        + ". Para JSON estricto (p3), los modelos grandes en nube fallaron menos; "
        "detalle por prompt en el Apéndice B.\n"
    )


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
    lines = [
        "*Dimensión 2 (precisión LLM): revisión manual de coherencia en p1/p2/p4/p5 "
        "y tasa de JSON válido en p3_json_estricto (escala 1-5 en las notas).*",
        "",
    ]
    if not records:
        lines.append("*Sin datos LLM para evaluar.*")
    else:
        json_rows = evaluate_json_prompt(records)
        lines.append("## Prompt p3_json_estricto: cumplimiento de esquema JSON\n")
        lines.append(tabulate(json_rows, headers="keys", tablefmt="github", showindex=False))
        notes = None
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
                    "`data/llm_quality_notes.json` (escala 1-5 por proveedor).*"
                )
            if notes.get("evaluador"):
                lines.append(
                    f"\n*Evaluador: {notes['evaluador']} · {notes.get('metodo', '')}*"
                )
            if notes.get("providers"):
                rows = [
                    {k: p[k] for k in ("provider", "coherencia_1_5", "instrucciones_1_5") if k in p}
                    for p in notes["providers"]
                ]
                lines.append("\n## Puntuación cualitativa (escala 1–5)\n")
                lines.append(tabulate(rows, headers="keys", tablefmt="github", showindex=False))
        else:
            lines.append(
                "\n*Coherencia global en p1/p2/p4/p5: completar en "
                "`data/llm_quality_notes.json` (escala 1-5 por proveedor).*"
            )

    out = OUT_DIR / "llm_calidad.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
