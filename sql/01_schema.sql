-- =============================================================
-- 01_schema.sql — Camada RAW
-- Tabelas espelhando os CSVs originais da Olist, com tipos e chaves.
-- =============================================================
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS raw_orders;
CREATE TABLE raw_orders (
    order_id                       TEXT PRIMARY KEY,
    customer_id                    TEXT NOT NULL,
    order_status                   TEXT NOT NULL,
    order_purchase_timestamp       TEXT NOT NULL,
    order_approved_at              TEXT,
    order_delivered_carrier_date   TEXT,
    order_delivered_customer_date  TEXT,
    order_estimated_delivery_date  TEXT
);

DROP TABLE IF EXISTS raw_order_items;
CREATE TABLE raw_order_items (
    order_id            TEXT    NOT NULL,
    order_item_id       INTEGER NOT NULL,
    product_id          TEXT    NOT NULL,
    seller_id           TEXT    NOT NULL,
    shipping_limit_date TEXT,
    price               REAL    NOT NULL,
    freight_value       REAL    NOT NULL,
    PRIMARY KEY (order_id, order_item_id)
);

DROP TABLE IF EXISTS raw_customers;
CREATE TABLE raw_customers (
    customer_id              TEXT PRIMARY KEY,
    customer_unique_id       TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city            TEXT,
    customer_state           TEXT
);

DROP TABLE IF EXISTS raw_order_reviews;
CREATE TABLE raw_order_reviews (
    review_id               TEXT NOT NULL,
    order_id                TEXT NOT NULL,
    review_score            INTEGER,
    review_comment_title    TEXT,
    review_comment_message  TEXT,
    review_creation_date    TEXT,
    review_answer_timestamp TEXT
);

DROP TABLE IF EXISTS raw_order_payments;
CREATE TABLE raw_order_payments (
    order_id             TEXT    NOT NULL,
    payment_sequential   INTEGER NOT NULL,
    payment_type         TEXT,
    payment_installments INTEGER,
    payment_value        REAL,
    PRIMARY KEY (order_id, payment_sequential)
);

DROP TABLE IF EXISTS raw_products;
CREATE TABLE raw_products (
    product_id                 TEXT PRIMARY KEY,
    product_category_name      TEXT,
    product_name_lenght        INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty         INTEGER,
    product_weight_g           REAL,
    product_length_cm          REAL,
    product_height_cm          REAL,
    product_width_cm           REAL
);

DROP TABLE IF EXISTS raw_sellers;
CREATE TABLE raw_sellers (
    seller_id              TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city            TEXT,
    seller_state           TEXT
);

DROP TABLE IF EXISTS raw_category_translation;
CREATE TABLE raw_category_translation (
    product_category_name         TEXT PRIMARY KEY,
    product_category_name_english TEXT
);

-- Tabela de apoio: UF -> região (IBGE)
DROP TABLE IF EXISTS ref_uf_regiao;
CREATE TABLE ref_uf_regiao (uf TEXT PRIMARY KEY, regiao TEXT NOT NULL);
INSERT INTO ref_uf_regiao VALUES
 ('AC','Norte'),('AP','Norte'),('AM','Norte'),('PA','Norte'),('RO','Norte'),('RR','Norte'),('TO','Norte'),
 ('AL','Nordeste'),('BA','Nordeste'),('CE','Nordeste'),('MA','Nordeste'),('PB','Nordeste'),('PE','Nordeste'),
 ('PI','Nordeste'),('RN','Nordeste'),('SE','Nordeste'),
 ('DF','Centro-Oeste'),('GO','Centro-Oeste'),('MT','Centro-Oeste'),('MS','Centro-Oeste'),
 ('ES','Sudeste'),('MG','Sudeste'),('RJ','Sudeste'),('SP','Sudeste'),
 ('PR','Sul'),('RS','Sul'),('SC','Sul');
