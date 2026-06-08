"""Inserta tablas y resúmenes generados en docs/informe.md (marcadores INCLUDE).

Marcadores en informe.md:
  <!-- INCLUDE: ruta/relativa/desde/docs -->

Uso:
    python -m analysis.merge_informe
"""
from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INFORME = PROJECT_ROOT / "docs" / "informe.md"
DOCS = PROJECT_ROOT / "docs"
MARKER = re.compile(r"<!--\s*INCLUDE:\s*([^\s]+)\s*-->")


def main() -> None:
    text = INFORME.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:
        rel = match.group(1).strip()
        path = DOCS / rel if not rel.startswith("docs/") else PROJECT_ROOT / rel
        if not path.exists():
            return f"\n> *Pendiente: generar `{rel}`*\n"
        body = path.read_text(encoding="utf-8")
        # Si el archivo ya tiene título H1, quitarlo para no duplicar
        lines = body.splitlines()
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
            while lines and not lines[0].strip():
                lines = lines[1:]
        return "\n" + "\n".join(lines) + "\n"

    new_text = MARKER.sub(repl, text)
    INFORME.write_text(new_text, encoding="utf-8")
    n = len(MARKER.findall(text))
    print(f"OK informe.md actualizado ({n} bloques INCLUDE)")


if __name__ == "__main__":
    main()
