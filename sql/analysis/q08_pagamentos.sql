-- Q8. Como o cliente paga? Participação, ticket e parcelamento por meio de pagamento.
SELECT
    main_payment_type                               AS meio_pagamento,
    COUNT(*)                                        AS pedidos,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_pedidos,
    ROUND(AVG(order_value), 2)                      AS ticket_medio,
    ROUND(AVG(installments), 1)                     AS parcelas_media
FROM vw_valid_orders
WHERE main_payment_type IS NOT NULL AND main_payment_type <> 'not_defined'
GROUP BY main_payment_type
ORDER BY pedidos DESC;
