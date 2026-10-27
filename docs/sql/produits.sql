SELECT p.product_name, SUM(f.quantity) AS articles
FROM fact_sales AS f
JOIN dim_product AS p
  ON p.product_key = f.product_key
GROUP BY p.product_name;
