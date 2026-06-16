"""Renderiza diagrama del pipeline a PNG (sin dependencia de PlantUML)."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from analysis.chart_theme import PRIMARY, PRIMARY_LIGHT, TEXT, apply_theme, save_figure, style_axes

OUT = ROOT / "docs" / "graficos_generados" / "pipeline_comunicacion.png"

BOXES = [
    (0.05, 0.55, "Usuario", "#EFF6FF"),
    (0.22, 0.55, "Cliente\n(micrófono)", "#DBEAFE"),
    (0.40, 0.55, "STT\n(cloud/local)", "#BFDBFE"),
    (0.58, 0.55, "LLM\n(streaming)", "#93C5FD"),
    (0.76, 0.55, "TTS\n(cloud/local)", "#60A5FA"),
    (0.92, 0.55, "Reproductor\naudio", "#3B82F6"),
]


def main() -> None:
    apply_theme()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.5, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    style_axes(ax, title="Pipeline de comunicación: Agente virtual (PF-3312)")

    centers = []
    for x, y, label, fill in BOXES:
        box = FancyBboxPatch(
            (x - 0.075, y - 0.13),
            0.15,
            0.26,
            boxstyle="round,pad=0.03,rounding_size=0.06",
            linewidth=1.6,
            edgecolor=PRIMARY_LIGHT,
            facecolor=fill,
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center", fontsize=9.5, color=TEXT, fontweight="600")
        centers.append((x, y))

    for i in range(len(centers) - 1):
        x1, y1 = centers[i]
        x2, y2 = centers[i + 1]
        arrow = FancyArrowPatch(
            (x1 + 0.085, y1),
            (x2 - 0.085, y2),
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=2.0,
            color=PRIMARY,
            zorder=5,
        )
        ax.add_patch(arrow)

    ax.text(
        0.5,
        0.1,
        "15 servicios evaluados en STT, LLM y TTS · Ver docs/pipeline.puml para detalle UML",
        ha="center",
        fontsize=8.5,
        color="#64748B",
        style="italic",
    )
    save_figure(fig, OUT, dpi=180)


if __name__ == "__main__":
    main()
