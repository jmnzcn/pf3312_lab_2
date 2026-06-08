"""Exporta docs/informe.md a PDF vía Pandoc (si está instalado)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFORME = ROOT / "docs" / "informe.md"
OUT = ROOT / "docs" / "informe_PF3312_Proyecto2.pdf"


def main() -> None:
    if not INFORME.exists():
        sys.exit(f"No existe {INFORME}")
    pandoc = shutil.which("pandoc")
    if not pandoc:
        print(
            "Pandoc no está en PATH. Alternativas:\n"
            "  1. Instalar Pandoc: https://pandoc.org/installing.html\n"
            "  2. VS Code: extensión Markdown PDF sobre docs/informe.md\n"
            f"  3. Subir {INFORME} a un convertidor online"
        )
        sys.exit(1)
    cmd = [
        pandoc,
        str(INFORME),
        "-o",
        str(OUT),
        "--resource-path=docs",
        "-V",
        "geometry:margin=2.5cm",
        "-V",
        "fontsize=11pt",
        "--toc",
        "--toc-depth=2",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    print(f"OK {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
