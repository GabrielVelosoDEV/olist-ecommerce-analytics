-- Q6. Os clientes voltam? Retenção por coorte de primeira compra (meses 1 a 6).
WITH primeira AS (
    SELECT customer_unique_id, MIN(purchase_month) AS coorte
    FROM vw_valid_orders
    GROUP BY customer_unique_id
),
atividade AS (
    SELECT DISTINCT v.customer_unique_id, p.coorte,
           (CAST(substr(v.purchase_month,1,4) AS INT) - CAST(substr(p.coorte,1,4) AS INT)) * 12
         + (CAST(substr(v.purchase_month,6,2) AS INT) - CAST(substr(p.coorte,6,2) AS INT)) AS mes_relativo
    FROM vw_valid_orders v
    JOIN primeira p USING (customer_unique_id)
)
SELECT
    coorte,
    COUNT(DISTINCT CASE WHEN mes_relativo = 0 THEN customer_unique_id END) AS clientes,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN mes_relativo = 1 THEN customer_unique_id END)
        / COUNT(DISTINCT CASE WHEN mes_relativo = 0 THEN customer_unique_id END), 2) AS m1,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN mes_relativo = 2 THEN customer_unique_id END)
        / COUNT(DISTINCT CASE WHEN mes_relativo = 0 THEN customer_unique_id END), 2) AS m2,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN mes_relativo = 3 THEN customer_unique_id END)
        / COUNT(DISTINCT CASE WHEN mes_relativo = 0 THEN customer_unique_id END), 2) AS m3,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN mes_relativo BETWEEN 1 AND 6 THEN customer_unique_id END)
        / COUNT(DISTINCT CASE WHEN mes_relativo = 0 THEN customer_unique_id END), 2) AS ate_m6
FROM atividade
WHERE coorte BETWEEN '2017-01' AND '2018-02'
GROUP BY coorte
ORDER BY coorte;
