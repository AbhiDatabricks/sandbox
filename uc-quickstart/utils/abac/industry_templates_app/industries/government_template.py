"""
Government Industry ABAC Template
"""

INDUSTRY_NAME = "Government"
INDUSTRY_DESCRIPTION = "Government data protection with security clearances and classifications"

FUNCTIONS_SQL = """
-- GOVERNMENT ABAC FUNCTIONS
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING) RETURNS STRING
COMMENT 'SSN masking' RETURN CASE WHEN ssn IS NULL THEN ssn ELSE CONCAT('XXX-XX-', RIGHT(REPLACE(ssn, '-', ''), 4)) END;

CREATE OR REPLACE FUNCTION mask_license_plate_partial(plate STRING) RETURNS STRING
COMMENT 'Plate partial' RETURN CASE WHEN plate IS NULL THEN plate ELSE CONCAT('***-', RIGHT(plate, 4)) END;

CREATE OR REPLACE FUNCTION mask_address_zip_only(address STRING, zip STRING) RETURNS STRING
COMMENT 'ZIP only' RETURN COALESCE(zip, '***');

CREATE OR REPLACE FUNCTION mask_tax_amount_bucket(amt DECIMAL(12,2)) RETURNS STRING
COMMENT 'Tax ranges' RETURN CASE WHEN amt IS NULL THEN 'Unknown' WHEN amt < 10000 THEN '$0-$10K'
WHEN amt < 50000 THEN '$10K-$50K' WHEN amt < 100000 THEN '$50K-$100K' ELSE '$100K+' END;

CREATE OR REPLACE FUNCTION mask_citizen_id_hash(id STRING) RETURNS STRING
COMMENT 'Deterministic' RETURN CONCAT('CIT_', SUBSTRING(SHA2(id, 256), 1, 12));

SELECT '✅ Government functions created!' AS status;
"""

TAG_DEFINITIONS = [
    ("pii_type_government", "Government PII data types", [
        "ssn", "name", "dob", "address", "phone", "email", 
        "employee_id", "clearance_level"
    ]),
    ("security_classification_government", "Security classification levels", [
        "Top_Secret", "Secret", "Confidential", "Unclassified"
    ]),
    ("clearance_required_government", "Security clearance requirement", [
        "Top_Secret", "Secret", "Confidential", "Public_Trust", "None"
    ]),
    ("data_sensitivity_government", "Data sensitivity levels", [
        "CUI", "FOUO", "Sensitive", "Public"
    ]),
]

ABAC_POLICIES_SQL = """
-- ABAC policies for government to be defined
"""

TEST_TABLES_SQL = """
-- GOVERNMENT DATABASE SCHEMA
CREATE SCHEMA IF NOT EXISTS government; DROP TABLE IF EXISTS citizens;
CREATE TABLE citizens (citizen_id STRING, first_name STRING, last_name STRING, ssn STRING,
address STRING, city STRING, state STRING, zip STRING, PRIMARY KEY (citizen_id)) USING DELTA;
INSERT INTO citizens VALUES
('CZ-1001', 'John', 'Smith', '123-45-6789', '123 Main St', 'Springfield', 'IL', '62701'),
('CZ-1002', 'Sarah', 'Johnson', '234-56-7890', '456 Oak Ave', 'Madison', 'WI', '53703'),
('CZ-1003', 'Mike', 'Williams', '345-67-8901', '789 Pine Rd', 'Columbus', 'OH', '43201');

DROP TABLE IF EXISTS licenses;
CREATE TABLE licenses (license_id STRING, citizen_id STRING, license_type STRING, license_number STRING,
issue_date DATE, expiry_date DATE, PRIMARY KEY (license_id)) USING DELTA;
INSERT INTO licenses VALUES
('L-2001', 'CZ-1001', 'Drivers', 'DL-123456', '2020-01-15', '2025-01-15'),
('L-2002', 'CZ-1002', 'Drivers', 'DL-234567', '2019-05-20', '2024-05-20'),
('L-2003', 'CZ-1003', 'Business', 'BL-345678', '2021-03-10', '2026-03-10');

DROP TABLE IF EXISTS tax_records;
CREATE TABLE tax_records (record_id STRING, citizen_id STRING, tax_year INT, income DECIMAL(12,2),
tax_owed DECIMAL(12,2), PRIMARY KEY (record_id)) USING DELTA;
INSERT INTO tax_records VALUES
('T-3001', 'CZ-1001', 2023, 75000.00, 12500.00),
('T-3002', 'CZ-1002', 2023, 95000.00, 18000.00),
('T-3003', 'CZ-1003', 2023, 62000.00, 9800.00);

SELECT 'citizens' AS tbl, COUNT(*) AS cnt FROM citizens
UNION ALL SELECT 'licenses', COUNT(*) FROM licenses
UNION ALL SELECT 'tax_records', COUNT(*) FROM tax_records;

-- GOVERNMENT EXTENDED
DROP TABLE IF EXISTS violations;
CREATE TABLE violations (violation_id STRING, citizen_id STRING, violation_type STRING, fine DECIMAL(8,2),
violation_date DATE, PRIMARY KEY (violation_id)) USING DELTA;
INSERT INTO violations VALUES ('V-1', 'CZ-1001', 'Speeding', 150.00, '2024-02-10'), ('V-2', 'CZ-1002', 'Parking', 50.00, '2024-03-05');
SELECT 'violations' AS tbl, COUNT(*) AS cnt FROM violations;
"""

TAG_APPLICATIONS_SQL = """
-- Tag applications for government to be defined
"""

TEST_TABLES = ["citizens_test", "employees_test", "security_clearances_test", 
               "classified_documents_test", "access_logs_test", "facilities_test"]
