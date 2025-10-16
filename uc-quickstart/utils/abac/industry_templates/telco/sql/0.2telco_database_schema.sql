-- TELCO DATABASE SCHEMA
USE CATALOG apscat; CREATE SCHEMA IF NOT EXISTS telco; USE SCHEMA telco;

DROP TABLE IF EXISTS subscribers;
CREATE TABLE subscribers (subscriber_id STRING, phone_number STRING, email STRING, plan_name STRING,
monthly_fee DECIMAL(8,2), status STRING, PRIMARY KEY (subscriber_id)) USING DELTA;
INSERT INTO subscribers VALUES
('S-1001', '555-1001', 'john@email.com', 'Unlimited', 79.99, 'Active'),
('S-1002', '555-1002', 'sarah@email.com', 'Premium', 99.99, 'Active'),
('S-1003', '555-1003', 'mike@email.com', 'Basic', 49.99, 'Active');

DROP TABLE IF EXISTS call_records;
CREATE TABLE call_records (record_id STRING, subscriber_id STRING, call_type STRING, duration_min INT,
call_date TIMESTAMP, PRIMARY KEY (record_id)) USING DELTA;
INSERT INTO call_records VALUES
('CDR-1', 'S-1001', 'Voice', 15, timestamp('2024-03-01 10:00:00')),
('CDR-2', 'S-1002', 'Voice', 30, timestamp('2024-03-01 11:00:00')),
('CDR-3', 'S-1003', 'SMS', 0, timestamp('2024-03-01 12:00:00'));

DROP TABLE IF EXISTS data_usage;
CREATE TABLE data_usage (usage_id STRING, subscriber_id STRING, data_gb DECIMAL(10,2),
usage_date DATE, PRIMARY KEY (usage_id)) USING DELTA;
INSERT INTO data_usage VALUES
('U-1', 'S-1001', 8.5, '2024-03-01'),
('U-2', 'S-1002', 15.2, '2024-03-01'),
('U-3', 'S-1003', 2.3, '2024-03-01');

SELECT 'subscribers' AS tbl, COUNT(*) AS cnt FROM subscribers
UNION ALL SELECT 'call_records', COUNT(*) FROM call_records
UNION ALL SELECT 'data_usage', COUNT(*) FROM data_usage;
