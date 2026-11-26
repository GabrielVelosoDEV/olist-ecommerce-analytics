-- Q3. Quais categorias concentram a receita? Curva ABC (Pareto).
WITH cat AS (
    SELECT category_pt AS categoria,
           COUNT(*)            AS itens,
           SUM(price)          AS receita,
           AVG(price)          AS preco_medio
    FROM fct_order_items
    WHERE order_status NOT IN ('canceled','unavailable')
    GROUP BY category_pt
),
acc AS (
    SELECT *,
           SUM(receita) OVER (ORDER BY receita DESC
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
             / SUM(receita) OVER () AS share_acumulado
    FROM cat
)
SELECT
    categoria, itens,
    ROUND(receita, 2)                    AS receita,
    ROUND(preco_medio, 2)                AS preco_medio,
    ROUND(100 * share_acumulado, 1)      AS share_acumulado_pct,
    CASE WHEN share_acumulado <= 0.80 THEN 'A'
         WHEN share_acumulado <= 0.95 THEN 'B'
         ELSE 'C' END                    AS classe_abc
FROM acc
ORDER BY receita DESC;
