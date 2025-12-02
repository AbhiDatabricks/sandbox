"""
Telco Industry ABAC Template
"""

INDUSTRY_NAME = "Telco"
INDUSTRY_DESCRIPTION = "Telecommunications data protection with subscriber privacy"

FUNCTIONS_SQL = """
-- TELCO ABAC FUNCTIONS
CREATE OR REPLACE FUNCTION mask_phone_number(phone STRING) RETURNS STRING
COMMENT 'Phone masking' RETURN CASE WHEN phone IS NULL THEN phone ELSE CONCAT('XXX-XXX-', RIGHT(phone, 4)) END;

CREATE OR REPLACE FUNCTION mask_imei(imei STRING) RETURNS STRING
COMMENT 'IMEI last 4' RETURN CASE WHEN imei IS NULL THEN imei ELSE CONCAT('***********', RIGHT(imei, 4)) END;

CREATE OR REPLACE FUNCTION mask_usage_bucket(gb DECIMAL(10,2)) RETURNS STRING
COMMENT 'Usage ranges' RETURN CASE WHEN gb IS NULL THEN 'Unknown' WHEN gb < 1 THEN '<1GB'
WHEN gb < 5 THEN '1-5GB' WHEN gb < 10 THEN '5-10GB' ELSE '10GB+' END;

CREATE OR REPLACE FUNCTION mask_subscriber_id_hash(id STRING) RETURNS STRING
COMMENT 'Deterministic sub ID' RETURN CONCAT('SUB_', SUBSTRING(SHA2(id, 256), 1, 12));

CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING) RETURNS STRING
COMMENT 'IP masking' RETURN CASE WHEN ip IS NULL THEN ip ELSE CONCAT(SPLIT(ip, '\\.')[0], '.', SPLIT(ip, '\\.')[1], '.', SPLIT(ip, '\\.')[2], '.***') END;

SELECT '✅ Telco functions created!' AS status;
"""

TAG_DEFINITIONS = [
    ("pii_type_telco", "Telco PII data types", [
        "subscriber_name", "phone_number", "email", "address", 
        "imsi", "imei", "account_number", "usage_data"
    ]),
    ("data_classification_telco", "Data classification levels", [
        "Highly_Confidential", "Confidential", "Internal", "Public"
    ]),
    ("regulatory_compliance_telco", "Regulatory compliance requirements", [
        "GDPR", "CPNI", "CALEA", "None"
    ]),
    ("subscriber_type_telco", "Subscriber type classification", [
        "Enterprise", "Business", "Consumer", "Government"
    ]),
]

ABAC_POLICIES_SQL = """
-- ABAC policies for telco to be defined
"""

TEST_TABLES_SQL = """
-- TELCO DATABASE SCHEMA
CREATE SCHEMA IF NOT EXISTS telco; DROP TABLE IF EXISTS subscribers;
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

-- TELCO EXTENDED
DROP TABLE IF EXISTS devices;
CREATE TABLE devices (device_id STRING, subscriber_id STRING, imei STRING, device_model STRING,
PRIMARY KEY (device_id)) USING DELTA;
INSERT INTO devices VALUES
('D-1', 'S-1001', '123456789012345', 'iPhone 14'),
('D-2', 'S-1002', '234567890123456', 'Samsung S23'),
('D-3', 'S-1003', '345678901234567', 'Google Pixel');

SELECT 'devices' AS tbl, COUNT(*) AS cnt FROM devices;
"""

TAG_APPLICATIONS_SQL = """
-- Tag applications for telco to be defined
"""

TEST_TABLES = ["subscribers_test", "accounts_test", "call_records_test", 
               "data_usage_test", "network_devices_test", "billing_test"]
