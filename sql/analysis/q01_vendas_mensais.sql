-- Q1. Como evoluíram receita, pedidos e ticket médio mês a mês?
-- Considera pedidos válidos; exclui meses de borda com poucos registros (2016-09..12 e 2018-09+).
SELECT
    purchase_month                              AS mes,
    COUNT(*)                                    AS pedidos,
    ROUND(SUM(order_value), 2)                  AS receita,
    ROUND(AVG(order_value), 2)                  AS ticket_medio,
    COUNT(DISTINCT customer_unique_id)          AS clientes
FROM vw_valid_orders
WHERE purchase_month BETWEEN '2017-01' AND '2018-08'
GROUP BY purchase_month
ORDER BY purchase_month;
