-- INSURANCE EXTENDED
USE CATALOG apscat; USE SCHEMA insurance;
DROP TABLE IF EXISTS premiums;
CREATE TABLE premiums (payment_id STRING, policy_id STRING, amount DECIMAL(10,2), payment_date DATE,
PRIMARY KEY (payment_id)) USING DELTA;
INSERT INTO premiums VALUES ('PM-1', 'P-5001', 100.00, '2024-01-01'), ('PM-2', 'P-5002', 150.00, '2024-01-01');
SELECT 'premiums' AS tbl, COUNT(*) AS cnt FROM premiums;
