SELECT s.shop_id,
       SUM(f.amount_millimes) AS millimes
FROM fact_sales AS f
JOIN dim_shop AS s ON s.shop_key = f.shop_key
GROUP BY s.shop_id
ORDER BY s.shop_id;
