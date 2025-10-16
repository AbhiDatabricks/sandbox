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
