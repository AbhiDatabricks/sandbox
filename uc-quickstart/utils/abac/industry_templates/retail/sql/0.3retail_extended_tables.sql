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
