"""Gera o dashboard estático (docs/index.html) publicado no GitHub Pages.

Uso:
    python src/build_dashboard.py     # requer reports/ gerado por src/analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "reports" / "results"
OUT = ROOT / "docs" / "index.html"


def brl(v: float) -> str:
    return f"R$ {v:,.0f}".replace(",", ".")


def load() -> dict:
    r = {p.stem: pd.read_csv(p) for p in RES.glob("q*.csv")}
    k = json.loads((ROOT / "reports" / "kpis.json").read_text(encoding="utf-8"))
    mensal = r["q01_vendas_mensais"]
    entrega = r["q04_entrega_vs_avaliacao"]
    uf = r["q02_receita_por_uf"].head(10)
    rfm = r["q07_rfm"]
    pag = r["q08_pagamentos"]
    atraso = r["q05_atraso_por_uf"].head(8)
    cat = r["q03_categorias_pareto"].head(10)
    nome_pag = {"credit_card": "Cartão de crédito", "boleto": "Boleto", "voucher": "Voucher", "debit_card": "Débito"}
    return {
        "kpis": k,
        "mensal": {"labels": mensal["mes"].tolist(), "receita": mensal["receita"].round(0).tolist(),
                   "pedidos": mensal["pedidos"].tolist()},
        "entrega": {"labels": [s.split(". ", 1)[1] for s in entrega["faixa_entrega"]],
                    "nota": entrega["nota_media"].tolist(), "ruins": entrega["pct_notas_1_2"].tolist()},
        "uf": {"labels": uf["uf"].tolist(), "share": uf["share_receita_pct"].tolist(),
               "frete": uf["frete_sobre_produto_pct"].tolist()},
        "rfm": {"labels": [s.split(". ", 1)[1] for s in rfm["segmento"]],
                "clientes": rfm["pct_clientes"].tolist(), "receita": rfm["pct_receita"].tolist()},
        "pag": {"labels": [nome_pag.get(x, x) for x in pag["meio_pagamento"]], "pct": pag["pct_pedidos"].tolist()},
        "atraso": atraso[["uf", "dias_entrega_medio", "pct_no_prazo", "nota_media"]].to_dict("records"),
        "cat": cat[["categoria", "receita", "preco_medio", "share_acumulado_pct"]].to_dict("records"),
    }


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Olist E-commerce Analytics — Gabriel Veloso</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--bg:#f7f8fa;--card:#fff;--ink:#111827;--mute:#6b7280;--line:#e5e7eb;--acc:#2563eb;--acc2:#93c5fd;--bad:#dc2626;--warn:#f59e0b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{background:#0f172a;color:#fff;padding:40px 24px 34px}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
header .k{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#93c5fd}
header h1{font-size:34px;margin:8px 0 8px;letter-spacing:-.02em}
header p{color:#cbd5e1;max-width:760px;margin:0}
header a{color:#93c5fd}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin:-22px auto 26px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.kpi b{display:block;font-size:24px;letter-spacing:-.02em}.kpi span{font-size:12.5px;color:var(--mute)}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px}
.card h2{font-size:16px;margin:0 0 4px}.card .q{font-size:13px;color:var(--mute);margin:0 0 14px}
.card .ins{font-size:13.5px;margin:12px 0 0;padding-top:12px;border-top:1px solid var(--line)}
.full{grid-column:1/-1}
canvas{max-height:300px}
table{width:100%;border-collapse:collapse;font-size:13.5px}th,td{padding:7px 6px;border-bottom:1px solid var(--line);text-align:right}
th:first-child,td:first-child{text-align:left}th{color:var(--mute);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
section.rec{margin:26px 0}.rec ol{margin:8px 0 0;padding-left:20px}.rec li{margin:6px 0}
footer{color:var(--mute);font-size:13px;padding:24px 0 40px}
@media(max-width:820px){.grid{grid-template-columns:1fr}header h1{font-size:26px}}
</style>
</head>
<body>
<header><div class="wrap">
  <div class="k">Análise de dados · Inteligência de mercado</div>
  <h1>E-commerce brasileiro: o que 98 mil pedidos reais revelam</h1>
  <p>Base pública da Olist (2016–2018) modelada em SQL — camadas raw, staging e marts — e analisada com Python.
  Código em <a href="https://github.com/GabrielVelosoDEV/olist-ecommerce-analytics">github.com/GabrielVelosoDEV/olist-ecommerce-analytics</a>.</p>
</div></header>

<div class="wrap">
  <div class="kpis">
    <div class="kpi"><b>__RECEITA__</b><span>receita de pedidos válidos</span></div>
    <div class="kpi"><b>__PEDIDOS__</b><span>pedidos · __CLIENTES__ clientes</span></div>
    <div class="kpi"><b>__TICKET__</b><span>ticket médio</span></div>
    <div class="kpi"><b>+__CRESC__%</b><span>receita 1º sem/18 vs 1º sem/17</span></div>
    <div class="kpi"><b>__RECOMPRA__%</b><span>clientes que compraram 2+ vezes</span></div>
    <div class="kpi"><b>__NOTA__</b><span>nota média · __PRAZO__% entregues no prazo</span></div>
  </div>

  <div class="grid">
    <div class="card full">
      <h2>Receita e pedidos por mês</h2>
      <p class="q">Como o negócio cresceu? (jan/2017 – ago/2018)</p>
      <canvas id="cMensal"></canvas>
      <p class="ins"><b>Leitura:</b> a receita quase triplicou em um ano e o pico foi a Black Friday de nov/2017. Em 2018 o crescimento estabiliza perto de R$ 1 mi/mês, sinal de que a próxima alavanca não é só aquisição.</p>
    </div>

    <div class="card">
      <h2>Atraso na entrega x avaliação</h2>
      <p class="q">O prazo de entrega afeta a satisfação?</p>
      <canvas id="cEntrega"></canvas>
      <p class="ins"><b>Leitura:</b> a nota cai de __NOTAPRAZO__ (no prazo) para __NOTA7__ quando o atraso passa de 7 dias, e __RUINS__% desses pedidos recebem nota 1 ou 2. Logística é o maior detrator de reputação.</p>
    </div>

    <div class="card">
      <h2>Onde está a receita</h2>
      <p class="q">Participação das 10 maiores UFs</p>
      <canvas id="cUF"></canvas>
      <p class="ins"><b>Leitura:</b> SP sozinho responde por __SP__% da receita e o Sudeste por __SUD__%. Fora do Sudeste o frete pesa mais sobre o valor do produto, o que limita a expansão regional.</p>
    </div>

    <div class="card">
      <h2>Segmentação RFM</h2>
      <p class="q">Quem são os clientes que geram valor?</p>
      <canvas id="cRFM"></canvas>
      <p class="ins"><b>Leitura:</b> só __RECOMPRA__% dos clientes voltam a comprar. Os "alto valor inativos" concentram a maior fatia da receita histórica — é a base natural para campanhas de reativação.</p>
    </div>

    <div class="card">
      <h2>Meios de pagamento</h2>
      <p class="q">Como o cliente paga?</p>
      <canvas id="cPag"></canvas>
      <p class="ins"><b>Leitura:</b> cartão de crédito domina (__CARTAO__% dos pedidos) com média de 3,6 parcelas: condições de parcelamento são parte central da oferta.</p>
    </div>

    <div class="card">
      <h2>UFs com pior desempenho logístico</h2>
      <p class="q">Menor % de entregas no prazo (mín. 100 pedidos)</p>
      <table><thead><tr><th>UF</th><th>Dias p/ entregar</th><th>% no prazo</th><th>Nota</th></tr></thead><tbody id="tAtraso"></tbody></table>
    </div>

    <div class="card">
      <h2>Categorias líderes (curva ABC)</h2>
      <p class="q">__CATA__ de __CATT__ categorias fazem 80% da receita</p>
      <table><thead><tr><th>Categoria</th><th>Receita</th><th>Preço médio</th><th>% acum.</th></tr></thead><tbody id="tCat"></tbody></table>
    </div>
  </div>

  <section class="rec card">
    <h2>Recomendações</h2>
    <ol>
      <li><b>Atacar o atraso antes de ampliar o alcance:</b> priorizar transportadoras e prazos estimados no Nordeste, onde estão as menores taxas de entrega no prazo.</li>
      <li><b>Programa de recompra:</b> com recompra de __RECOMPRA__%, uma régua de pós-venda para os segmentos "novos de alto valor" e "alto valor inativos" tem o maior retorno potencial.</li>
      <li><b>Gestão de sellers:</b> os 10% maiores vendedores fazem __TOP10__% da receita; vale um programa de contas-chave e de qualidade de entrega para eles.</li>
      <li><b>Frete regional:</b> subsidiar ou renegociar frete nas UFs onde ele passa de 20% do valor do produto para destravar demanda fora do Sudeste.</li>
    </ol>
  </section>

  <footer>Dados: <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce">Brazilian E-Commerce Public Dataset by Olist</a> (CC BY-NC-SA 4.0). Análise: Gabriel Veloso · <a href="https://www.linkedin.com/in/gabrielvelosodev/">LinkedIn</a> · <a href="https://github.com/GabrielVelosoDEV">GitHub</a></footer>
</div>

<script>
const D = __DATA__;
Chart.defaults.font.family = "Inter,system-ui,sans-serif"; Chart.defaults.color = "#6b7280";
const brl = v => "R$ " + (v >= 1e6 ? (v/1e6).toFixed(1) + " mi" : (v/1e3).toFixed(0) + " mil");
new Chart(cMensal, {data: {labels: D.mensal.labels, datasets: [
  {type: "line", label: "Receita", data: D.mensal.receita, borderColor: "#2563eb", backgroundColor: "#2563eb", yAxisID: "y", tension: .25, pointRadius: 2.5},
  {type: "bar", label: "Pedidos", data: D.mensal.pedidos, backgroundColor: "#dbeafe", yAxisID: "y1"}]},
  options: {interaction: {mode: "index", intersect: false}, scales: {y: {ticks: {callback: brl}}, y1: {position: "right", grid: {display: false}}},
  plugins: {tooltip: {callbacks: {label: c => c.dataset.label === "Receita" ? "Receita: " + brl(c.raw) : "Pedidos: " + c.raw.toLocaleString("pt-BR")}}}}});
new Chart(cEntrega, {type: "bar", data: {labels: D.entrega.labels, datasets: [{label: "Nota média", data: D.entrega.nota,
  backgroundColor: ["#2563eb", "#2563eb", "#f59e0b", "#dc2626", "#dc2626"]}]},
  options: {indexAxis: "y", plugins: {legend: {display: false}}, scales: {x: {min: 0, max: 5}}}});
new Chart(cUF, {type: "bar", data: {labels: D.uf.labels, datasets: [{label: "% da receita", data: D.uf.share,
  backgroundColor: D.uf.labels.map(u => u === "SP" ? "#2563eb" : "#93c5fd")}]},
  options: {plugins: {legend: {display: false}}, scales: {y: {ticks: {callback: v => v + "%"}}}}});
new Chart(cRFM, {type: "bar", data: {labels: D.rfm.labels, datasets: [
  {label: "% clientes", data: D.rfm.clientes, backgroundColor: "#93c5fd"}, {label: "% receita", data: D.rfm.receita, backgroundColor: "#2563eb"}]},
  options: {indexAxis: "y", scales: {x: {ticks: {callback: v => v + "%"}}}}});
new Chart(cPag, {type: "doughnut", data: {labels: D.pag.labels, datasets: [{data: D.pag.pct,
  backgroundColor: ["#2563eb", "#93c5fd", "#f59e0b", "#d1d5db"]}]}, options: {plugins: {legend: {position: "right"}}}});
tAtraso.innerHTML = D.atraso.map(r => `<tr><td>${r.uf}</td><td>${r.dias_entrega_medio.toFixed(1)}</td><td>${r.pct_no_prazo.toFixed(1)}%</td><td>${r.nota_media.toFixed(2)}</td></tr>`).join("");
tCat.innerHTML = D.cat.map(r => `<tr><td>${r.categoria.replaceAll("_", " ")}</td><td>${brl(r.receita)}</td><td>R$ ${r.preco_medio.toFixed(2).replace(".", ",")}</td><td>${r.share_acumulado_pct.toFixed(1)}%</td></tr>`).join("");
</script>
</body>
</html>
"""


def main() -> None:
    d = load()
    k = d["kpis"]
    html = TEMPLATE
    repl = {
        "__RECEITA__": f"R$ {k['receita']/1e6:.1f} mi".replace(".", ","),
        "__PEDIDOS__": f"{k['pedidos']:,}".replace(",", "."),
        "__CLIENTES__": f"{k['clientes']:,}".replace(",", "."),
        "__TICKET__": f"R$ {k['ticket_medio']:.2f}".replace(".", ","),
        "__CRESC__": f"{k['crescimento_receita_1s18_vs_1s17_pct']:.0f}",
        "__RECOMPRA__": f"{k['taxa_recompra_pct']:.1f}".replace(".", ","),
        "__NOTA__": f"{k['nota_media']:.2f}".replace(".", ","),
        "__PRAZO__": f"{k['pct_no_prazo']:.0f}",
        "__NOTAPRAZO__": f"{k['nota_no_prazo']:.2f}".replace(".", ","),
        "__NOTA7__": f"{k['nota_atraso_7d']:.2f}".replace(".", ","),
        "__RUINS__": f"{k['pct_notas_ruins_atraso_7d']:.0f}",
        "__SP__": f"{k['share_sp_pct']:.0f}",
        "__SUD__": f"{k['share_sudeste_pct']:.0f}",
        "__CARTAO__": f"{k['share_cartao_pct']:.0f}",
        "__TOP10__": f"{k['share_top10_vendedores_pct']:.0f}",
        "__CATA__": str(k["categorias_classe_a"]),
        "__CATT__": str(k["categorias_total"]),
        "__DATA__": json.dumps(d, ensure_ascii=False),
    }
    for a, b in repl.items():
        html = html.replace(a, b)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"dashboard gerado em {OUT.relative_to(ROOT)} ({len(html)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
