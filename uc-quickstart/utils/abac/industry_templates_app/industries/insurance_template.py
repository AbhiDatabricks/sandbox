"""
Insurance Industry ABAC Template
All SQL definitions for insurance industry
"""
# Industry metadata
INDUSTRY_NAME = "Insurance"
INDUSTRY_DESCRIPTION = "Insurance policies, policy holders, premiums, and claims"

# Step 1: Function Definitions
FUNCTIONS_SQL = """
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Mask SSN showing last 4 digits (XXX-XX-1234)'
RETURN CASE 
  WHEN ssn IS NULL THEN ssn 
  ELSE CONCAT('XXX-XX-', RIGHT(REPLACE(ssn, '-', ''), 4)) 
END;

CREATE OR REPLACE FUNCTION mask_policy_number_last4(policy STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Mask policy number showing last 4 digits'
RETURN CASE 
  WHEN policy IS NULL THEN policy 
  ELSE CONCAT('****', RIGHT(policy, 4)) 
END;

CREATE OR REPLACE FUNCTION mask_claim_amount_bucket(amt DECIMAL(12,2))
RETURNS STRING
COMMENT 'ABAC utility: Bucket claim amounts into ranges' 
RETURN CASE 
  WHEN amt IS NULL THEN 'Unknown' 
  WHEN amt < 1000 THEN '\$0-\$1K'
  WHEN amt < 5000 THEN '\$1K-\$5K' 
  WHEN amt < 10000 THEN '\$5K-\$10K' 
  ELSE '\$10K+' 
END;

CREATE OR REPLACE FUNCTION mask_policyholder_id_hash(id STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Deterministic policy holder ID masking for joins'
RETURN CONCAT('PH_', SUBSTRING(SHA2(id, 256), 1, 12));

CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask email local part'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN email NOT LIKE '%@%' THEN '****'
  ELSE CONCAT('****@', SPLIT(email, '@')[1])
END;

CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask phone number showing last 4 digits'
RETURN CASE 
  WHEN phone IS NULL OR phone = '' THEN phone
  WHEN LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '')) < 4 THEN 'XXXX'
  ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4))
END;

CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 14 AND 22; -- adjusted for UTC

CREATE OR REPLACE FUNCTION filter_high_value_claims(amount DECIMAL(12,2))
RETURNS BOOLEAN
COMMENT 'ABAC utility: Filter out high-value claims'
RETURN amount > 5000; 

"""

# Step 2: Tag Policy Definitions (tag_key, description, allowed_values)
TAG_DEFINITIONS = [
    ("pii_type_insurance", "PII field types for insurance industry", 
     ["ssn", "email", "phone", "policy_number", "amount", "id"]),
    
    ("data_classification_insurance", "Data classification level for insurance industry",
     ["Confidential", "Internal", "Public"])
]

# Step 3: ABAC Policy Definitions
# Syntax per https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/policies
ABAC_POLICIES_SQL = """
-- SSN Column Mask Policy
CREATE OR REPLACE POLICY ssn_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','ssn') AS ssn
ON COLUMN ssn;

-- Policy Number Mask Policy
CREATE OR REPLACE POLICY policy_no_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_policy_number_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','policy_number') AS policy
ON COLUMN policy;

-- Email Column Mask Policy
CREATE OR REPLACE POLICY email_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','email') AS email
ON COLUMN email;

-- Phone Column Mask Policy
CREATE OR REPLACE POLICY phone_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','phone') AS phone
ON COLUMN phone;

-- Policy Holder ID Column Mask Policy
CREATE OR REPLACE POLICY policyholder_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_policyholder_id_hash 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','id') AS policyholder_id
ON COLUMN policyholder_id;

-- High Value Claims Row Filter Policy
CREATE OR REPLACE POLICY claims_filter ON SCHEMA {CATALOG}.{SCHEMA}
ROW FILTER {CATALOG}.{SCHEMA}.filter_high_value_claims 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','amount') AS amount
USING COLUMNS (amount);
"""

# Step 4: Test Table Creation (Optional - with _test suffix)
TEST_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS policyholders_test (
  policyholder_id STRING, 
  first_name STRING, 
  last_name STRING, 
  ssn STRING,
  email STRING, 
  phone STRING, 
  CONSTRAINT pk_policyholders PRIMARY KEY (policyholder_id)
) USING DELTA;

INSERT INTO policyholders_test VALUES
('PH-1001', 'John', 'Smith', '123-45-6789', 'john@email.com', '246-555-0101'),
('PH-1002', 'Sarah', 'Johnson', '234-56-7890', 'sarah@email.com', '135-555-0102'),
('PH-1003', 'Mike', 'Williams', '345-67-8901', 'mike@email.com', '357-555-0103'),
('PH-1004', 'Emily', 'Brown', '456-78-9012', 'ebrown@email.com', '344-555-0104'),
('PH-1005', 'David', 'Jones', '567-89-0123', 'djones@email.com', '124-555-0105'),
('PH-1006', 'Jennifer', 'Garcia', '678-90-1234', 'jgarcia@email.com', '756-555-0106'),
('PH-1007', 'Robert', 'Martinez', '789-01-2345', 'rmartinez@email.com', '874-555-0107'),
('PH-1008', 'Lisa', 'Rodriguez', '890-12-3456', 'lrodriguez@email.com', '583-555-0108'),
('PH-1009', 'James', 'Wilson', '901-23-4567', 'jwilson@email.com', '869-555-0109'),
('PH-1010', 'Maria', 'Anderson', '012-34-5678', 'manderson@email.com', '284-555-0110'),
('PH-1011', 'William', 'Thomas', '111-22-3333', 'wthomas@email.com', '663-555-0111'),
('PH-1012', 'Jessica', 'Taylor', '222-33-4444', 'jtaylor@email.com', '653555-0112'),
('PH-1013', 'Christopher', 'Moore', '333-44-5555', 'cmoore@email.com', '229-555-0113'),
('PH-1014', 'Amanda', 'Jackson', '444-55-6666', 'ajackson@email.com', '694-555-0114'),
('PH-1015', 'Daniel', 'Martin', '555-66-7777', 'dmartin@email.com', '611-555-0115'),
('PH-1016', 'Ashley', 'Lee', '666-77-8888', 'alee@email.com', '927-555-0116'),
('PH-1017', 'Matthew', 'Perez', '777-88-9999', 'mperez@email.com', '218-555-0117'),
('PH-1018', 'Michelle', 'Thompson', '888-99-0000', 'mthompson@email.com', '627-555-0118'),
('PH-1019', 'Joshua', 'White', '999-00-1111', 'jwhite@email.com', '722-555-0119'),
('PH-1020', 'Stephanie', 'Harris', '000-11-2222', 'sharris@email.com', '828-555-0120');

CREATE TABLE IF NOT EXISTS policies_test (
  policy_id STRING, 
  policyholder_id STRING, 
  policy_number STRING, 
  policy_type STRING,
  premium DECIMAL(10,2), 
  coverage_amount STRING, 
  CONSTRAINT pk_policies PRIMARY KEY (policy_id)
) USING DELTA;

INSERT INTO policies_test VALUES
('P-5001', 'PH-1001', '172123456', 'Auto', 1200.00, '50000.00'),
('P-5002', 'PH-1002', '434234567', 'Home', 1800.00, '300000.00'),
('P-5003', 'PH-1003', '555345678', 'Life', 600.00, '500000.00'),
('P-5004', 'PH-1004', '432456789', 'Auto', 1900.00, '100000.00'),
('P-5005', 'PH-1005', '667567890', 'Home', 1800.00, '200000.00'),
('P-5006', 'PH-1006', '947678901', 'Life', 1700.00, '300000.00'),
('P-5007', 'PH-1007', '823789012', 'Auto', 1600.00, '400000.00'),
('P-5008', 'PH-1008', '474890123', 'Home', 1500.00, '500000.00'),
('P-5009', 'PH-1009', '884901234', 'Life', 1400.00, '600000.00'),
('P-5010', 'PH-1010', '927012345', 'Auto', 1300.00, '700000.00'),
('P-5011', 'PH-1011', '038135799', 'Home', 1200.00, '800000.00'),
('P-5012', 'PH-1012', '302246800', 'Life', 1100.00, '900000.00'),
('P-5013', 'PH-1013', '119975311', 'Auto', 1000.00, '1000000.00'),
('P-5014', 'PH-1014', '947864200', 'Home', 900.00, '90000.00'),
('P-5015', 'PH-1015', '324642088', 'Life', 800.00, '80000.00'),
('P-5016', 'PH-1016', '927753199', 'Auto', 700.00, '70000.00'),
('P-5017', 'PH-1017', '038357911', 'Home', 600.00, '60000.00'),
('P-5018', 'PH-1018', '482024688', 'Life', 500.00, '50000.00'),
('P-5019', 'PH-1019', '482011235', 'Auto', 1850.00, '350000.00'),
('P-5020', 'PH-1020', '823124816', 'Home', 1220.00, '450000.00');

CREATE TABLE IF NOT EXISTS claims_test (
  claim_id STRING, 
  policy_id STRING, 
  claim_amount STRING, 
  claim_date DATE,
  status STRING, 
  CONSTRAINT pk_claims PRIMARY KEY (claim_id)
) USING DELTA;

INSERT INTO claims_test VALUES
('C-1001', 'P-5001', '8500.00', '2024-02-15', 'Approved'),
('C-1002', 'P-5002', '15000.00', '2024-03-01', 'Pending'),
('C-1003', 'P-5003', '0.00', '2024-03-10', 'Denied'),
('C-1004', 'P-5004', '30000.00', '2024-02-15', 'Approved'),
('C-1005', 'P-5005', '9000.00', '2024-03-01', 'Pending'),
('C-1006', 'P-5006', '700.00', '2024-03-10', 'Denied'),
('C-1007', 'P-5007', '2500.00', '2024-02-15', 'Approved'),
('C-1008', 'P-5008', '15000.00', '2024-03-01', 'Pending'),
('C-1009', 'P-5009', '50000.00', '2024-03-10', 'Denied');

CREATE TABLE IF NOT EXISTS premiums_test (
  payment_id STRING, 
  policy_id STRING, 
  amount STRING, 
  payment_date DATE,
  CONSTRAINT pk_premiums PRIMARY KEY (payment_id)
) USING DELTA;

INSERT INTO premiums_test VALUES 
('PM-1', 'P-5001', '10000.00', '2024-01-01'), 
('PM-2', 'P-5002', '15000.00', '2024-01-01'),
('PM-3', 'P-5003', '1000.00', '2024-11-01'), 
('PM-4', 'P-5004', '50.00', '2024-03-01'),
('PM-5', 'P-5005', '600.00', '2024-04-01'), 
('PM-6', 'P-5006', '75000.00', '2024-05-01'),
('PM-7', 'P-5007', '80.00', '2024-08-01'), 
('PM-8', 'P-5008', '75.00', '2024-07-01'),
('PM-9', 'P-5009', '10.00', '2024-06-01'), 
('PM-10', 'P-5010', '1500.00', '2024-10-01'),
('PM-11', 'P-5011', '95000.00', '2024-09-01'), 
('PM-12', 'P-5012', '50.00', '2024-02-01'),
('PM-13', 'P-5013', '400.00', '2024-11-01');
"""

# Step 5: Tag Applications (Optional - for test tables only)
# Uses {CATALOG}.{SCHEMA} placeholders for fully qualified names
TAG_APPLICATIONS_SQL = """
ALTER TABLE {CATALOG}.{SCHEMA}.policyholders_test ALTER COLUMN ssn SET TAGS ('pii_type_insurance' = 'ssn', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.policyholders_test ALTER COLUMN email SET TAGS ('pii_type_insurance' = 'email');
ALTER TABLE {CATALOG}.{SCHEMA}.policyholders_test ALTER COLUMN phone SET TAGS ('pii_type_insurance' = 'phone');
ALTER TABLE {CATALOG}.{SCHEMA}.policyholders_test ALTER COLUMN policyholder_id SET TAGS ('pii_type_insurance' = 'id');

ALTER TABLE {CATALOG}.{SCHEMA}.policies_test ALTER COLUMN policyholder_id SET TAGS ('pii_type_insurance' = 'id');
ALTER TABLE {CATALOG}.{SCHEMA}.policies_test ALTER COLUMN policy_number SET TAGS ('pii_type_insurance' = 'policy_number', 'data_classification_insurance' = 'Confidential');

ALTER TABLE {CATALOG}.{SCHEMA}.claims_test ALTER COLUMN claim_amount SET TAGS ('pii_type_insurance' = 'amount');

ALTER TABLE {CATALOG}.{SCHEMA}.premiums_test ALTER COLUMN amount SET TAGS ('pii_type_insurance' = 'amount');
"""

# List of test tables created
TEST_TABLES = ["policyholders_test", "policies_test", "claims_test", "premiums_test"]
