SELECT ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue_gbp
FROM order_items oi
JOIN invoices i ON i.invoice_no = oi.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0;

SELECT TO_CHAR(DATE_TRUNC('month', i.invoice_date), 'YYYY-MM') AS month,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY DATE_TRUNC('month', i.invoice_date)
ORDER BY DATE_TRUNC('month', i.invoice_date);

SELECT p.stock_code,
       COALESCE(p.description, 'Description unavailable') AS product,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp
FROM products p
JOIN order_items oi ON oi.stock_code = p.stock_code
JOIN invoices i ON i.invoice_no = oi.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY p.stock_code, p.description
ORDER BY revenue_gbp DESC
LIMIT 10;

SELECT i.country,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp,
       COUNT(DISTINCT i.invoice_no) AS order_count
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY i.country
ORDER BY revenue_gbp DESC;

SELECT c.customer_id,
       c.country,
       COUNT(DISTINCT i.invoice_no) AS order_count
FROM customers c
JOIN invoices i ON i.customer_id = c.customer_id
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY c.customer_id, c.country
ORDER BY order_count DESC, c.customer_id
LIMIT 20;

WITH order_totals AS (
    SELECT i.invoice_no,
           SUM(oi.quantity * oi.unit_price) AS order_value
    FROM invoices i
    JOIN order_items oi ON oi.invoice_no = i.invoice_no
    WHERE NOT i.is_cancelled
      AND oi.quantity > 0
      AND oi.unit_price > 0
    GROUP BY i.invoice_no
)
SELECT ROUND(AVG(order_value), 2) AS average_order_value_gbp
FROM order_totals;

SELECT p.stock_code,
       COALESCE(p.description, 'Description unavailable') AS product,
       SUM(oi.quantity) AS units_sold
FROM products p
JOIN order_items oi ON oi.stock_code = p.stock_code
JOIN invoices i ON i.invoice_no = oi.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY p.stock_code, p.description
ORDER BY units_sold DESC
LIMIT 20;

SELECT i.country,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY i.country
HAVING SUM(oi.quantity * oi.unit_price) > 100000
ORDER BY revenue_gbp DESC;

SELECT c.customer_id,
       c.country,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS spending_gbp
FROM customers c
JOIN invoices i ON i.customer_id = c.customer_id
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY c.customer_id, c.country
HAVING SUM(oi.quantity * oi.unit_price) > 10000
ORDER BY spending_gbp DESC;

SELECT TO_CHAR(DATE_TRUNC('month', i.invoice_date), 'YYYY-MM') AS month,
       COUNT(DISTINCT i.invoice_no) AS order_count
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY DATE_TRUNC('month', i.invoice_date)
ORDER BY DATE_TRUNC('month', i.invoice_date);
