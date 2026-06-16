"""Arma las 6 dimensiones del enunciado y las guarda en docs/dimensiones_datos/."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

import json

from analysis.chart_theme import apply_theme, qualitative_cmap, save_figure, style_axes
from analysis.aggregate import (
    aggregate_category,
    build_category_matrix_5x6,
    format_matrix_for_display,
    load_category_df,
    stt_wer_by_source,
)
from analysis.dimensions_catalog import QUALITATIVE
from common.paths import docs_dir, project_root, results_dir

PROJECT_ROOT = project_root()
RESULTS_DIR = results_dir()
OUT_DIR = docs_dir() / "dimensiones_datos"
CHARTS_DIR = docs_dir() / "graficos_generados"
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
        else:
            row["privacidad_1_5"] = row["customizacion_1_5"] = row["integracion_1_5"] = None

        # Texto de precisión que va en la matriz
        if cat == "stt" and row.get("wer") is not None:
            row["precision_resumen"] = f"WER={row['wer']}"
        elif cat == "llm":
            row["precision_resumen"] = "Coherencia (revisión manual)"
        else:
            row["precision_resumen"] = "MOS 1-5 (escucha manual)"

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
    apply_theme()
    pivot = sub.pivot_table(index="servicio", values=col, aggfunc="first")
    fig, ax = plt.subplots(figsize=(7, max(4.5, len(pivot) * 0.38)))
    cmap = qualitative_cmap()
    im = ax.imshow(pivot.values, aspect="auto", cmap=cmap, vmin=1, vmax=5)
    ax.set_xticks([0])
    ax.set_xticklabels([title], fontsize=9, fontweight="600")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8.5)
    for i, v in enumerate(pivot.values.flatten()):
        txt_color = "white" if float(v) >= 3.5 else "#1E293B"
        ax.text(0, i, f"{int(v)}", ha="center", va="center", color=txt_color, fontsize=10, fontweight="bold")
    cbar = plt.colorbar(im, ax=ax, label="Puntuación 1-5", shrink=0.85)
    cbar.ax.tick_params(labelsize=8)
    style_axes(ax, title=title)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    save_figure(fig, CHARTS_DIR / fname, dpi=160)
    print(f"OK {(CHARTS_DIR / fname).relative_to(PROJECT_ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    master_rows = _build_master_rows()
    master = pd.DataFrame(master_rows)

    # Dimensión 1: latencia
    lat = master[["servicio", "latencia_ms", "ttft_ms", "categoria"]].copy()
    lat = lat.dropna(subset=["latencia_ms"], how="all")
    body = tabulate(lat, headers="keys", tablefmt="github", showindex=False, floatfmt=".2f")
    body += "\n\n*TTFT solo aplica a LLM con streaming.*\n"
    _write_md(OUT_DIR / "1_latencia.md", "Dimensión 1: Latencia empírica", body)

    # Dimensión 2: precisión
    prec = master[["servicio", "categoria", "wer", "precision_resumen"]].copy()
    _write_md(
        OUT_DIR / "2_precision.md",
        "Dimensión 2: Precisión y calidad",
        tabulate(prec, headers="keys", tablefmt="github", showindex=False),
    )

    # Dimensión 3: costo
    cost = master[["servicio", "costo_usd", "categoria"]].copy()
    cost = cost[cost["costo_usd"].notna()]
    _write_md(
        OUT_DIR / "3_costo.md",
        "Dimensión 3: Costo (USD por llamada, estimado)",
        tabulate(cost.round(6), headers="keys", tablefmt="github", showindex=False),
    )

    # Dimensiones 4-6 (catálogo cualitativo)
    for key, col, title, fname in [
        ("4_privacidad", "privacidad_1_5", "Privacidad y gobernanza", "heatmap_privacidad.png"),
        ("5_customizacion", "customizacion_1_5", "Customización", "heatmap_customizacion.png"),
        ("6_integracion", "integracion_1_5", "Integración", "heatmap_integracion.png"),
    ]:
        sub = master[["servicio", col]].dropna(subset=[col])
        tbl = tabulate(sub, headers="keys", tablefmt="github", showindex=False)
        _write_md(OUT_DIR / f"{key}.md", f"Dimensión: {title}", tbl)
        _heatmap_qualitative(master, col, title, fname)

    # Matriz 15×6
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
    matrix = format_matrix_for_display(master[matrix_cols])
    matriz_tbl = tabulate(matrix, headers="keys", tablefmt="github", showindex=False, floatfmt=".4f")
    matriz_body = (
        "*Los 15 servicios en las seis dimensiones del enunciado. "
        "WER solo en STT; TTFT solo en LLM; Priv./Cust./Integr. van de 1 a 5. "
        "Gráficos en `docs/graficos_generados/`.*\n\n"
        f"{matriz_tbl}\n"
    )
    _write_md(
        OUT_DIR / "matriz_6_dimensiones.md",
        "Matriz maestra: 6 dimensiones × servicios",
        matriz_body,
    )

    # WER STT agrupado por fuente de audio (solo tabla + figura)
    stt_df = _load_ok("stt")
    wer_src = stt_wer_by_source(stt_df)
    if not wer_src.empty:
        wer_body = tabulate(wer_src, headers="keys", tablefmt="github", showindex=False)
        wer_body += (
            "\n\n![WER por fuente de audio (STT)](graficos_generados/stt_wer_por_fuente.png)\n\n"
            "*Figura: WER promedio por proveedor y tipo de audio (Piper sintético vs FLEURS "
            "humano vs Common Voice). Barras más bajas = mejor transcripción.*\n"
        )
        _write_md(OUT_DIR / "stt_wer_por_fuente.md", "STT: WER por fuente de audio", wer_body)

    # Matrices 5×6 por categoría
    for cat in ("llm", "stt", "tts"):
        m5 = build_category_matrix_5x6(cat, master)
        if m5.empty:
            continue
        prefix = ""
        if cat == "llm":
            prefix = (
                "*Desglose de la matriz maestra por capa del pipeline (LLM, STT, TTS).*\n\n"
            )
        _write_md(
            OUT_DIR / f"matriz_5x6_{cat}.md",
            f"Matriz 5×6 ({cat.upper()})",
            prefix
            + f"#### {cat.upper()}\n\n"
            + tabulate(m5, headers="keys", tablefmt="github", showindex=False, floatfmt=".4f"),
        )  # m5 ya viene con etiquetas cortas vía format_matrix_for_display

    # MOS TTS desde plantilla JSON (solo tabla)
    if MOS_FILE.exists():
        mos = json.loads(MOS_FILE.read_text(encoding="utf-8"))
        provs = mos.get("providers", [])
        if provs:
            mos_body = ""
            if mos.get("evaluador"):
                mos_body += (
                    f"*Evaluador: {mos['evaluador']} · "
                    f"{mos.get('metodo', 'MOS inteligibilidad + naturalidad')}*\n\n"
                )
            mos_body += tabulate(provs, headers="keys", tablefmt="github", showindex=False)
            _write_md(
                OUT_DIR / "tts_mos.md",
                "TTS: MOS (inteligibilidad y naturalidad)",
                mos_body,
            )

    # Combinado de tablas (repositorio)
    combined = []
    for key, _ in DIMENSIONS:
        p = OUT_DIR / f"{key}.md"
        if p.exists():
            combined.append(p.read_text(encoding="utf-8"))
    matriz_path = OUT_DIR / "matriz_6_dimensiones.md"
    if matriz_path.exists():
        combined.append(matriz_path.read_text(encoding="utf-8"))
    if combined:
        (OUT_DIR / "todas_las_dimensiones.md").write_text("\n\n---\n\n".join(combined), encoding="utf-8")
        print(f"OK {OUT_DIR / 'todas_las_dimensiones.md'}")


if __name__ == "__main__":
    main()
