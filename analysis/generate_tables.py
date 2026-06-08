"""Genera tablas comparativas por categoría (última corrida filtrada)."""

from __future__ import annotations



from pathlib import Path



from tabulate import tabulate



from analysis.aggregate import aggregate_category, analysis_meta_line, load_category_df



PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUT_DIR = PROJECT_ROOT / "docs" / "tablas_generadas"





def _format_table(df):

    out = df.copy()

    if "costo_usd_prom" in out.columns:

        out["costo_usd_prom"] = out["costo_usd_prom"].map(

            lambda x: f"{x:.6f}" if x == x else ""

        )

    for col in ("latencia_ms_prom", "latencia_ms_std", "latencia_ms_p95", "ttft_ms_prom", "calidad_prom"):

        if col in out.columns:

            out[col] = out[col].round(2)

    return out





def main() -> None:

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sections: list[str] = []

    meta = analysis_meta_line()



    for category in ("llm", "stt", "tts"):

        df = load_category_df(category, latest_only=True)

        if df.empty:

            print(f"[WARN] Sin datos OK para {category}")

            continue

        agg = aggregate_category(df, category)

        out_md = OUT_DIR / f"tabla_{category}.md"

        body = tabulate(_format_table(agg), headers="keys", tablefmt="github", showindex=False)

        content = f"# Resumen comparativo - {category.upper()}\n\n{meta}\n\n{body}\n"

        out_md.write_text(content, encoding="utf-8")

        print(f"OK {out_md.relative_to(PROJECT_ROOT)}")

        sections.append(content)



    if sections:

        combined = OUT_DIR / "todas_las_tablas.md"

        combined.write_text("\n\n---\n\n".join(sections), encoding="utf-8")

        print(f"OK {combined.relative_to(PROJECT_ROOT)}")





if __name__ == "__main__":

    main()


