-- Q7. Segmentação RFM: recência, frequência e valor monetário por cliente.
-- Data de referência: um dia após a última compra da base.
WITH ref AS (SELECT date(MAX(purchased_at), '+1 day') AS d FROM vw_valid_orders),
cli AS (
    SELECT customer_unique_id,
           CAST(julianday((SELECT d FROM ref)) - julianday(MAX(purchased_at)) AS INT) AS recencia,
           COUNT(*)            AS frequencia,
           SUM(order_value)    AS monetario
    FROM vw_valid_orders
    GROUP BY customer_unique_id
),
score AS (
    SELECT *,
           6 - NTILE(5) OVER (ORDER BY recencia)                          AS r,
           CASE WHEN frequencia >= 3 THEN 5 WHEN frequencia = 2 THEN 4 ELSE 1 END AS f,
           NTILE(5) OVER (ORDER BY monetario)                             AS m
    FROM cli
)
SELECT
    CASE
        WHEN f >= 4 AND r >= 4             THEN '1. Campeões'
        WHEN f >= 4                        THEN '2. Recorrentes em risco'
        WHEN r >= 4 AND m >= 4             THEN '3. Novos de alto valor'
        WHEN r >= 4                        THEN '4. Novos'
        WHEN m >= 4                        THEN '5. Alto valor inativos'
        ELSE                                    '6. Inativos'
    END                                    AS segmento,
    COUNT(*)                               AS clientes,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_clientes,
    ROUND(SUM(monetario), 2)               AS receita,
    ROUND(100.0 * SUM(monetario) / SUM(SUM(monetario)) OVER (), 1) AS pct_receita,
    ROUND(AVG(recencia), 0)                AS recencia_media_dias,
    ROUND(AVG(monetario), 2)               AS valor_medio
FROM score
GROUP BY segmento
ORDER BY segmento;
