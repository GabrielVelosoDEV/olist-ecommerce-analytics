-- Q2. Onde está a receita? Participação por UF, ticket e frete relativo.
WITH base AS (
    SELECT state, region,
           COUNT(*)            AS pedidos,
           SUM(order_value)    AS receita,
           SUM(items_value)    AS valor_produtos,
           SUM(freight_value)  AS frete
    FROM vw_valid_orders
    GROUP BY state, region
)
SELECT
    state  AS uf,
    region AS regiao,
    pedidos,
    ROUND(receita, 2)                                         AS receita,
    ROUND(100.0 * receita / SUM(receita) OVER (), 2)          AS share_receita_pct,
    ROUND(receita / pedidos, 2)                               AS ticket_medio,
    ROUND(100.0 * frete / valor_produtos, 1)                  AS frete_sobre_produto_pct
FROM base
ORDER BY receita DESC;
