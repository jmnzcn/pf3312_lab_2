"""Renderiza diagrama del pipeline a PNG (sin dependencia de PlantUML)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "graficos_generados" / "pipeline_comunicacion.png"

BOXES = [
    (0.05, 0.55, "Usuario"),
    (0.22, 0.55, "Unity\n(micrófono)"),
    (0.40, 0.55, "STT\n(cloud/local)"),
    (0.58, 0.55, "LLM\n(streaming)"),
    (0.76, 0.55, "TTS\n(cloud/local)"),
    (0.92, 0.55, "Lip-sync\n+ audio"),
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("Pipeline de comunicación — Agente virtual (PF-3312)", fontsize=13, pad=12)

    centers = []
    for x, y, label in BOXES:
        box = FancyBboxPatch(
            (x - 0.07, y - 0.12),
            0.14,
            0.24,
            boxstyle="round,pad=0.02",
            linewidth=1.2,
            edgecolor="#334155",
            facecolor="#e2e8f0",
        )
        ax.add_patch(box)
        ax.text(x, y, label, ha="center", va="center", fontsize=9)
        centers.append((x, y))

    for i in range(len(centers) - 1):
        x1, y1 = centers[i]
        x2, y2 = centers[i + 1]
        arrow = FancyArrowPatch(
            (x1 + 0.08, y1),
            (x2 - 0.08, y2),
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.2,
            color="#0f172a",
        )
        ax.add_patch(arrow)

    ax.text(
        0.5,
        0.12,
        "Benchmarking: 15 servicios evaluados en STT, LLM y TTS "
        "(ver docs/pipeline.puml para detalle UML)",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    fig.tight_layout()
    fig.savefig(OUT, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"OK {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
