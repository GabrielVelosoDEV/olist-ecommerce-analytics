-- Q9. Quão concentrada é a base de vendedores? Receita dos top 10% vs. o resto.
WITH s AS (
    SELECT seller_id, SUM(price) AS receita
    FROM fct_order_items
    WHERE order_status NOT IN ('canceled','unavailable')
    GROUP BY seller_id
),
d AS (SELECT *, NTILE(10) OVER (ORDER BY receita DESC) AS decil FROM s)
SELECT
    decil,
    COUNT(*)                                            AS vendedores,
    ROUND(SUM(receita), 2)                              AS receita,
    ROUND(100.0 * SUM(receita) / SUM(SUM(receita)) OVER (), 1) AS pct_receita
FROM d
GROUP BY decil
ORDER BY decil;
