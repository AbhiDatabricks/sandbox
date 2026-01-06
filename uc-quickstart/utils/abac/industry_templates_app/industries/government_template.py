"""
Government Industry ABAC Template
"""

INDUSTRY_NAME = "Government"
INDUSTRY_DESCRIPTION = "Government data protection with security clearances and classifications"

FUNCTIONS_SQL = """
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING) 
RETURNS STRING
COMMENT 'SSN masking' 
RETURN CASE 
    WHEN ssn IS NULL THEN ssn 
    ELSE CONCAT('XXX-XX-', RIGHT(REPLACE(ssn, '-', ''), 4)) 
END;

CREATE OR REPLACE FUNCTION mask_license_partial(license STRING) 
RETURNS STRING
RETURN CASE 
  WHEN license IS NULL THEN license 
  ELSE CONCAT('****-', RIGHT(license, 2)) 
END;

CREATE OR REPLACE FUNCTION mask_address(address STRING) 
RETURNS STRING
RETURN '***';

CREATE OR REPLACE FUNCTION mask_tax_amount_bucket(amt DECIMAL(12,2)) 
RETURNS STRING
COMMENT 'Tax ranges' 
RETURN CASE 
  WHEN amt IS NULL THEN 'Unknown' 
  WHEN amt < 10000 THEN '\$0-\$10K'
  WHEN amt < 50000 THEN '\$10K-\$50K' 
  WHEN amt < 100000 THEN '\$50K-\$100K' 
  ELSE '\$100K+' 
END;

CREATE OR REPLACE FUNCTION mask_citizen_id_hash(id STRING) 
RETURNS STRING
COMMENT 'Deterministic' 
RETURN CONCAT('CIT_', SUBSTRING(SHA2(id, 256), 1, 12));

CREATE OR REPLACE FUNCTION business_hours_filter()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours (8AM-6PM America/Chicago)'
RETURN hour(from_utc_timestamp(current_timestamp(), 'America/Chicago')) BETWEEN 8 AND 18;

"""

TAG_DEFINITIONS = [
    ("pii_type_government", "Government PII data types", [
        "ssn", "name", "dob", "address", "phone", "email",
        "id", "amount", "license"
    ]),
    ("security_classification_government", "Security classification levels", [
        "Top_Secret", "Secret", "Confidential", "Unclassified"
    ]),
    ("data_sensitivity_government", "Data sensitivity levels", [
        "CUI", "FOUO", "Sensitive", "Public"
    ])
]

ABAC_POLICIES_SQL = """
-- ABAC policies for government to be defined

-- POLICY 1: SSN Masking
CREATE OR REPLACE POLICY ssn_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
hasTagValue('pii_type_government','ssn') AS ssn
ON COLUMN ssn;

-- POLICY 2: License Masking
CREATE OR REPLACE POLICY license_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_license_partial 
TO `account users`
FOR TABLES
MATCH COLUMNS
hasTagValue('pii_type_government','license') AS license
ON COLUMN license;

-- POLICY 3: Address Masking
CREATE OR REPLACE POLICY address_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_address 
TO `account users`
FOR TABLES
MATCH COLUMNS
hasTagValue('pii_type_government','address') AS address
ON COLUMN address;

-- POLICY 4: Amount Bucketing
CREATE OR REPLACE POLICY amount_bucket ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_tax_amount_bucket 
TO `account users`
FOR TABLES
MATCH COLUMNS
hasTagValue('pii_type_government','amount') AS amount
ON COLUMN amount;

-- POLICY 5: Citizen ID Masking
CREATE OR REPLACE POLICY citizen_id_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_citizen_id_hash
TO `account users`
FOR TABLES
MATCH COLUMNS 
hasTagValue('pii_type_government', 'id') AND hasTagValue('security_classification_government', 'Secret') AS citizen_id_cols
ON COLUMN citizen_id_cols;

-- POLICY 6: Business Hours Filter
CREATE OR REPLACE POLICY business_hours_filter
ON SCHEMA {CATALOG}.{SCHEMA}
ROW FILTER {CATALOG}.{SCHEMA}.business_hours_filter
TO `account users`
FOR TABLES;

"""

TEST_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS citizens_test (citizen_id STRING, first_name STRING, last_name STRING, ssn STRING,
address STRING, city STRING, state STRING, zip STRING, PRIMARY KEY (citizen_id)) USING DELTA;
INSERT INTO citizens_test VALUES
('CZ-1001', 'John', 'Smith', '123-45-6789', '123 Main St', 'Springfield', 'IL', '62701'),
('CZ-1002', 'Sarah', 'Johnson', '234-56-7890', '456 Oak Ave', 'Madison', 'WI', '53703'),
('CZ-1003', 'Mike', 'Williams', '345-67-8901', '789 Pine Rd', 'Columbus', 'OH', '43201');

CREATE TABLE IF NOT EXISTS licenses_test (license_id STRING, citizen_id STRING, license_type STRING, license_number STRING,
issue_date DATE, expiry_date DATE, PRIMARY KEY (license_id)) USING DELTA;
INSERT INTO licenses_test VALUES
('L-2001', 'CZ-1001', 'Drivers', 'DL-123456', '2020-01-15', '2025-01-15'),
('L-2002', 'CZ-1002', 'Drivers', 'DL-234567', '2019-05-20', '2024-05-20'),
('L-2003', 'CZ-1003', 'Business', 'BL-345678', '2021-03-10', '2026-03-10');

CREATE TABLE IF NOT EXISTS tax_records_test (record_id STRING, citizen_id STRING, tax_year INT, income DECIMAL(12,2),
tax_owed STRING, PRIMARY KEY (record_id)) USING DELTA;
INSERT INTO tax_records_test VALUES
('T-3001', 'CZ-1001', 2023, 75000.00, 12500.00),
('T-3002', 'CZ-1002', 2023, 95000.00, 18000.00),
('T-3003', 'CZ-1003', 2023, 62000.00, 9800.00);

CREATE TABLE IF NOT EXISTS violations_test (violation_id STRING, citizen_id STRING, violation_type STRING, fine DECIMAL(8,2),
violation_date DATE, PRIMARY KEY (violation_id)) USING DELTA;
INSERT INTO violations_test VALUES ('V-1', 'CZ-1001', 'Speeding', 150.00, '2024-02-10'), ('V-2', 'CZ-1002', 'Parking', 50.00, '2024-03-05');
"""

TAG_APPLICATIONS_SQL = """
ALTER TABLE {CATALOG}.{SCHEMA}.citizens_test ALTER COLUMN citizen_id SET TAGS ('pii_type_government' = 'id', 'security_classification_government' = 'Secret');
ALTER TABLE {CATALOG}.{SCHEMA}.citizens_test ALTER COLUMN first_name SET TAGS ('pii_type_government' = 'name');
ALTER TABLE {CATALOG}.{SCHEMA}.citizens_test ALTER COLUMN last_name SET TAGS ('pii_type_government' = 'name');
ALTER TABLE {CATALOG}.{SCHEMA}.citizens_test ALTER COLUMN ssn SET TAGS ('pii_type_government' = 'ssn', 'data_sensitivity_government' = 'Sensitive');
ALTER TABLE {CATALOG}.{SCHEMA}.citizens_test ALTER COLUMN address SET TAGS ('pii_type_government' = 'address');

ALTER TABLE {CATALOG}.{SCHEMA}.licenses_test ALTER COLUMN citizen_id SET TAGS ('pii_type_government' = 'id', 'security_classification_government' = 'Secret');
ALTER TABLE {CATALOG}.{SCHEMA}.licenses_test ALTER COLUMN license_number SET TAGS ('pii_type_government' = 'license', 'data_sensitivity_government' = 'Sensitive');

ALTER TABLE {CATALOG}.{SCHEMA}.tax_records_test ALTER COLUMN tax_owed SET TAGS ('pii_type_government' = 'amount');
ALTER TABLE {CATALOG}.{SCHEMA}.tax_records_test ALTER COLUMN citizen_id SET TAGS ('pii_type_government' = 'id', 'security_classification_government' = 'Secret');

ALTER TABLE {CATALOG}.{SCHEMA}.violations_test ALTER COLUMN fine SET TAGS ('data_sensitivity_government' = 'Sensitive');
"""

TEST_TABLES = ["licenses_test", "citizens_test", "tax_records_test", "violations_test"]
