"""Gráficos de latencia/costo y barras con la última corrida."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.aggregate import aggregate_category, load_category_df, load_e2e_df, stt_wer_by_source
from analysis.chart_theme import (
    SOURCE_COLORS,
    apply_theme,
    provider_color,
    save_figure,
    style_axes,
)

from common.paths import docs_dir, project_root

PROJECT_ROOT = project_root()
OUT_DIR = docs_dir() / "graficos_generados"


def _scatter_latency_cost(agg, category: str) -> None:
    apply_theme()
    fig, ax = plt.subplots(figsize=(10, 6))
    costs = agg["costo_usd_prom"].fillna(0.0)
    lats = agg["latencia_ms_prom"]
    max_cost = max(costs.max(), 1e-9)
    max_lat = max(lats.max(), 1.0)

    for i, row in agg.iterrows():
        color = provider_color(str(row["provider"]), i)
        x = row["latencia_ms_prom"]
        y = row["costo_usd_prom"] or 0.0
        size = 180 + 120 * (y / max_cost)
        ax.scatter(x, y, s=size, c=color, alpha=0.88, edgecolors="white", linewidths=1.2, zorder=4)
        ax.annotate(
            f'{row["provider"]}\n{row["model"]}',
            (x, y),
            xytext=(10, 10),
            textcoords="offset points",
            fontsize=8.5,
            color="#334155",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#E2E8F0", alpha=0.92),
            arrowprops=dict(arrowstyle="-", color="#CBD5E1", lw=0.8),
        )

    style_axes(
        ax,
        title=f"Latencia vs. costo ({category.upper()})",
    )
    ax.set_xlabel("Latencia promedio (ms)")
    ax.set_ylabel("Costo promedio por llamada (USD)")
    ax.set_xlim(left=0, right=max_lat * 1.12)
    ax.set_ylim(bottom=-max_cost * 0.05, top=max_cost * 1.15 if max_cost else 0.001)
    save_figure(fig, OUT_DIR / f"{category}_latencia_vs_costo.png")


def _bar_metric(agg, metric: str, category: str, ylabel: str, fname: str) -> None:
    sub = agg.dropna(subset=[metric])
    if sub.empty:
        return
    apply_theme()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    labels = [f"{p}\n{m}" for p, m in zip(sub["provider"], sub["model"], strict=True)]
    values = sub[metric].tolist()
    colors = [provider_color(lbl.split("\n")[0], i) for i, lbl in enumerate(labels)]
    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=colors, alpha=0.9, edgecolor="white", linewidth=1.0, width=0.72)
    ax.bar_label(bars, fmt="%.1f" if metric != "calidad_prom" else "%.3f", padding=4, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=18, ha="right", fontsize=8.5)
    style_axes(ax, title=f"{ylabel} ({category.upper()})")
    ax.set_ylabel(ylabel)
    save_figure(fig, OUT_DIR / fname)


def _stt_wer_by_source_chart(df) -> None:
    wer_df = stt_wer_by_source(df)
    if wer_df.empty:
        return
    apply_theme()
    pivot = wer_df.pivot(index="provider", columns="audio_source", values="wer_prom")
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    x = np.arange(len(pivot.index))
    width = 0.36
    sources = list(pivot.columns)
    for i, source in enumerate(sources):
        offset = (i - (len(sources) - 1) / 2) * width
        color = SOURCE_COLORS.get(str(source), provider_color(str(source), i))
        vals = pivot[source].values
        bars = ax.bar(x + offset, vals, width, label=str(source), color=color, alpha=0.9, edgecolor="white")
        ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels(pivot.index, fontsize=9)
    style_axes(ax, title="STT: WER por fuente de audio (Piper vs FLEURS)")
    ax.set_ylabel("WER promedio")
    ax.legend(title="Fuente", framealpha=0.95, loc="upper right")
    save_figure(fig, OUT_DIR / "stt_wer_por_fuente.png")


def _e2e_stacked_chart() -> None:
    """Barras apiladas: latencia STT/LLM/TTS por escenario E2E."""
    df = load_e2e_df()
    if df.empty:
        return
    agg = df.groupby("escenario")[
        ["stt_latency_ms", "llm_latency_ms", "tts_latency_ms", "overhead_ms"]
    ].mean()
    # ordenado por latencia total para que se lea de rápido a lento
    agg = agg.loc[agg.sum(axis=1).sort_values().index]

    apply_theme()
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    stages = [
        ("stt_latency_ms", "STT", "#0891B2"),
        ("llm_latency_ms", "LLM", "#0F3B82"),
        ("tts_latency_ms", "TTS", "#6366F1"),
        ("overhead_ms", "Overhead", "#94A3B8"),
    ]
    y = np.arange(len(agg.index))
    left = np.zeros(len(agg.index))
    for col, label, color in stages:
        vals = agg[col].fillna(0).values
        ax.barh(y, vals, left=left, height=0.62, label=label, color=color, alpha=0.92, edgecolor="white")
        left += vals

    for i, total in enumerate(left):
        ax.text(total * 1.01, i, f"{total:,.0f} ms", va="center", fontsize=8.5, color="#334155")

    ax.set_yticks(y)
    ax.set_yticklabels(agg.index, fontsize=9)
    style_axes(ax, title="Pipeline E2E: desglose de latencia por etapa")
    ax.set_xlabel("Latencia promedio del turno (ms)")
    ax.set_xlim(right=left.max() * 1.14)
    ax.legend(loc="lower right", framealpha=0.95)
    save_figure(fig, OUT_DIR / "e2e_desglose_latencia.png")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for category in ("llm", "stt", "tts"):
        df = load_category_df(category, latest_only=True)
        if df.empty:
            print(f"[WARN] Saltando gráficos {category}: sin datos")
            continue
        agg = aggregate_category(df, category)
        _scatter_latency_cost(agg, category)
        _bar_metric(agg, "latencia_ms_prom", category, "Latencia promedio (ms)", f"{category}_latency_ms.png")
        if category == "llm":
            _bar_metric(agg, "ttft_ms_prom", category, "TTFT promedio (ms)", f"{category}_ttft_ms.png")
        if category == "stt":
            _bar_metric(agg, "calidad_prom", category, "WER promedio", f"{category}_quality.png")
            _stt_wer_by_source_chart(df)
    _e2e_stacked_chart()


if __name__ == "__main__":
    main()
