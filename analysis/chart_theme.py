"""Colores y estilo matplotlib para gráficos del benchmark."""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors as mcolors
from matplotlib.patches import FancyBboxPatch

# Azul UCR + acentos para los gráficos.
PRIMARY = "#0F3B82"
PRIMARY_LIGHT = "#2A5BAA"
ACCENT = "#6366F1"
ACCENT_SOFT = "#A5B4FC"
SUCCESS = "#16A34A"
WARNING = "#D97706"
MUTED = "#64748B"
BG = "#F8FAFC"
GRID = "#E2E8F0"
TEXT = "#1E293B"

PROVIDER_COLORS: dict[str, str] = {
    "openai": "#0F3B82",
    "anthropic": "#6366F1",
    "google": "#16A34A",
    "groq": "#D97706",
    "ollama": "#7C3AED",
    "deepgram": "#0891B2",
    "azure": "#2563EB",
    "assemblyai": "#DB2777",
    "faster-whisper": "#475569",
    "elevenlabs": "#BE185D",
    "piper": "#0D9488",
}

CATEGORY_PALETTES = {
    "llm": ["#0F3B82", "#6366F1", "#16A34A", "#D97706", "#7C3AED"],
    "stt": ["#0891B2", "#0F3B82", "#2563EB", "#DB2777", "#475569"],
    "tts": ["#2563EB", "#BE185D", "#16A34A", "#0F3B82", "#0D9488"],
}

SOURCE_COLORS = {
    "synthetic_piper": "#6366F1",
    "synthetic_piper_long": "#4F46E5",
    "fleurs_human": "#16A34A",
    "fleurs_human_concat": "#15803D",
    "common_voice_noisy": "#D97706",
    "common_voice_long": "#CA8A04",
    "common_voice_central_america": "#059669",
    "synthetic_noisy_long": "#EA580C",
    "piper": "#6366F1",
}


def apply_theme() -> None:
    mpl.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": "#FFFFFF",
            "axes.edgecolor": GRID,
            "axes.labelcolor": TEXT,
            "axes.titlecolor": PRIMARY,
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "grid.alpha": 0.9,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "Inter", "DejaVu Sans", "Arial"],
            "font.size": 10,
            "legend.frameon": True,
            "legend.framealpha": 0.95,
            "legend.edgecolor": GRID,
            "figure.dpi": 150,
            "savefig.dpi": 300,
        }
    )


def provider_color(provider: str, fallback_idx: int = 0) -> str:
    key = provider.lower().replace("_", "-")
    if key in PROVIDER_COLORS:
        return PROVIDER_COLORS[key]
    palette = list(PROVIDER_COLORS.values())
    return palette[fallback_idx % len(palette)]


def style_axes(ax, *, title: str | None = None) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    if title:
        ax.set_title(title, pad=14, loc="left", fontsize=13, fontweight="bold", color=PRIMARY)


def add_figure_footer(fig, text: str) -> None:
    fig.text(
        0.01,
        0.01,
        text,
        fontsize=8,
        color=MUTED,
        ha="left",
        va="bottom",
    )


def save_figure(fig, path: Path, *, dpi: int = 360) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
        edgecolor="none",
        pad_inches=0.35,
    )
    plt.close(fig)


def gradient_cmap() -> mcolors.LinearSegmentedColormap:
    return mcolors.LinearSegmentedColormap.from_list(
        "ucr_blue_green",
        ["#FEE2E2", "#DBEAFE", "#0F3B82", "#14532D"],
    )


def qualitative_cmap() -> mcolors.LinearSegmentedColormap:
    return mcolors.LinearSegmentedColormap.from_list(
        "ucr_qual",
        ["#F1F5F9", "#93C5FD", "#2A5BAA", "#0F3B82", "#052E6F"],
    )


def bar_colors(labels: list[str], category: str) -> list[str]:
    palette = CATEGORY_PALETTES.get(category, list(PROVIDER_COLORS.values()))
    out = []
    for i, label in enumerate(labels):
        prov = label.split("\n")[0].lower()
        out.append(provider_color(prov, i) if prov else palette[i % len(palette)])
    return out


def draw_gradient_bar(ax, x, height, width, color: str, alpha: float = 0.92) -> None:
    base = np.array(mcolors.to_rgb(color))
    light = 1 - (1 - base) * 0.35
    grad = mcolors.LinearSegmentedColormap.from_list("bar", [light, color])
    ax.bar(
        x,
        height,
        width=width,
        color=color,
        alpha=alpha,
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )


def pipeline_box_style() -> dict:
    return {
        "boxstyle": "round,pad=0.03,rounding_size=0.08",
        "linewidth": 1.4,
        "edgecolor": PRIMARY_LIGHT,
        "facecolor": "#EFF6FF",
    }
