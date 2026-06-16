# Apéndice B: prompts, textos TTS y transcripciones de referencia
import json
from pathlib import Path

from common.audio_samples import TTS_TEXTS
from common.prompts import LLM_PROMPTS

from common.paths import docs_dir, project_root

PROJECT_ROOT = project_root()
REF_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"
OUT_FILE = docs_dir() / "dimensiones_datos" / "appendix_inputs.md"


def _quote_block(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def main() -> None:
    lines: list[str] = [
        "# Apéndice B: Inputs controlados de prueba",
        "",
        "Reproducción de los insumos definidos en `common/prompts.py`, "
        "`common/audio_samples.py` y `data/reference_transcriptions.json`.",
        "",
        "## B.1 Prompts LLM (5)",
        "",
    ]
    for p in LLM_PROMPTS:
        lines.append(f"### `{p['id']}`: {p['title']}")
        lines.append("")
        lines.append(_quote_block(p["content"]))
        lines.append("")

    lines.append("## B.2 Textos TTS (5)")
    lines.append("")
    for t in TTS_TEXTS:
        lines.append(f"- **`{t['id']}`:** {t['text']}")
    lines.append("")

    stt_samples: list[dict] = []
    if REF_FILE.exists():
        data = json.loads(REF_FILE.read_text(encoding="utf-8"))
        stt_samples = list(data.get("samples", []))
    lines.append(f"## B.3 Audios STT ({len(stt_samples)})")
    lines.append("")
    if stt_samples:
        for s in stt_samples:
            src = s.get("source", "n/d")
            lines.append(
                f"- **`{s['id']}`** (`{s['file']}`, {src}): "
                f"«{s['reference_text']}»"
            )
    else:
        lines.append("*Pendiente: `data/reference_transcriptions.json`*")
    lines.append("")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK {OUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
