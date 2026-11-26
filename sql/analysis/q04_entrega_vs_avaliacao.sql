-- Q4. Atraso na entrega derruba a avaliação? Nota média por faixa de atraso.
SELECT
    CASE
        WHEN delay_days <= -10 THEN '1. 10+ dias adiantado'
        WHEN delay_days <= 0   THEN '2. No prazo'
        WHEN delay_days <= 3   THEN '3. 1 a 3 dias de atraso'
        WHEN delay_days <= 7   THEN '4. 4 a 7 dias de atraso'
        ELSE                        '5. Mais de 7 dias de atraso'
    END                                         AS faixa_entrega,
    COUNT(*)                                    AS pedidos,
    ROUND(AVG(review_score), 2)                 AS nota_media,
    ROUND(100.0 * AVG(review_score <= 2), 1)    AS pct_notas_1_2
FROM fct_orders
WHERE order_status = 'delivered'
  AND delay_days IS NOT NULL
  AND review_score IS NOT NULL
GROUP BY faixa_entrega
ORDER BY faixa_entrega;
