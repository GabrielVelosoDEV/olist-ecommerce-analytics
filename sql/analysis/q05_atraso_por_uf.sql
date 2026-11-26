-- Q5. Quais UFs têm pior logística? Prazo real, atraso e % no prazo.
SELECT
    state                                       AS uf,
    region                                      AS regiao,
    COUNT(*)                                    AS pedidos_entregues,
    ROUND(AVG(delivery_days), 1)                AS dias_entrega_medio,
    ROUND(100.0 * AVG(on_time), 1)              AS pct_no_prazo,
    ROUND(AVG(review_score), 2)                 AS nota_media
FROM fct_orders
WHERE order_status = 'delivered' AND on_time IS NOT NULL
GROUP BY state, region
HAVING COUNT(*) >= 100
ORDER BY pct_no_prazo ASC;
