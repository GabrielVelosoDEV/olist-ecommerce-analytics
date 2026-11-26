-- =============================================================
-- 03_marts.sql — Camada MARTS
-- Tabelas analíticas materializadas, prontas para BI.
-- =============================================================

-- Fato de pedidos (grão: 1 linha por pedido)
DROP TABLE IF EXISTS fct_orders;
CREATE TABLE fct_orders AS
WITH items AS (
    SELECT order_id,
           COUNT(*)            AS n_items,
           SUM(price)          AS items_value,
           SUM(freight_value)  AS freight_value,
           COUNT(DISTINCT seller_id) AS n_sellers
    FROM stg_order_items
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_unique_id,
    c.state,
    c.region,
    o.order_status,
    o.purchased_at,
    o.purchase_month,
    i.n_items,
    i.n_sellers,
    ROUND(i.items_value, 2)                      AS items_value,
    ROUND(i.freight_value, 2)                    AS freight_value,
    ROUND(i.items_value + i.freight_value, 2)    AS order_value,
    o.delivery_days,
    o.delay_days,
    o.on_time,
    r.review_score,
    p.main_payment_type,
    p.installments
FROM stg_orders o
JOIN stg_customers c   ON c.customer_id = o.customer_id
JOIN items i           ON i.order_id = o.order_id
LEFT JOIN stg_reviews r  ON r.order_id = o.order_id
LEFT JOIN stg_payments p ON p.order_id = o.order_id;

CREATE INDEX idx_fct_orders_month    ON fct_orders(purchase_month);
CREATE INDEX idx_fct_orders_customer ON fct_orders(customer_unique_id);
CREATE INDEX idx_fct_orders_state    ON fct_orders(state);

-- Fato de itens (grão: 1 linha por item vendido), só pedidos válidos
DROP TABLE IF EXISTS fct_order_items;
CREATE TABLE fct_order_items AS
SELECT
    i.*,
    f.state,
    f.region,
    f.purchase_month,
    f.order_status
FROM stg_order_items i
JOIN fct_orders f ON f.order_id = i.order_id;

CREATE INDEX idx_fct_items_category ON fct_order_items(category_pt);

-- Visão "pedidos válidos": exclui cancelados e indisponíveis
DROP VIEW IF EXISTS vw_valid_orders;
CREATE VIEW vw_valid_orders AS
SELECT * FROM fct_orders
WHERE order_status NOT IN ('canceled', 'unavailable');
