-- RETAIL TEST QUERIES
USE CATALOG apscat; USE SCHEMA retail;
SELECT '=== TABLE COUNTS ===' AS section;
SELECT 'customers' AS tbl, COUNT(*) AS cnt FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders;

SELECT '=== EMAIL MASKING ===' AS section;
SELECT email AS orig, apscat.retail.mask_email(email) AS masked FROM customers LIMIT 3;

SELECT '=== PHONE MASKING ===' AS section;
SELECT phone AS orig, apscat.retail.mask_phone(phone) AS masked FROM customers LIMIT 3;

SELECT '=== AMOUNT BUCKETING ===' AS section;
SELECT total_amount AS orig, apscat.retail.mask_order_amount_bucket(total_amount) AS bucket FROM orders;

SELECT '=== CUSTOMER ID HASHING ===' AS section;
SELECT customer_id AS orig, apscat.retail.mask_customer_id_hash(customer_id) AS hashed FROM customers LIMIT 3;

SELECT '✅ Retail tests complete!' AS status;
