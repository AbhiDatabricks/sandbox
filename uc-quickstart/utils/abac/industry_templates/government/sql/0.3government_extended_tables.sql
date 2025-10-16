-- GOVERNMENT EXTENDED
USE CATALOG apscat; USE SCHEMA government;
DROP TABLE IF EXISTS violations;
CREATE TABLE violations (violation_id STRING, citizen_id STRING, violation_type STRING, fine DECIMAL(8,2),
violation_date DATE, PRIMARY KEY (violation_id)) USING DELTA;
INSERT INTO violations VALUES ('V-1', 'CZ-1001', 'Speeding', 150.00, '2024-02-10'), ('V-2', 'CZ-1002', 'Parking', 50.00, '2024-03-05');
SELECT 'violations' AS tbl, COUNT(*) AS cnt FROM violations;
