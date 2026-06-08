"""Genera gráficos latencia-vs-costo y barras por categoría (última corrida)."""

from __future__ import annotations



from pathlib import Path



import matplotlib.pyplot as plt



from analysis.aggregate import aggregate_category, load_category_df, stt_wer_by_source



PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUT_DIR = PROJECT_ROOT / "docs" / "graficos_generados"





def _scatter_latency_cost(agg, category: str) -> None:

    fig, ax = plt.subplots(figsize=(9, 5.5))

    for _, row in agg.iterrows():

        ax.scatter(row["latencia_ms_prom"], row["costo_usd_prom"] or 0.0, s=120)

        ax.annotate(

            f'{row["provider"]}\n{row["model"]}',

            (row["latencia_ms_prom"], row["costo_usd_prom"] or 0.0),

            xytext=(6, 6),

            textcoords="offset points",

            fontsize=9,

        )

    ax.set_xlabel("Latencia promedio (ms)")

    ax.set_ylabel("Costo promedio por llamada (USD)")

    ax.set_title(f"Latencia vs Costo - {category.upper()}")

    ax.grid(True, alpha=0.3)

    fig.tight_layout()

    out = OUT_DIR / f"{category}_latencia_vs_costo.png"

    fig.savefig(out, dpi=140)

    plt.close(fig)

    print(f"OK {out.relative_to(PROJECT_ROOT)}")





def _bar_metric(agg, metric: str, category: str, ylabel: str, fname: str) -> None:

    sub = agg.dropna(subset=[metric])

    if sub.empty:

        return

    fig, ax = plt.subplots(figsize=(9, 5))

    labels = [f"{p}\n{m}" for p, m in zip(sub["provider"], sub["model"])]

    ax.bar(labels, sub[metric])

    ax.set_ylabel(ylabel)

    ax.set_title(f"{ylabel} - {category.upper()}")

    ax.grid(True, axis="y", alpha=0.3)

    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")

    fig.tight_layout()

    out = OUT_DIR / fname

    fig.savefig(out, dpi=140)

    plt.close(fig)

    print(f"OK {out.relative_to(PROJECT_ROOT)}")





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


def _stt_wer_by_source_chart(df) -> None:
    wer_df = stt_wer_by_source(df)
    if wer_df.empty:
        return
    pivot = wer_df.pivot(index="provider", columns="audio_source", values="wer_prom")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    pivot.plot(kind="bar", ax=ax, rot=0)
    ax.set_ylabel("WER promedio")
    ax.set_title("STT — WER por fuente de audio (Piper vs FLEURS)")
    ax.legend(title="Fuente")
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out = OUT_DIR / "stt_wer_por_fuente.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    print(f"OK {out.relative_to(PROJECT_ROOT)}")





if __name__ == "__main__":

    main()


