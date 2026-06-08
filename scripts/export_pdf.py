"""Exporta docs/informe.md a PDF vía Pandoc (+ Playwright si hace falta)."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INFORME = ROOT / "docs" / "informe.md"
OUT = ROOT / "docs" / "informe_PF3312_Proyecto2.pdf"
HTML_OUT = ROOT / "docs" / "informe_PF3312_Proyecto2.html"


def _html_to_pdf_playwright(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    uri = html_path.resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(uri, wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="A4",
            margin={"top": "2cm", "bottom": "2cm", "left": "2cm", "right": "2cm"},
            print_background=True,
        )
        browser.close()


def _pandoc_html() -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc no está en PATH")
    cmd = [
        pandoc,
        str(INFORME),
        "-o",
        str(HTML_OUT),
        "--resource-path=docs",
        "--standalone",
        "--toc",
        "--toc-depth=2",
        "-c",
        "https://cdn.jsdelivr.net/npm/water.css@2/out/water.css",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)


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
    engines = []
    if shutil.which("pdflatex"):
        engines.append("pdflatex")
    if shutil.which("weasyprint"):
        engines.append("weasyprint")
    engines.append(None)  # HTML fallback

    for engine in engines:
        if engine:
            cmd = [
                pandoc,
                str(INFORME),
                "-o",
                str(OUT),
                "--resource-path=docs",
                f"--pdf-engine={engine}",
                "-V",
                "geometry:margin=2.5cm",
                "-V",
                "fontsize=11pt",
                "--toc",
                "--toc-depth=2",
            ]
            try:
                subprocess.run(cmd, cwd=ROOT, check=True)
                print(f"OK {OUT.relative_to(ROOT)} (motor: {engine})")
                return
            except subprocess.CalledProcessError:
                continue

    _pandoc_html()
    try:
        _html_to_pdf_playwright(HTML_OUT, OUT)
        print(f"OK {OUT.relative_to(ROOT)} (Pandoc + Playwright)")
        return
    except Exception as exc:  # noqa: BLE001
        print(
            f"No se pudo generar PDF automáticamente ({exc}).\n"
            f"HTML listo: {HTML_OUT.relative_to(ROOT)}\n"
            f"Abrir en el navegador → Imprimir → Guardar como PDF."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
