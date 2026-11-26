"""Testes de qualidade de dados sobre o banco gerado pelo pipeline.

Rodam com:  pytest -q
"""
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pipeline  # noqa: E402


@pytest.fixture(scope="session")
def con(tmp_path_factory):
    db = tmp_path_factory.mktemp("db") / "olist_test.db"
    pipeline.build(db)
    c = sqlite3.connect(db)
    yield c
    c.close()


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]


def test_carga_completa(con):
    """Todas as linhas dos arquivos brutos chegaram nas tabelas raw."""
    assert scalar(con, "SELECT COUNT(*) FROM raw_orders") == 99_441
    assert scalar(con, "SELECT COUNT(*) FROM raw_order_items") == 112_650
    assert scalar(con, "SELECT COUNT(*) FROM raw_customers") == 99_441


def test_chave_unica_fct_orders(con):
    assert scalar(con, "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM fct_orders") == 0


def test_integridade_referencial(con):
    """Todo item aponta para um pedido e um produto existentes."""
    orfaos = scalar(con, """
        SELECT COUNT(*) FROM raw_order_items i
        LEFT JOIN raw_orders o   ON o.order_id = i.order_id
        LEFT JOIN raw_products p ON p.product_id = i.product_id
        WHERE o.order_id IS NULL OR p.product_id IS NULL""")
    assert orfaos == 0


def test_valores_nao_negativos(con):
    assert scalar(con, "SELECT COUNT(*) FROM fct_orders WHERE items_value < 0 OR freight_value < 0") == 0


def test_notas_no_intervalo(con):
    assert scalar(con, "SELECT COUNT(*) FROM fct_orders WHERE review_score NOT BETWEEN 1 AND 5") == 0


def test_todas_ufs_mapeadas_para_regiao(con):
    assert scalar(con, "SELECT COUNT(*) FROM fct_orders WHERE region IS NULL") == 0


def test_entrega_nao_antecede_compra(con):
    assert scalar(con, "SELECT COUNT(*) FROM fct_orders WHERE delivery_days < 0") == 0


def test_receita_bate_com_itens(con):
    """A receita da fato de pedidos é igual à soma dos itens + frete."""
    a = scalar(con, "SELECT ROUND(SUM(order_value), 0) FROM fct_orders")
    b = scalar(con, "SELECT ROUND(SUM(price + freight_value), 0) FROM fct_order_items")
    assert a == b
