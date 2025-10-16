-- INSURANCE DATABASE SCHEMA
USE CATALOG apscat; CREATE SCHEMA IF NOT EXISTS insurance; USE SCHEMA insurance;

DROP TABLE IF EXISTS policyholders;
CREATE TABLE policyholders (policyholder_id STRING, first_name STRING, last_name STRING, ssn STRING,
email STRING, phone STRING, PRIMARY KEY (policyholder_id)) USING DELTA;
INSERT INTO policyholders VALUES
('PH-1001', 'John', 'Smith', '123-45-6789', 'john@email.com', '555-0101'),
('PH-1002', 'Sarah', 'Johnson', '234-56-7890', 'sarah@email.com', '555-0102'),
('PH-1003', 'Mike', 'Williams', '345-67-8901', 'mike@email.com', '555-0103');

DROP TABLE IF EXISTS policies;
CREATE TABLE policies (policy_id STRING, policyholder_id STRING, policy_number STRING, policy_type STRING,
premium DECIMAL(10,2), coverage_amount DECIMAL(12,2), PRIMARY KEY (policy_id)) USING DELTA;
INSERT INTO policies VALUES
('P-5001', 'PH-1001', 'POL123456', 'Auto', 1200.00, 50000.00),
('P-5002', 'PH-1002', 'POL234567', 'Home', 1800.00, 300000.00),
('P-5003', 'PH-1003', 'POL345678', 'Life', 600.00, 500000.00);

DROP TABLE IF EXISTS claims;
CREATE TABLE claims (claim_id STRING, policy_id STRING, claim_amount DECIMAL(12,2), claim_date DATE,
status STRING, PRIMARY KEY (claim_id)) USING DELTA;
INSERT INTO claims VALUES
('C-1001', 'P-5001', 8500.00, '2024-02-15', 'Approved'),
('C-1002', 'P-5002', 15000.00, '2024-03-01', 'Pending'),
('C-1003', 'P-5003', 0.00, '2024-03-10', 'Denied');

SELECT 'policyholders' AS tbl, COUNT(*) AS cnt FROM policyholders
UNION ALL SELECT 'policies', COUNT(*) FROM policies
UNION ALL SELECT 'claims', COUNT(*) FROM claims;
