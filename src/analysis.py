"""Executa as consultas de negócio, salva resultados, KPIs e gráficos.

Uso:
    python src/analysis.py      # requer data/olist.db (rode src/pipeline.py antes)
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mtick  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "olist.db"
QUERY_DIR = ROOT / "sql" / "analysis"
RESULTS_DIR = ROOT / "reports" / "results"
FIG_DIR = ROOT / "reports" / "figures"

INK, MUTED, ACCENT, ALERT, GRID = "#1f2937", "#6b7280", "#2563eb", "#dc2626", "#e5e7eb"

plt.rcParams.update({
    "figure.dpi": 130, "savefig.bbox": "tight", "font.size": 10,
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "axes.titleweight": "bold",
    "axes.titlesize": 12, "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "xtick.color": MUTED, "ytick.color": MUTED,
})

BRL = mtick.FuncFormatter(lambda v, _: f"R$ {v/1e6:.1f} mi" if v >= 1e6 else f"R$ {v/1e3:.0f} mil")


def run_queries(con: sqlite3.Connection) -> dict[str, pd.DataFrame]:
    out = {}
    for f in sorted(QUERY_DIR.glob("q*.sql")):
        df = pd.read_sql(f.read_text(encoding="utf-8"), con)
        df.to_csv(RESULTS_DIR / f"{f.stem}.csv", index=False)
        out[f.stem] = df
    return out


def kpis(con: sqlite3.Connection, r: dict[str, pd.DataFrame]) -> dict:
    q = lambda sql: con.execute(sql).fetchone()  # noqa: E731
    pedidos, receita, clientes, ticket = q(
        "SELECT COUNT(*), SUM(order_value), COUNT(DISTINCT customer_unique_id), AVG(order_value) "
        "FROM vw_valid_orders")
    recompra = q(
        "SELECT AVG(n > 1) FROM (SELECT COUNT(*) n FROM vw_valid_orders GROUP BY customer_unique_id)")[0]
    no_prazo, nota = q(
        "SELECT AVG(on_time), AVG(review_score) FROM fct_orders WHERE order_status = 'delivered'")
    entrega = r["q04_entrega_vs_avaliacao"].set_index("faixa_entrega")
    uf = r["q02_receita_por_uf"].set_index("uf")
    sud = r["q02_receita_por_uf"].query("regiao == 'Sudeste'")["share_receita_pct"].sum()
    pareto = r["q03_categorias_pareto"]
    mensal = r["q01_vendas_mensais"].set_index("mes")
    return {
        "pedidos": int(pedidos),
        "receita": round(receita, 2),
        "clientes": int(clientes),
        "ticket_medio": round(ticket, 2),
        "taxa_recompra_pct": round(100 * recompra, 2),
        "pct_no_prazo": round(100 * no_prazo, 1),
        "nota_media": round(nota, 2),
        "nota_no_prazo": float(entrega.loc["2. No prazo", "nota_media"]),
        "nota_atraso_7d": float(entrega.loc["5. Mais de 7 dias de atraso", "nota_media"]),
        "pct_notas_ruins_atraso_7d": float(entrega.loc["5. Mais de 7 dias de atraso", "pct_notas_1_2"]),
        "share_sp_pct": float(uf.loc["SP", "share_receita_pct"]),
        "share_sudeste_pct": round(float(sud), 1),
        "categorias_classe_a": int((pareto["classe_abc"] == "A").sum()),
        "categorias_total": int(len(pareto)),
        "share_top10_vendedores_pct": float(r["q09_vendedores_concentracao"].iloc[0]["pct_receita"]),
        "share_cartao_pct": float(r["q08_pagamentos"].set_index("meio_pagamento").loc["credit_card", "pct_pedidos"]),
        "crescimento_receita_1s18_vs_1s17_pct": round(
            100 * (mensal.loc["2018-01":"2018-06", "receita"].sum()
                   / mensal.loc["2017-01":"2017-06", "receita"].sum() - 1), 1),
    }


def fig_vendas(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(df["mes"], df["receita"], color=ACCENT, lw=2.2, marker="o", ms=3.5)
    peak = df.loc[df["receita"].idxmax()]
    ax.annotate(f"Black Friday\n{peak['mes']}", (peak["mes"], peak["receita"]),
                xytext=(0, 14), textcoords="offset points", ha="center", color=INK, fontsize=9)
    ax.yaxis.set_major_formatter(BRL)
    ax.set_title("Receita mensal (pedidos válidos)")
    ax.tick_params(axis="x", rotation=45)
    ax.set_ylim(0, df["receita"].max() * 1.2)
    fig.savefig(FIG_DIR / "01_receita_mensal.png")
    plt.close(fig)


def fig_entrega(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.4))
    labels = [s.split(". ", 1)[1] for s in df["faixa_entrega"]]
    colors = [ACCENT, ACCENT, "#f59e0b", ALERT, ALERT]
    bars = ax.barh(labels, df["nota_media"], color=colors)
    ax.bar_label(bars, fmt="%.2f", padding=4, color=INK)
    ax.invert_yaxis()
    ax.set_xlim(0, 5)
    ax.set_title("Nota média da avaliação por situação da entrega")
    ax.grid(axis="y", visible=False)
    fig.savefig(FIG_DIR / "02_entrega_vs_nota.png")
    plt.close(fig)


def fig_uf(df: pd.DataFrame) -> None:
    top = df.head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    bars = ax.barh(top["uf"], top["share_receita_pct"],
                   color=[ACCENT if u == "SP" else "#93c5fd" for u in top["uf"]])
    ax.bar_label(bars, fmt="%.1f%%", padding=4, color=INK)
    ax.set_title("Participação na receita — 10 maiores UFs")
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.grid(axis="y", visible=False)
    fig.savefig(FIG_DIR / "03_receita_por_uf.png")
    plt.close(fig)


def fig_pareto(df: pd.DataFrame) -> None:
    top = df.head(20)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(range(len(top)), top["receita"], color=[ACCENT if c == "A" else "#93c5fd" for c in top["classe_abc"]])
    ax.yaxis.set_major_formatter(BRL)
    ax.set_xticks(range(len(top)), top["categoria"].str.replace("_", " "), rotation=60, ha="right", fontsize=8)
    ax2 = ax.twinx()
    ax2.plot(range(len(top)), top["share_acumulado_pct"], color=INK, lw=1.6, marker="o", ms=3)
    ax2.set_ylim(0, 100)
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    ax.set_title("Curva ABC — 20 categorias com maior receita")
    fig.savefig(FIG_DIR / "04_pareto_categorias.png")
    plt.close(fig)


def fig_rfm(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 3.4))
    labels = [s.split(". ", 1)[1] for s in df["segmento"]]
    y = range(len(df))
    ax.barh([i + 0.2 for i in y], df["pct_clientes"], height=0.4, color="#93c5fd", label="% clientes")
    ax.barh([i - 0.2 for i in y], df["pct_receita"], height=0.4, color=ACCENT, label="% receita")
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Segmentação RFM — clientes x receita")
    ax.grid(axis="y", visible=False)
    fig.savefig(FIG_DIR / "05_rfm.png")
    plt.close(fig)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        r = run_queries(con)
        k = kpis(con, r)
    finally:
        con.close()
    (ROOT / "reports" / "kpis.json").write_text(json.dumps(k, indent=2, ensure_ascii=False), encoding="utf-8")
    fig_vendas(r["q01_vendas_mensais"])
    fig_entrega(r["q04_entrega_vs_avaliacao"])
    fig_uf(r["q02_receita_por_uf"])
    fig_pareto(r["q03_categorias_pareto"])
    fig_rfm(r["q07_rfm"])
    print(json.dumps(k, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
