"""Limpia informe.md antes de exportar PDF/DOCX de entrega académica."""
from __future__ import annotations

import re

META_LINE_PREFIXES = ("**Autor:**", "**Carné:**", "**Curso:**", "**Profesor:**", "**Programa:**", "**Entregable:**")

_BLOCKED_SUBSTRINGS = (
    "results/raw/",
    "results/tts_outputs/",
    "results/network_speedtest.json",
    "docs/tablas_generadas/",
    "docs/analisis_local/",
    "docs/dimensiones_generadas/",
    "data/test_audio/",
    "entrega/",
    "tools/piper/",
    "scripts/export_pdf.py",
    "scripts/export_docx.py",
    "analysis/merge_informe.py",
    "analysis/pipeline_steps_local",
    "analysis/dimensions_rubric.py",
    "informe_template.md",
)

_CORRIDA_META_RE = re.compile(
    r"^\*\s*Corrida(?:\s+E2E)?:[^*]+\*\s*$",
    re.MULTILINE,
)
_BATCH_ID_RE = re.compile(r"`?20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z`?")
_BATCH_PAREN_RE = re.compile(r"\s*\(20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\)")


def scrub_delivery_text(text: str) -> str:
    lines: list[str] = []
    skip_next_trazabilidad = False
    for line in text.splitlines():
        if "Regenerar tras cada corrida" in line or "Exportar PDF:" in line:
            continue
        if line.startswith(META_LINE_PREFIXES):
            continue
        if "no se versionan en Git" in line or "no están en Git" in line:
            continue
        if any(s in line for s in _BLOCKED_SUBSTRINGS):
            continue
        if line.strip().startswith("**Script:**") and "python -m" in line:
            continue
        if line.strip().startswith("- **Trazabilidad:**"):
            lines.append(
                "- **Trazabilidad:** los resultados quedan en los CSV del repositorio "
                "con identificador de corrida por fila y un manifiesto de ejecución."
            )
            skip_next_trazabilidad = True
            continue
        if skip_next_trazabilidad and (
            "corresponden al batch" in line
            or "E2E se re-corrió" in line
            or "e2e_batch_id" in line
            or "run_batch_id" in line
        ):
            continue
        skip_next_trazabilidad = False
        lines.append(line)

    text = "\n".join(lines) + "\n"
    text = _CORRIDA_META_RE.sub("", text)
    text = _BATCH_PAREN_RE.sub("", text)
    text = _BATCH_ID_RE.sub("", text)
    text = re.sub(r"\s+en el batch\s*", " ", text)
    text = re.sub(r"Batch:\s*", "", text)
    text = re.sub(r"\(ver\s+`[^`]+`\)", "", text)
    text = re.sub(r"\s+\.", ".", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = text.replace("MOS 1-5 (escucha tts_outputs/)", "MOS 1-5 (escucha manual)")
    text = text.replace("t2_oracion_media_run1", "t2_oracion_media")
    text = re.sub(r"\s*\(`[^`]+\.wav`,\s*", " (", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text
