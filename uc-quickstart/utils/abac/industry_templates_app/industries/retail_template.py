"""
Retail Industry ABAC Template
"""

INDUSTRY_NAME = "Retail"
INDUSTRY_DESCRIPTION = "Retail customer data protection and PCI compliance"

FUNCTIONS_SQL = """
-- RETAIL & E-COMMERCE ABAC FUNCTIONS
USE CATALOG apscat;
USE SCHEMA retail;

-- 1. EMAIL MASKING
CREATE OR REPLACE FUNCTION mask_email(email STRING) RETURNS STRING
COMMENT 'Mask email local part' RETURN CASE WHEN email IS NULL OR email = '' THEN email
WHEN email NOT LIKE '%@%' THEN '****' ELSE CONCAT('****@', SPLIT(email, '@')[1]) END;

-- 2. PHONE MASKING  
CREATE OR REPLACE FUNCTION mask_phone(phone STRING) RETURNS STRING
COMMENT 'Mask phone showing last 4' RETURN CASE WHEN phone IS NULL THEN phone
ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4)) END;

-- 3. CREDIT CARD LAST 4
CREATE OR REPLACE FUNCTION mask_credit_card_last4(card STRING) RETURNS STRING
COMMENT 'Show last 4 of card' RETURN CASE WHEN card IS NULL THEN card
WHEN LENGTH(card) < 4 THEN '****' ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card, '[^0-9]', ''), 4)) END;

-- 4. ADDRESS PARTIAL (City, State only)
CREATE OR REPLACE FUNCTION mask_address_partial(address STRING) RETURNS STRING
COMMENT 'Show city/state only' RETURN CASE WHEN address IS NULL THEN address
WHEN address LIKE '%,%' THEN CONCAT(SPLIT(address, ',')[1], ', ', SUBSTRING(SPLIT(address, ',')[2], 1, 2))
ELSE '[REDACTED]' END;

-- 5. ORDER AMOUNT BUCKETING
CREATE OR REPLACE FUNCTION mask_order_amount_bucket(amount DECIMAL(12,2)) RETURNS STRING
COMMENT 'Order amount ranges' RETURN CASE WHEN amount IS NULL THEN 'Unknown' WHEN amount < 0 THEN 'Refund'
WHEN amount = 0 THEN '$0' WHEN amount < 50 THEN '$0-$50' WHEN amount < 100 THEN '$50-$100'
WHEN amount < 250 THEN '$100-$250' WHEN amount < 500 THEN '$250-$500' WHEN amount < 1000 THEN '$500-$1K'
ELSE '$1K+' END;

-- 6. CUSTOMER ID DETERMINISTIC
CREATE OR REPLACE FUNCTION mask_customer_id_hash(customer_id STRING) RETURNS STRING
COMMENT 'Deterministic customer ID' RETURN CASE WHEN customer_id IS NULL THEN customer_id
ELSE CONCAT('CUST_', SUBSTRING(SHA2(customer_id, 256), 1, 12)) END;

-- 7. PRODUCT COST MASKING
CREATE OR REPLACE FUNCTION mask_product_cost(cost DECIMAL(12,2)) RETURNS STRING
COMMENT 'Hide wholesale cost' RETURN '[REDACTED]';

-- 8. IP ADDRESS MASKING
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING) RETURNS STRING
COMMENT 'Mask last octet' RETURN CASE WHEN ip IS NULL OR ip NOT LIKE '%.%.%.%' THEN ip
ELSE CONCAT(SPLIT(ip, '\\.')[0], '.', SPLIT(ip, '\\.')[1], '.', SPLIT(ip, '\\.')[2], '.***') END;

-- 9. BUSINESS HOURS FILTER
CREATE OR REPLACE FUNCTION filter_business_hours() RETURNS BOOLEAN
COMMENT 'Business hours only' RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

SELECT '✅ Retail ABAC functions created!' AS status;
"""

TAG_DEFINITIONS = [
    ("pii_type_retail", "Retail PII data types", [
        "customer_name", "email", "phone", "address", "credit_card", 
        "loyalty_id", "purchase_history"
    ]),
    ("pci_compliance_retail", "PCI-DSS compliance requirement", [
        "Required", "Not_Required"
    ]),
    ("customer_tier_retail", "Customer loyalty tier", [
        "Platinum", "Gold", "Silver", "Bronze", "Standard"
    ]),
    ("data_classification_retail", "Data classification levels", [
        "Confidential", "Internal", "Public"
    ]),
]

ABAC_POLICIES_SQL = """
-- ABAC policies for retail to be defined
"""

TEST_TABLES_SQL = """
-- RETAIL DATABASE SCHEMA
USE CATALOG apscat;
CREATE SCHEMA IF NOT EXISTS retail;
USE SCHEMA retail;

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (customer_id STRING, first_name STRING, last_name STRING, email STRING, phone STRING, 
address STRING, city STRING, state STRING, zip STRING, created_date DATE, PRIMARY KEY (customer_id)) USING DELTA;
INSERT INTO customers VALUES
('C-1001', 'John', 'Smith', 'john.s@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001', '2023-01-15'),
('C-1002', 'Sarah', 'Johnson', 'sarah.j@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001', '2023-02-20'),
('C-1003', 'Michael', 'Williams', 'm.will@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601', '2023-03-10'),
('C-1004', 'Emily', 'Brown', 'ebrown@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001', '2023-04-05'),
('C-1005', 'David', 'Jones', 'djones@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001', '2023-05-12');

DROP TABLE IF EXISTS products;
CREATE TABLE products (product_id STRING, product_name STRING, category STRING, price DECIMAL(10,2), 
cost DECIMAL(10,2), stock INT, PRIMARY KEY (product_id)) USING DELTA;
INSERT INTO products VALUES
('P-101', 'Laptop Pro', 'Electronics', 1299.99, 850.00, 50),
('P-102', 'Wireless Mouse', 'Electronics', 29.99, 12.00, 200),
('P-103', 'Coffee Maker', 'Appliances', 89.99, 45.00, 75),
('P-104', 'Running Shoes', 'Apparel', 129.99, 60.00, 150),
('P-105', 'Backpack', 'Accessories', 49.99, 20.00, 100);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (order_id STRING, customer_id STRING, order_date TIMESTAMP, total_amount DECIMAL(12,2),
payment_method STRING, ip_address STRING, status STRING, PRIMARY KEY (order_id)) USING DELTA;
INSERT INTO orders VALUES
('O-5001', 'C-1001', timestamp('2024-03-01 10:30:00'), 1329.98, 'Credit Card', '192.168.1.100', 'Completed'),
('O-5002', 'C-1002', timestamp('2024-03-02 14:15:00'), 219.98, 'PayPal', '10.0.0.50', 'Completed'),
('O-5003', 'C-1003', timestamp('2024-03-03 09:45:00'), 89.99, 'Credit Card', '172.16.0.25', 'Completed'),
('O-5004', 'C-1004', timestamp('2024-03-04 16:20:00'), 179.98, 'Debit Card', '192.168.2.75', 'Shipped'),
('O-5005', 'C-1005', timestamp('2024-03-05 11:10:00'), 1299.99, 'Credit Card', '10.1.1.100', 'Processing');

SELECT 'customers' AS tbl, COUNT(*) AS cnt FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products
UNION ALL SELECT 'orders', COUNT(*) FROM orders;

-- RETAIL EXTENDED TABLES
USE CATALOG apscat; USE SCHEMA retail;

DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (item_id STRING, order_id STRING, product_id STRING, quantity INT, 
unit_price DECIMAL(10,2), PRIMARY KEY (item_id)) USING DELTA;
INSERT INTO order_items VALUES
('I-1', 'O-5001', 'P-101', 1, 1299.99), ('I-2', 'O-5001', 'P-102', 1, 29.99),
('I-3', 'O-5002', 'P-103', 1, 89.99), ('I-4', 'O-5002', 'P-104', 1, 129.99),
('I-5', 'O-5003', 'P-103', 1, 89.99), ('I-6', 'O-5004', 'P-104', 1, 129.99),
('I-7', 'O-5004', 'P-105', 1, 49.99), ('I-8', 'O-5005', 'P-101', 1, 1299.99);

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (review_id STRING, product_id STRING, customer_id STRING, rating INT,
review_text STRING, review_date DATE, PRIMARY KEY (review_id)) USING DELTA;
INSERT INTO reviews VALUES
('R-1', 'P-101', 'C-1001', 5, 'Excellent laptop!', '2024-03-10'),
('R-2', 'P-102', 'C-1002', 4, 'Good mouse', '2024-03-11'),
('R-3', 'P-103', 'C-1003', 5, 'Love this coffee maker', '2024-03-12');

SELECT 'order_items' AS tbl, COUNT(*) AS cnt FROM order_items
UNION ALL SELECT 'reviews', COUNT(*) FROM reviews;
"""

TAG_APPLICATIONS_SQL = """
-- Tag applications for retail to be defined
"""

TEST_TABLES = ["customers_test", "orders_test", "products_test", 
               "transactions_test", "loyalty_programs_test", "stores_test"]
