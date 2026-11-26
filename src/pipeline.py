"""Pipeline ELT: CSVs brutos da Olist -> SQLite (raw -> staging -> marts).

Uso:
    python src/pipeline.py            # constrói data/olist.db do zero
"""
from __future__ import annotations

import csv
import gzip
import logging
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "olist.db"
SQL_DIR = ROOT / "sql"

# arquivo bruto -> tabela raw
SOURCES = {
    "olist_orders_dataset.csv.gz": "raw_orders",
    "olist_order_items_dataset.csv.gz": "raw_order_items",
    "olist_customers_dataset.csv.gz": "raw_customers",
    "olist_order_reviews_dataset.csv.gz": "raw_order_reviews",
    "olist_order_payments_dataset.csv.gz": "raw_order_payments",
    "olist_products_dataset.csv.gz": "raw_products",
    "olist_sellers_dataset.csv.gz": "raw_sellers",
    "product_category_name_translation.csv.gz": "raw_category_translation",
}

log = logging.getLogger("pipeline")


def run_sql_file(con: sqlite3.Connection, path: Path) -> None:
    log.info("executando %s", path.relative_to(ROOT))
    con.executescript(path.read_text(encoding="utf-8"))


def load_csv(con: sqlite3.Connection, file: Path, table: str) -> int:
    """Carrega um CSV .gz em uma tabela já criada; strings vazias viram NULL."""
    with gzip.open(file, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        header = [h.lstrip("﻿") for h in next(reader)]  # remove BOM, se houver
        cols = ", ".join(header)
        marks = ", ".join("?" * len(header))
        rows = ([v if v != "" else None for v in row] for row in reader)
        cur = con.executemany(f"INSERT INTO {table} ({cols}) VALUES ({marks})", rows)
    return cur.rowcount


def build(db_path: Path = DB_PATH) -> Path:
    t0 = time.perf_counter()
    db_path.unlink(missing_ok=True)
    con = sqlite3.connect(db_path)
    try:
        run_sql_file(con, SQL_DIR / "01_schema.sql")
        for file, table in SOURCES.items():
            n = load_csv(con, RAW_DIR / file, table)
            log.info("%-26s %8d linhas", table, n)
        con.commit()
        run_sql_file(con, SQL_DIR / "02_staging.sql")
        run_sql_file(con, SQL_DIR / "03_marts.sql")
        con.commit()
        n = con.execute("SELECT COUNT(*) FROM fct_orders").fetchone()[0]
        log.info("fct_orders: %d pedidos | %.1fs", n, time.perf_counter() - t0)
    finally:
        con.close()
    return db_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    build()
