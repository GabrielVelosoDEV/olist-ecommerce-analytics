-- =============================================================
-- 02_staging.sql — Camada STAGING
-- Limpeza, padronização e regras de negócio básicas.
-- =============================================================

-- Pedidos: datas convertidas e métricas de prazo calculadas
DROP VIEW IF EXISTS stg_orders;
CREATE VIEW stg_orders AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    datetime(o.order_purchase_timestamp)                           AS purchased_at,
    strftime('%Y-%m', o.order_purchase_timestamp)                  AS purchase_month,
    datetime(o.order_approved_at)                                  AS approved_at,
    datetime(o.order_delivered_customer_date)                      AS delivered_at,
    date(o.order_estimated_delivery_date)                          AS estimated_at,
    ROUND(julianday(o.order_delivered_customer_date)
        - julianday(o.order_purchase_timestamp), 1)                AS delivery_days,
    ROUND(julianday(date(o.order_delivered_customer_date))
        - julianday(date(o.order_estimated_delivery_date)), 0)     AS delay_days,
    CASE
        WHEN o.order_delivered_customer_date IS NULL THEN NULL
        WHEN date(o.order_delivered_customer_date) <= date(o.order_estimated_delivery_date) THEN 1
        ELSE 0
    END                                                            AS on_time
FROM raw_orders o;

-- Itens: categoria traduzida e com fallback para "sem_categoria"
DROP VIEW IF EXISTS stg_order_items;
CREATE VIEW stg_order_items AS
SELECT
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    i.price,
    i.freight_value,
    COALESCE(p.product_category_name, 'sem_categoria')             AS category_pt,
    COALESCE(t.product_category_name_english, 'uncategorized')     AS category_en,
    p.product_weight_g
FROM raw_order_items i
LEFT JOIN raw_products p             ON p.product_id = i.product_id
LEFT JOIN raw_category_translation t ON t.product_category_name = p.product_category_name;

-- Clientes com região
DROP VIEW IF EXISTS stg_customers;
CREATE VIEW stg_customers AS
SELECT
    c.customer_id,
    c.customer_unique_id,
    UPPER(TRIM(c.customer_state))  AS state,
    r.regiao                       AS region,
    LOWER(TRIM(c.customer_city))   AS city
FROM raw_customers c
LEFT JOIN ref_uf_regiao r ON r.uf = UPPER(TRIM(c.customer_state));

-- Avaliações: um pedido pode ter mais de uma; fica a mais recente
DROP VIEW IF EXISTS stg_reviews;
CREATE VIEW stg_reviews AS
SELECT order_id, review_score
FROM (
    SELECT order_id, review_score,
           ROW_NUMBER() OVER (PARTITION BY order_id
                              ORDER BY review_answer_timestamp DESC) AS rn
    FROM raw_order_reviews
)
WHERE rn = 1;

-- Pagamentos consolidados por pedido
DROP VIEW IF EXISTS stg_payments;
CREATE VIEW stg_payments AS
SELECT
    order_id,
    SUM(payment_value)                                   AS paid_value,
    MAX(payment_installments)                            AS installments,
    -- forma de pagamento com maior valor no pedido
    (SELECT p2.payment_type FROM raw_order_payments p2
      WHERE p2.order_id = p.order_id
      ORDER BY p2.payment_value DESC LIMIT 1)            AS main_payment_type
FROM raw_order_payments p
GROUP BY order_id;
