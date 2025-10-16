-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 🛒 Retail ABAC Demo - SQL Notebook
-- MAGIC 
-- MAGIC ## Overview
-- MAGIC This SQL notebook deploys a complete Retail industry ABAC demo with:
-- MAGIC - **5 tables**: customers, products, orders, order_items, reviews
-- MAGIC - **7 masking functions**: email, phone, credit card, amount bucketing, etc.
-- MAGIC - **26 sample rows** of realistic retail data
-- MAGIC 
-- MAGIC ## Prerequisites
-- MAGIC - Unity Catalog access
-- MAGIC - CREATE SCHEMA permission on a catalog
-- MAGIC - SQL Warehouse or Cluster attached to this notebook
-- MAGIC 
-- MAGIC ## Instructions
-- MAGIC 1. **Attach** this notebook to a SQL Warehouse or Cluster
-- MAGIC 2. **Update** the catalog name in the cell below (Cell 2)
-- MAGIC 3. **Run All** cells
-- MAGIC 
-- MAGIC ✅ **Deployment time: < 5 minutes**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Step 1: Configuration
-- MAGIC **⚠️ UPDATE THIS:** Change `apscat` to your catalog name

-- COMMAND ----------

-- Configuration - UPDATE THIS LINE!
USE CATALOG apscat;  -- ⚠️ CHANGE THIS to your catalog name

CREATE SCHEMA IF NOT EXISTS retail
COMMENT 'Retail ABAC demo - E-commerce data with PII masking';

USE SCHEMA retail;

SELECT '🎯 Deploying to: ' || current_catalog() || '.' || current_schema() AS deployment_target;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Step 2: Create Masking Functions
-- MAGIC These functions mask sensitive retail data (PII, financial info, etc.)

-- COMMAND ----------

-- Function 1: Email Masking (shows domain only)
CREATE OR REPLACE FUNCTION mask_email(email STRING) 
RETURNS STRING
COMMENT 'Mask email address showing only domain for privacy'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN email NOT LIKE '%@%' THEN '****' 
  ELSE CONCAT('****@', SPLIT(email, '@')[1]) 
END;

SELECT '✅ Function created: mask_email' AS status;

-- COMMAND ----------

-- Function 2: Phone Masking (shows last 4 digits)
CREATE OR REPLACE FUNCTION mask_phone(phone STRING) 
RETURNS STRING
COMMENT 'Mask phone number showing only last 4 digits'
RETURN CASE 
  WHEN phone IS NULL THEN phone
  ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4)) 
END;

SELECT '✅ Function created: mask_phone' AS status;

-- COMMAND ----------

-- Function 3: Credit Card Masking (PCI-DSS compliant)
CREATE OR REPLACE FUNCTION mask_credit_card_last4(card STRING) 
RETURNS STRING
COMMENT 'PCI-DSS compliant credit card masking - shows last 4 digits'
RETURN CASE 
  WHEN card IS NULL THEN card
  WHEN LENGTH(card) < 4 THEN '****' 
  ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card, '[^0-9]', ''), 4)) 
END;

SELECT '✅ Function created: mask_credit_card_last4' AS status;

-- COMMAND ----------

-- Function 4: Order Amount Bucketing
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

SELECT '✅ Function created: mask_order_amount_bucket' AS status;

-- COMMAND ----------

-- Function 5: Customer ID Deterministic Hashing
CREATE OR REPLACE FUNCTION mask_customer_id_hash(customer_id STRING) 
RETURNS STRING
COMMENT 'Deterministic hash for cross-table customer analytics'
RETURN CASE 
  WHEN customer_id IS NULL THEN customer_id
  ELSE CONCAT('CUST_', SUBSTRING(SHA2(customer_id, 256), 1, 12)) 
END;

SELECT '✅ Function created: mask_customer_id_hash' AS status;

-- COMMAND ----------

-- Function 6: Product Cost Masking (margin protection)
CREATE OR REPLACE FUNCTION mask_product_cost(cost DECIMAL(12,2)) 
RETURNS STRING
COMMENT 'Redact wholesale cost to protect margins'
RETURN '[REDACTED]';

SELECT '✅ Function created: mask_product_cost' AS status;

-- COMMAND ----------

-- Function 7: IP Address Masking
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING) 
RETURNS STRING
COMMENT 'Mask last octet of IP address for privacy'
RETURN CASE 
  WHEN ip IS NULL OR ip NOT LIKE '%.%.%.%' THEN ip
  ELSE CONCAT(SPLIT(ip, '\\.')[0], '.', SPLIT(ip, '\\.')[1], '.', SPLIT(ip, '\\.')[2], '.***') 
END;

SELECT '✅ Function created: mask_ip_address' AS status;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ✅ **7 masking functions created successfully!**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Step 3: Create Tables with Sample Data

-- COMMAND ----------

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

SELECT '✅ Table created: customers (' || COUNT(*) || ' rows)' AS status FROM customers;

-- COMMAND ----------

-- Table 2: PRODUCTS (with cost data)
DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id STRING NOT NULL,
  product_name STRING,
  category STRING,
  price DECIMAL(10,2),
  cost DECIMAL(10,2),
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

SELECT '✅ Table created: products (' || COUNT(*) || ' rows)' AS status FROM products;

-- COMMAND ----------

-- Table 3: ORDERS (with transaction data)
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
  order_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  order_date TIMESTAMP,
  total_amount DECIMAL(12,2),
  payment_method STRING,
  ip_address STRING,
  status STRING,
  CONSTRAINT pk_orders PRIMARY KEY (order_id)
) USING DELTA
COMMENT 'Order transactions with customer linkage';

INSERT INTO orders VALUES
('O-5001', 'C-1001', timestamp('2024-03-01 10:30:00'), 1329.98, 'Credit Card', '192.168.1.100', 'Completed'),
('O-5002', 'C-1002', timestamp('2024-03-02 14:15:00'), 219.98, 'PayPal', '10.0.0.50', 'Completed'),
('O-5003', 'C-1003', timestamp('2024-03-03 09:45:00'), 89.99, 'Credit Card', '172.16.0.25', 'Completed'),
('O-5004', 'C-1004', timestamp('2024-03-04 16:20:00'), 179.98, 'Debit Card', '192.168.2.75', 'Shipped'),
('O-5005', 'C-1005', timestamp('2024-03-05 11:10:00'), 1299.99, 'Credit Card', '10.1.1.100', 'Processing');

SELECT '✅ Table created: orders (' || COUNT(*) || ' rows)' AS status FROM orders;

-- COMMAND ----------

-- Table 4: ORDER_ITEMS
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
('OI-8003', 'O-5002', 'P-104', 1, 129.99),
('OI-8004', 'O-5002', 'P-103', 1, 89.99),
('OI-8005', 'O-5003', 'P-103', 1, 89.99),
('OI-8006', 'O-5004', 'P-104', 1, 129.99),
('OI-8007', 'O-5004', 'P-105', 1, 49.99),
('OI-8008', 'O-5005', 'P-101', 1, 1299.99);

SELECT '✅ Table created: order_items (' || COUNT(*) || ' rows)' AS status FROM order_items;

-- COMMAND ----------

-- Table 5: REVIEWS
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

SELECT '✅ Table created: reviews (' || COUNT(*) || ' rows)' AS status FROM reviews;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ✅ **5 tables created with 26 sample rows total!**

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Step 4: Verification & Testing
-- MAGIC Let's test our masking functions!

-- COMMAND ----------

-- Show all table counts
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 1: Email Masking

-- COMMAND ----------

SELECT 
  customer_id,
  email AS original_email,
  mask_email(email) AS masked_email
FROM customers
LIMIT 3;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 2: Phone Masking

-- COMMAND ----------

SELECT 
  customer_id,
  phone AS original_phone,
  mask_phone(phone) AS masked_phone
FROM customers
LIMIT 3;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 3: Order Amount Bucketing

-- COMMAND ----------

SELECT 
  order_id,
  total_amount AS original_amount,
  mask_order_amount_bucket(total_amount) AS amount_bucket
FROM orders;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 4: Customer ID Hashing (Deterministic)

-- COMMAND ----------

SELECT 
  customer_id AS original_id,
  mask_customer_id_hash(customer_id) AS hashed_id,
  mask_customer_id_hash(customer_id) AS hashed_again_same
FROM customers
LIMIT 3;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ℹ️ **Note:** The two hashed columns should be identical (deterministic hashing)

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 5: IP Address Masking

-- COMMAND ----------

SELECT 
  order_id,
  ip_address AS original_ip,
  mask_ip_address(ip_address) AS masked_ip
FROM orders
LIMIT 3;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 6: Product Cost Masking (Margin Protection)

-- COMMAND ----------

SELECT 
  product_name,
  price AS sale_price,
  cost AS actual_cost,
  mask_product_cost(cost) AS masked_cost
FROM products
LIMIT 3;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Test 7: Complex Analytics with Masking

-- COMMAND ----------

SELECT 
  mask_customer_id_hash(c.customer_id) AS masked_customer,
  c.state,
  COUNT(o.order_id) AS order_count,
  mask_order_amount_bucket(SUM(o.total_amount)) AS total_spent_bucket
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.state
ORDER BY order_count DESC;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # ✅ Deployment Complete!
-- MAGIC 
-- MAGIC ## What Was Created
-- MAGIC - **Schema**: `<your_catalog>.retail`
-- MAGIC - **Tables**: 5 (customers, products, orders, order_items, reviews)
-- MAGIC - **Functions**: 7 masking functions
-- MAGIC - **Data**: 26 sample rows
-- MAGIC 
-- MAGIC ## Next Steps
-- MAGIC 1. ✅ Test masking functions in your queries
-- MAGIC 2. Apply tags to sensitive columns for policy-based masking
-- MAGIC 3. Create ABAC policies to enforce masking for specific groups
-- MAGIC 
-- MAGIC ## Example Usage
-- MAGIC ```sql
-- MAGIC SELECT 
-- MAGIC   mask_email(email) AS masked_email,
-- MAGIC   mask_phone(phone) AS masked_phone
-- MAGIC FROM customers;
-- MAGIC ```
-- MAGIC 
-- MAGIC ## Example ABAC Policy (requires admin permissions)
-- MAGIC ```sql
-- MAGIC CREATE POLICY retail_email_masking
-- MAGIC ON SCHEMA <your_catalog>.retail
-- MAGIC COLUMN MASK mask_email
-- MAGIC TO `users` EXCEPT `admins`
-- MAGIC FOR TABLES
-- MAGIC MATCH COLUMNS hasTagValue('pii_level', 'High') AS email_cols
-- MAGIC ON COLUMN email_cols;
-- MAGIC ```
-- MAGIC 
-- MAGIC 📚 **For more information**, see README.md in the retail directory.
