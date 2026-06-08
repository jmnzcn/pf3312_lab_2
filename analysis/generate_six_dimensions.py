"""Genera análisis de las 6 dimensiones del enunciado PF-3312.

Salida en docs/dimensiones_generadas/:
  - Una tabla/gráfico por dimensión
  - Matriz maestra 15 servicios × 6 dimensiones
  - resumen_ejecutivo.md

Dimensiones:
  1. Latencia empírica (CSV: latency_ms, ttft_ms)
  2. Precisión / calidad (CSV: WER STT; cualitativo LLM/TTS)
  3. Costo (CSV: cost_usd)
  4. Privacidad (catálogo 1-5)
  5. Customización (catálogo 1-5)
  6. Integración (catálogo 1-5)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

import json

from analysis.aggregate import (
    aggregate_category,
    analysis_meta_line,
    build_category_matrix_5x6,
    load_category_df,
    stt_wer_by_source,
)
from analysis.dimensions_catalog import QUALITATIVE


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results"
OUT_DIR = PROJECT_ROOT / "docs" / "dimensiones_generadas"
CHARTS_DIR = PROJECT_ROOT / "docs" / "graficos_generados"
MOS_FILE = PROJECT_ROOT / "data" / "tts_mos_scores.json"

DIMENSIONS = [
    ("1_latencia", "Latencia empírica"),
    ("2_precision", "Precisión y calidad"),
    ("3_costo", "Costo y escalabilidad"),
    ("4_privacidad", "Privacidad y gobernanza"),
    ("5_customizacion", "Customización"),
    ("6_integracion", "Facilidad de integración"),
]


def _load_ok(category: str) -> pd.DataFrame:
    return load_category_df(category, latest_only=True)


def _agg_quantitative(df: pd.DataFrame, category: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    agg = aggregate_category(df, category)
    g = agg.rename(
        columns={
            "latencia_ms_prom": "latencia_ms",
            "latencia_ms_p95": "latencia_p95",
            "ttft_ms_prom": "ttft_ms",
            "costo_usd_prom": "costo_usd",
            "calidad_prom": "wer",
        }
    )
    g["servicio"] = g["categoria"] + "/" + g["provider"]
    return g


def _build_master_rows() -> list[dict]:
    rows: list[dict] = []
    categories = ("llm", "stt", "tts")
    quant = {c: _agg_quantitative(_load_ok(c), c) for c in categories}

    all_services: set[str] = set(QUALITATIVE.keys())
    for c in categories:
        if not quant[c].empty:
            all_services.update(quant[c]["servicio"].tolist())

    for servicio in sorted(all_services):
        cat, _, prov = servicio.partition("/")
        prov = prov or servicio
        q = QUALITATIVE.get(servicio) or QUALITATIVE.get(servicio.replace("_", "-"))
        row: dict = {
            "servicio": servicio,
            "categoria": cat,
            "proveedor": prov.split("/")[-1] if "/" in prov else prov,
        }

        sub = quant[cat][quant[cat]["servicio"] == servicio] if not quant[cat].empty else pd.DataFrame()
        if not sub.empty:
            r = sub.iloc[0]
            row["latencia_ms"] = round(r["latencia_ms"], 1) if pd.notna(r["latencia_ms"]) else None
            row["ttft_ms"] = round(r["ttft_ms"], 1) if "ttft_ms" in r and pd.notna(r.get("ttft_ms")) else None
            row["costo_usd"] = r["costo_usd"] if pd.notna(r["costo_usd"]) else 0.0
            row["wer"] = round(r["wer"], 4) if "wer" in r and pd.notna(r.get("wer")) else None
        else:
            row["latencia_ms"] = row["ttft_ms"] = row["wer"] = None
            row["costo_usd"] = None

        if q:
            row["privacidad_1_5"] = q.privacidad
            row["customizacion_1_5"] = q.customizacion
            row["integracion_1_5"] = q.integracion
            row["nota_privacidad"] = q.privacidad_nota
            row["nota_custom"] = q.customizacion_nota
            row["nota_integracion"] = q.integracion_nota
        else:
            row["privacidad_1_5"] = row["customizacion_1_5"] = row["integracion_1_5"] = None

        # Precisión resumen
        if cat == "stt" and row.get("wer") is not None:
            row["precision_resumen"] = f"WER={row['wer']}"
        elif cat == "llm":
            row["precision_resumen"] = "Coherencia (cualitativo en informe)"
        else:
            row["precision_resumen"] = "MOS 1-5 (escucha tts_outputs/)"

        rows.append(row)
    return rows


def _write_md(path: Path, title: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    print(f"OK {path.relative_to(PROJECT_ROOT)}")


def _heatmap_qualitative(master: pd.DataFrame, col: str, title: str, fname: str) -> None:
    sub = master.dropna(subset=[col]).copy()
    if sub.empty:
        return
    pivot = sub.pivot_table(index="servicio", values=col, aggfunc="first")
    fig, ax = plt.subplots(figsize=(6, max(4, len(pivot) * 0.35)))
    im = ax.imshow(pivot.values, aspect="auto", cmap="YlGn", vmin=1, vmax=5)
    ax.set_xticks([0])
    ax.set_xticklabels([title])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    for i, v in enumerate(pivot.values.flatten()):
        ax.text(0, i, f"{int(v)}", ha="center", va="center", color="black", fontsize=9)
    plt.colorbar(im, ax=ax, label="Puntuación 1-5")
    ax.set_title(title)
    fig.tight_layout()
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHARTS_DIR / fname
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"OK {out.relative_to(PROJECT_ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    master_rows = _build_master_rows()
    master = pd.DataFrame(master_rows)

    # --- Dimensión 1: Latencia ---
    lat = master[["servicio", "latencia_ms", "ttft_ms", "categoria"]].copy()
    lat = lat.dropna(subset=["latencia_ms"], how="all")
    body = tabulate(lat, headers="keys", tablefmt="github", showindex=False, floatfmt=".2f")
    body += "\n\n*TTFT solo aplica a LLM con streaming.*\n"
    _write_md(OUT_DIR / "1_latencia.md", "Dimensión 1 — Latencia empírica", body)

    # --- Dimensión 2: Precisión ---
    prec = master[["servicio", "categoria", "wer", "precision_resumen"]].copy()
    _write_md(
        OUT_DIR / "2_precision.md",
        "Dimensión 2 — Precisión y calidad",
        tabulate(prec, headers="keys", tablefmt="github", showindex=False),
    )

    # --- Dimensión 3: Costo ---
    cost = master[["servicio", "costo_usd", "categoria"]].copy()
    cost = cost[cost["costo_usd"].notna()]
    _write_md(
        OUT_DIR / "3_costo.md",
        "Dimensión 3 — Costo (USD por llamada, estimado)",
        tabulate(cost.round(6), headers="keys", tablefmt="github", showindex=False),
    )

    # --- Dimensiones 4-6 cualitativas ---
    for key, col, note_col, title, fname in [
        ("4_privacidad", "privacidad_1_5", "nota_privacidad", "Privacidad y gobernanza", "heatmap_privacidad.png"),
        ("5_customizacion", "customizacion_1_5", "nota_custom", "Customización", "heatmap_customizacion.png"),
        ("6_integracion", "integracion_1_5", "nota_integracion", "Integración", "heatmap_integracion.png"),
    ]:
        sub = master[["servicio", col, note_col]].dropna(subset=[col])
        tbl = tabulate(sub, headers="keys", tablefmt="github", showindex=False)
        _write_md(OUT_DIR / f"{key}.md", f"Dimensión — {title}", tbl)
        _heatmap_qualitative(master, col, title, fname)

    # --- Matriz maestra ---
    matrix_cols = [
        "servicio",
        "latencia_ms",
        "ttft_ms",
        "wer",
        "costo_usd",
        "privacidad_1_5",
        "customizacion_1_5",
        "integracion_1_5",
        "precision_resumen",
    ]
    matrix = master[matrix_cols]
    _write_md(
        OUT_DIR / "matriz_6_dimensiones.md",
        "Matriz maestra — 6 dimensiones × servicios",
        tabulate(matrix, headers="keys", tablefmt="github", showindex=False, floatfmt=".4f"),
    )

    # --- Resumen ejecutivo ---
    lines = [
        "## Cobertura de dimensiones en este repo\n",
        "| Dimensión | Fuente en el proyecto |",
        "|-----------|------------------------|",
        "| 1 Latencia | `results/*_results.csv` (automático) |",
        "| 2 Precisión | WER en STT (automático); LLM/TTS cualitativo |",
        "| 3 Costo | CSV (estimado por rates en cada script) |",
        "| 4 Privacidad | `analysis/dimensions_catalog.py` (1-5, revisar políticas) |",
        "| 5 Customización | catálogo 1-5 |",
        "| 6 Integración | catálogo 1-5 |",
        "",
        "## Servicios con datos de benchmark",
    ]
    for cat in ("llm", "stt", "tts"):
        n = len(master[master["categoria"] == cat])
        csv_exists = (RESULTS_DIR / f"{cat}_results.csv").exists()
        lines.append(f"- **{cat.upper()}**: {n} filas en matriz; CSV={'sí' if csv_exists else 'no'}")
    lines.append("\n## Mejores por dimensión (solo filas con datos)\n")
    if master["latencia_ms"].notna().any():
        best = master.loc[master["latencia_ms"].idxmin()]
        lines.append(f"- Menor latencia: **{best['servicio']}** ({best['latencia_ms']} ms)")
    if master["wer"].notna().any():
        best_w = master.loc[master["wer"].idxmin()]
        lines.append(f"- Menor WER (STT): **{best_w['servicio']}** ({best_w['wer']})")
    if master["costo_usd"].notna().any():
        best_c = master.loc[master["costo_usd"].idxmin()]
        lines.append(f"- Menor costo/llamada: **{best_c['servicio']}** (${best_c['costo_usd']})")
    for col, label in [
        ("privacidad_1_5", "Privacidad"),
        ("customizacion_1_5", "Customización"),
        ("integracion_1_5", "Integración"),
    ]:
        if master[col].notna().any():
            best_q = master.loc[master[col].idxmax()]
            lines.append(f"- Mayor {label} (catálogo): **{best_q['servicio']}** ({int(best_q[col])}/5)")

    lines.insert(0, analysis_meta_line())
    _write_md(OUT_DIR / "resumen_ejecutivo.md", "Resumen — 6 dimensiones", "\n".join(lines))

    # STT: WER por fuente de audio (Piper vs FLEURS)
    stt_df = _load_ok("stt")
    wer_src = stt_wer_by_source(stt_df)
    if not wer_src.empty:
        _write_md(
            OUT_DIR / "stt_wer_por_fuente.md",
            "STT — WER por fuente de audio",
            tabulate(wer_src, headers="keys", tablefmt="github", showindex=False),
        )

    # Matrices 5×6 por categoría (enunciado)
    for cat in ("llm", "stt", "tts"):
        m5 = build_category_matrix_5x6(cat, master)
        if m5.empty:
            continue
        _write_md(
            OUT_DIR / f"matriz_5x6_{cat}.md",
            f"Matriz 5×6 — {cat.upper()}",
            tabulate(m5, headers="keys", tablefmt="github", showindex=False, floatfmt=".4f"),
        )

    # MOS TTS desde plantilla JSON
    if MOS_FILE.exists():
        mos = json.loads(MOS_FILE.read_text(encoding="utf-8"))
        provs = mos.get("providers", [])
        if provs:
            _write_md(
                OUT_DIR / "tts_mos.md",
                "TTS — MOS (plantilla)",
                tabulate(provs, headers="keys", tablefmt="github", showindex=False),
            )

    # Combinado
    combined = []
    for _, title in DIMENSIONS:
        p = OUT_DIR / f"{title}.md"
        if p.exists():
            combined.append(p.read_text(encoding="utf-8"))
    combined.append((OUT_DIR / "matriz_6_dimensiones.md").read_text(encoding="utf-8"))
    (OUT_DIR / "todas_las_dimensiones.md").write_text("\n\n---\n\n".join(combined), encoding="utf-8")
    print(f"OK {OUT_DIR / 'todas_las_dimensiones.md'}")


if __name__ == "__main__":
    main()
