SELECT COUNT(*) AS ventes,
       SUM(quantity) AS articles,
       SUM(amount_millimes) AS millimes
FROM fact_sales;
