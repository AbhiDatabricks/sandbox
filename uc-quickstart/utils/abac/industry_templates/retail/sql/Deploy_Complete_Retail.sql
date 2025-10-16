-- =====================================================================
-- RETAIL ABAC DEMO - COMPLETE DEPLOYMENT
-- =====================================================================
-- This file contains everything needed to deploy the Retail ABAC demo
-- 
-- INSTRUCTIONS:
-- 1. Update the catalog name below (change 'apscat' to your catalog)
-- 2. Run this entire file in Databricks SQL Editor or Notebook
-- 3. All tables, functions, and test data will be created
--
-- WHAT GETS CREATED:
-- - Schema: <your_catalog>.retail
-- - 5 Tables: customers, products, orders, order_items, reviews
-- - 6 Masking Functions: email, phone, credit card, amount bucketing, etc.
-- - 26 Sample rows of retail data
-- =====================================================================

-- =====================================================================
-- STEP 1: CONFIGURATION - UPDATE THIS!
-- =====================================================================
USE CATALOG apscat;  -- ⚠️ CHANGE THIS to your catalog name
CREATE SCHEMA IF NOT EXISTS retail 
COMMENT 'Retail ABAC demo - E-commerce data with PII masking';
USE SCHEMA retail;

SELECT '🎯 Deploying to: ' || current_catalog() || '.' || current_schema() AS deployment_target;

-- =====================================================================
-- STEP 2: CREATE MASKING FUNCTIONS
-- =====================================================================

-- Function 1: Email Masking (shows domain only)
CREATE OR REPLACE FUNCTION mask_email(email STRING) 
RETURNS STRING
COMMENT 'Mask email address showing only domain for privacy'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN email NOT LIKE '%@%' THEN '****' 
  ELSE CONCAT('****@', SPLIT(email, '@')[1]) 
END;

-- Function 2: Phone Masking (shows last 4 digits)
CREATE OR REPLACE FUNCTION mask_phone(phone STRING) 
RETURNS STRING
COMMENT 'Mask phone number showing only last 4 digits'
RETURN CASE 
  WHEN phone IS NULL THEN phone
  ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4)) 
END;

-- Function 3: Credit Card Masking (PCI-DSS compliant - last 4)
CREATE OR REPLACE FUNCTION mask_credit_card_last4(card STRING) 
RETURNS STRING
COMMENT 'PCI-DSS compliant credit card masking - shows last 4 digits'
RETURN CASE 
  WHEN card IS NULL THEN card
  WHEN LENGTH(card) < 4 THEN '****' 
  ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card, '[^0-9]', ''), 4)) 
END;

-- Function 4: Order Amount Bucketing (for privacy-preserving analytics)
CREATE OR REPLACE FUNCTION mask_order_amount_bucket(amount DECIMAL(12,2)) 
RETURNS STRING
COMMENT 'Bucket order amounts for privacy-preserving analytics'
RETURN CASE 
  WHEN amount IS NULL THEN 'Unknown' 
  WHEN amount < 0 THEN 'Refund'
  WHEN amount = 0 THEN '$0' 
  WHEN amount < 50 THEN '$0-$50' 
  WHEN amount < 100 THEN '$50-$100'
  WHEN amount < 250 THEN '$100-$250' 
  WHEN amount < 500 THEN '$250-$500' 
  WHEN amount < 1000 THEN '$500-$1K'
  ELSE '$1K+' 
END;

-- Function 5: Customer ID Deterministic Hashing (for cross-table analytics)
CREATE OR REPLACE FUNCTION mask_customer_id_hash(customer_id STRING) 
RETURNS STRING
COMMENT 'Deterministic hash for cross-table customer analytics while preserving privacy'
RETURN CASE 
  WHEN customer_id IS NULL THEN customer_id
  ELSE CONCAT('CUST_', SUBSTRING(SHA2(customer_id, 256), 1, 12)) 
END;

-- Function 6: Product Cost Masking (margin protection)
CREATE OR REPLACE FUNCTION mask_product_cost(cost DECIMAL(12,2)) 
RETURNS STRING
COMMENT 'Redact wholesale cost to protect margins'
RETURN '[REDACTED]';

-- Function 7: IP Address Masking (last octet)
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING) 
RETURNS STRING
COMMENT 'Mask last octet of IP address for privacy'
RETURN CASE 
  WHEN ip IS NULL OR ip NOT LIKE '%.%.%.%' THEN ip
  ELSE CONCAT(SPLIT(ip, '\\.')[0], '.', SPLIT(ip, '\\.')[1], '.', SPLIT(ip, '\\.')[2], '.***') 
END;

SELECT '✅ Step 2 Complete: 7 masking functions created' AS status;

-- =====================================================================
-- STEP 3: CREATE TABLES WITH SAMPLE DATA
-- =====================================================================

-- Table 1: CUSTOMERS (with PII data)
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  customer_id STRING NOT NULL,
  first_name STRING,
  last_name STRING,
  email STRING,
  phone STRING, 
  address STRING,
  city STRING,
  state STRING,
  zip STRING,
  created_date DATE,
  CONSTRAINT pk_customers PRIMARY KEY (customer_id)
) USING DELTA
COMMENT 'Customer master data with PII';

INSERT INTO customers VALUES
('C-1001', 'John', 'Smith', 'john.s@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001', '2023-01-15'),
('C-1002', 'Sarah', 'Johnson', 'sarah.j@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001', '2023-02-20'),
('C-1003', 'Michael', 'Williams', 'm.will@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601', '2023-03-10'),
('C-1004', 'Emily', 'Brown', 'ebrown@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001', '2023-04-05'),
('C-1005', 'David', 'Jones', 'djones@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001', '2023-05-12');

-- Table 2: PRODUCTS (with cost data - confidential)
DROP TABLE IF EXISTS products;
CREATE TABLE products (
  product_id STRING NOT NULL,
  product_name STRING,
  category STRING,
  price DECIMAL(10,2),
  cost DECIMAL(10,2),  -- Confidential: wholesale cost
  stock INT,
  CONSTRAINT pk_products PRIMARY KEY (product_id)
) USING DELTA
COMMENT 'Product catalog with confidential cost data';

INSERT INTO products VALUES
('P-101', 'Laptop Pro', 'Electronics', 1299.99, 850.00, 50),
('P-102', 'Wireless Mouse', 'Electronics', 29.99, 12.00, 200),
('P-103', 'Coffee Maker', 'Appliances', 89.99, 45.00, 75),
('P-104', 'Running Shoes', 'Apparel', 129.99, 60.00, 150),
('P-105', 'Backpack', 'Accessories', 49.99, 20.00, 100);

-- Table 3: ORDERS (with transaction data and IP addresses)
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  order_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  order_date TIMESTAMP,
  total_amount DECIMAL(12,2),
  payment_method STRING,
  ip_address STRING,  -- PII: customer IP
  status STRING,
  CONSTRAINT pk_orders PRIMARY KEY (order_id)
) USING DELTA
COMMENT 'Order transactions with customer linkage and IP tracking';

INSERT INTO orders VALUES
('O-5001', 'C-1001', timestamp('2024-03-01 10:30:00'), 1329.98, 'Credit Card', '192.168.1.100', 'Completed'),
('O-5002', 'C-1002', timestamp('2024-03-02 14:15:00'), 219.98, 'PayPal', '10.0.0.50', 'Completed'),
('O-5003', 'C-1003', timestamp('2024-03-03 09:45:00'), 89.99, 'Credit Card', '172.16.0.25', 'Completed'),
('O-5004', 'C-1004', timestamp('2024-03-04 16:20:00'), 179.98, 'Debit Card', '192.168.2.75', 'Shipped'),
('O-5005', 'C-1005', timestamp('2024-03-05 11:10:00'), 1299.99, 'Credit Card', '10.1.1.100', 'Processing');

-- Table 4: ORDER_ITEMS (line items for orders)
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
  order_item_id STRING NOT NULL,
  order_id STRING NOT NULL,
  product_id STRING NOT NULL,
  quantity INT,
  unit_price DECIMAL(10,2),
  CONSTRAINT pk_order_items PRIMARY KEY (order_item_id)
) USING DELTA
COMMENT 'Order line items';

INSERT INTO order_items VALUES
('OI-8001', 'O-5001', 'P-101', 1, 1299.99),
('OI-8002', 'O-5001', 'P-102', 1, 29.99),
('OI-8003', 'O-5002', 'O-5002', 1, 129.99),
('OI-8004', 'O-5002', 'P-103', 1, 89.99),
('OI-8005', 'O-5003', 'P-103', 1, 89.99),
('OI-8006', 'O-5004', 'P-104', 1, 129.99),
('OI-8007', 'O-5004', 'P-105', 1, 49.99),
('OI-8008', 'O-5005', 'P-101', 1, 1299.99);

-- Table 5: REVIEWS (product reviews with customer linkage)
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
  review_id STRING NOT NULL,
  product_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  rating INT,
  review_text STRING,
  review_date DATE,
  CONSTRAINT pk_reviews PRIMARY KEY (review_id)
) USING DELTA
COMMENT 'Product reviews';

INSERT INTO reviews VALUES
('R-9001', 'P-101', 'C-1001', 5, 'Excellent laptop, fast performance!', '2024-03-10'),
('R-9002', 'P-102', 'C-1002', 4, 'Good value for money', '2024-03-11'),
('R-9003', 'P-103', 'C-1003', 5, 'Perfect coffee maker, highly recommend', '2024-03-12');

SELECT '✅ Step 3 Complete: 5 tables created with 26 sample rows' AS status;

-- =====================================================================
-- STEP 4: VERIFICATION & TESTING
-- =====================================================================

-- Show table counts
SELECT 'TABLE COUNTS' AS section, '==================' AS divider;
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews;

-- Test 1: Email Masking
SELECT '==================' AS section, 'TEST 1: EMAIL MASKING' AS test_name;
SELECT 
  customer_id,
  email AS original_email,
  mask_email(email) AS masked_email
FROM customers
LIMIT 3;

-- Test 2: Phone Masking
SELECT '==================' AS section, 'TEST 2: PHONE MASKING' AS test_name;
SELECT 
  customer_id,
  phone AS original_phone,
  mask_phone(phone) AS masked_phone
FROM customers
LIMIT 3;

-- Test 3: Order Amount Bucketing
SELECT '==================' AS section, 'TEST 3: ORDER AMOUNT BUCKETING' AS test_name;
SELECT 
  order_id,
  total_amount AS original_amount,
  mask_order_amount_bucket(total_amount) AS amount_bucket
FROM orders;

-- Test 4: Customer ID Hashing (Deterministic)
SELECT '==================' AS section, 'TEST 4: CUSTOMER ID HASHING' AS test_name;
SELECT 
  customer_id AS original_id,
  mask_customer_id_hash(customer_id) AS hashed_id,
  mask_customer_id_hash(customer_id) AS hashed_again_same
FROM customers
LIMIT 3;

-- Test 5: IP Address Masking
SELECT '==================' AS section, 'TEST 5: IP ADDRESS MASKING' AS test_name;
SELECT 
  order_id,
  ip_address AS original_ip,
  mask_ip_address(ip_address) AS masked_ip
FROM orders
LIMIT 3;

-- Test 6: Product Cost Masking (Margin Protection)
SELECT '==================' AS section, 'TEST 6: COST MASKING (Margin Protection)' AS test_name;
SELECT 
  product_name,
  price AS sale_price,
  cost AS actual_cost,
  mask_product_cost(cost) AS masked_cost
FROM products
LIMIT 3;

-- Test 7: Complex Analytics with Masking
SELECT '==================' AS section, 'TEST 7: CUSTOMER ANALYTICS (with masking)' AS test_name;
SELECT 
  mask_customer_id_hash(c.customer_id) AS masked_customer,
  c.state,
  COUNT(o.order_id) AS order_count,
  mask_order_amount_bucket(SUM(o.total_amount)) AS total_spent_bucket
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.state
ORDER BY order_count DESC;

-- =====================================================================
-- DEPLOYMENT COMPLETE!
-- =====================================================================
SELECT '
=====================================================================
✅ RETAIL ABAC DEMO DEPLOYMENT COMPLETE!
=====================================================================

DEPLOYED TO: ' || current_catalog() || '.' || current_schema() || '

WHAT WAS CREATED:
- 5 Tables: customers, products, orders, order_items, reviews
- 7 Masking Functions: email, phone, credit card, amount bucketing, etc.
- 26 Sample rows of retail data

NEXT STEPS:
1. Test masking functions in your queries
2. Apply tags to sensitive columns for policy-based masking
3. Create ABAC policies to enforce masking for specific groups

EXAMPLE QUERY:
  SELECT 
    mask_email(email) AS masked_email,
    mask_phone(phone) AS masked_phone
  FROM customers;

EXAMPLE ABAC POLICY (requires admin permissions):
  CREATE POLICY retail_email_masking
  ON SCHEMA ' || current_catalog() || '.' || current_schema() || '
  COLUMN MASK mask_email
  TO `users` EXCEPT `admins`
  FOR TABLES
  MATCH COLUMNS hasTagValue(''pii_level'', ''High'') AS email_cols
  ON COLUMN email_cols;

📚 For more information, see README.md in the retail directory.
=====================================================================
' AS deployment_summary;


