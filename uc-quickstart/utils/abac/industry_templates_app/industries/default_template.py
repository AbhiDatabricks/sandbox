"""
Default Industry ABAC Template
Comprehensive, generic ABAC template with maximum coverage across all use cases.
This is the SUPER-SET template - all other industries are subsets of this.

Includes:
- 20 Column Masking Functions (covering all PII types)
- 8 Row Filter Functions (time, region, value, flag-based access)
- 8 Tag Policies (generic functional names, no industry suffix)
- 15 ABAC Policies (catalog-level, comprehensive coverage)
- 5 Test Tables (users, transactions, employees, assets, audit_log)
"""

# Industry metadata
INDUSTRY_NAME = "Default"
INDUSTRY_DESCRIPTION = "Comprehensive generic ABAC template - super-set of all industries with maximum coverage"

# =============================================================================
# STEP 1: MASKING AND FILTER FUNCTIONS (28 total: 20 masks + 8 filters)
# =============================================================================
FUNCTIONS_SQL = """
-- =============================================================================
-- COLUMN MASKING FUNCTIONS (20)
-- =============================================================================

-- 1. SSN Masking - Show last 4 digits
CREATE OR REPLACE FUNCTION mask_ssn(ssn STRING)
RETURNS STRING
COMMENT 'Mask SSN showing last 4 digits (XXX-XX-1234)'
RETURN CASE 
  WHEN ssn IS NULL OR ssn = '' THEN ssn 
  ELSE CONCAT('XXX-XX-', RIGHT(REGEXP_REPLACE(ssn, '[^0-9]', ''), 4)) 
END;

-- 2. Email Masking - Hide local part, show domain
CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'Mask email local part, preserve domain'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN LOCATE('@', email) = 0 THEN '****'
  ELSE CONCAT('****@', SUBSTRING(email, LOCATE('@', email) + 1))
END;

-- 3. Phone Masking - Show last 4 digits
CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'Mask phone number showing last 4 digits'
RETURN CASE 
  WHEN phone IS NULL OR phone = '' THEN phone
  WHEN LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '')) < 4 THEN 'XXXX'
  ELSE CONCAT('XXX-XXX-', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4))
END;

-- 4. Credit Card Masking - PCI-DSS compliant (last 4 only)
CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'PCI-DSS compliant credit card masking (last 4 only)'
RETURN CASE
  WHEN card_number IS NULL OR card_number = '' THEN card_number
  ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card_number, '[^0-9]', ''), 4))
END;

-- 5. Account Number Masking - Last 4 digits
CREATE OR REPLACE FUNCTION mask_account_number(account_number STRING)
RETURNS STRING
COMMENT 'Mask account number showing last 4 digits'
RETURN CASE
  WHEN account_number IS NULL OR account_number = '' THEN account_number
  WHEN LENGTH(account_number) <= 4 THEN REPEAT('*', LENGTH(account_number))
  ELSE CONCAT(REPEAT('*', LENGTH(account_number) - 4), RIGHT(account_number, 4))
END;

-- 6. Routing Number Masking - Last 2 digits
CREATE OR REPLACE FUNCTION mask_routing_number(routing_number STRING)
RETURNS STRING
COMMENT 'Mask routing number showing last 2 digits'
RETURN CASE
  WHEN routing_number IS NULL OR routing_number = '' THEN routing_number
  ELSE CONCAT('*******', RIGHT(routing_number, 2))
END;

-- 7. Name Partial Masking - First initial + asterisks
CREATE OR REPLACE FUNCTION mask_name(name STRING)
RETURNS STRING
COMMENT 'Partial name masking (J*** for John)'
RETURN CASE 
  WHEN name IS NULL OR name = '' THEN name
  WHEN LENGTH(name) = 1 THEN '*'
  ELSE CONCAT(LEFT(name, 1), REPEAT('*', LENGTH(name) - 1))
END;

-- 8. Full Name Masking - Hash for privacy
CREATE OR REPLACE FUNCTION mask_name_hash(name STRING)
RETURNS STRING
COMMENT 'Hash name for complete anonymization'
RETURN CASE 
  WHEN name IS NULL THEN NULL
  ELSE CONCAT('NAME_', SUBSTRING(SHA2(name, 256), 1, 8))
END;

-- 9. Address Masking - Show city/state only
CREATE OR REPLACE FUNCTION mask_address(address STRING, city STRING, state STRING)
RETURNS STRING
COMMENT 'Mask street address, show city/state'
RETURN CASE
  WHEN city IS NULL AND state IS NULL THEN '*****, ***'
  WHEN state IS NULL THEN CONCAT('*****, ', city)
  WHEN city IS NULL THEN CONCAT('*****, ', state)
  ELSE CONCAT('*****, ', city, ', ', state)
END;

-- 10. DOB Masking - Show year only
CREATE OR REPLACE FUNCTION mask_dob(dob DATE)
RETURNS STRING
COMMENT 'Mask date of birth showing year only'
RETURN CASE
  WHEN dob IS NULL THEN NULL
  ELSE CONCAT('****-**-** (', YEAR(dob), ')')
END;

-- 11. Age Range - Convert DOB to age bucket
CREATE OR REPLACE FUNCTION mask_dob_age_range(dob DATE)
RETURNS STRING
COMMENT 'Convert DOB to age range bucket'
RETURN CASE
  WHEN dob IS NULL THEN 'Unknown'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 18 THEN 'Under 18'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 25 THEN '18-24'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 35 THEN '25-34'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 45 THEN '35-44'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 55 THEN '45-54'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 65 THEN '55-64'
  ELSE '65+'
END;

-- 12. IP Address Masking - Subnet only
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'Mask IP address to subnet level'
RETURN CASE
  WHEN ip IS NULL OR ip = '' THEN ip
  WHEN LOCATE('.', ip) = 0 THEN '***'
  ELSE CONCAT(SPLIT(ip, '\\\\.')[0], '.', SPLIT(ip, '\\\\.')[1], '.*.*')
END;

-- 13. Amount Bucketing - Financial amounts to ranges
CREATE OR REPLACE FUNCTION mask_amount_bucket(amount DECIMAL(18,2))
RETURNS STRING
COMMENT 'Bucket financial amounts into ranges'
RETURN CASE 
  WHEN amount IS NULL THEN 'Unknown' 
  WHEN amount < 0 THEN 'Negative'
  WHEN amount < 100 THEN '$0-$100'
  WHEN amount < 1000 THEN '$100-$1K'
  WHEN amount < 10000 THEN '$1K-$10K' 
  WHEN amount < 100000 THEN '$10K-$100K' 
  WHEN amount < 1000000 THEN '$100K-$1M'
  ELSE '$1M+'
END;

-- 14. Salary Bucketing - Annual salary ranges
CREATE OR REPLACE FUNCTION mask_salary_bucket(salary DECIMAL(18,2))
RETURNS STRING
COMMENT 'Bucket salary into compensation ranges'
RETURN CASE 
  WHEN salary IS NULL THEN 'Not Disclosed' 
  WHEN salary < 30000 THEN 'Entry (<$30K)'
  WHEN salary < 50000 THEN 'Junior ($30K-$50K)'
  WHEN salary < 75000 THEN 'Mid ($50K-$75K)'
  WHEN salary < 100000 THEN 'Senior ($75K-$100K)'
  WHEN salary < 150000 THEN 'Lead ($100K-$150K)'
  WHEN salary < 250000 THEN 'Principal ($150K-$250K)'
  ELSE 'Executive ($250K+)'
END;

-- 15. String Hash - One-way SHA-256 anonymization
CREATE OR REPLACE FUNCTION mask_string_hash(input STRING)
RETURNS STRING
COMMENT 'One-way SHA-256 hash for complete anonymization'
RETURN CASE
  WHEN input IS NULL THEN NULL
  ELSE SHA2(input, 256)
END;

-- 16. String Partial - First and last characters visible
CREATE OR REPLACE FUNCTION mask_string_partial(input STRING)
RETURNS STRING
COMMENT 'Partial masking showing first and last characters'
RETURN CASE 
  WHEN input IS NULL OR input = '' THEN input
  WHEN LENGTH(input) <= 2 THEN REPEAT('*', LENGTH(input))
  WHEN LENGTH(input) = 3 THEN CONCAT(LEFT(input, 1), '*', RIGHT(input, 1))
  ELSE CONCAT(LEFT(input, 1), REPEAT('*', LENGTH(input) - 2), RIGHT(input, 1))
END;

-- 17. ID Deterministic Hash - Consistent masking for joins
CREATE OR REPLACE FUNCTION mask_id_deterministic(id STRING)
RETURNS STRING
COMMENT 'Deterministic ID masking preserving join capability'
RETURN CASE
  WHEN id IS NULL THEN NULL
  ELSE CONCAT('ID_', SUBSTRING(SHA2(id, 256), 1, 12))
END;

-- 18. Timestamp Rounding - Round to 15-minute intervals
CREATE OR REPLACE FUNCTION mask_timestamp_round(ts TIMESTAMP)
RETURNS TIMESTAMP
COMMENT 'Round timestamp to 15-minute intervals for privacy'
RETURN TO_TIMESTAMP(UNIX_TIMESTAMP(ts) - (UNIX_TIMESTAMP(ts) % 900));

-- 19. GPS Precision Reduction - Reduce coordinate precision
CREATE OR REPLACE FUNCTION mask_gps_precision(coordinate DOUBLE)
RETURNS DOUBLE
COMMENT 'Reduce GPS precision to 2 decimal places (~1km accuracy)'
RETURN ROUND(coordinate, 2);

-- 20. Serial Number Masking - Last 4 characters
CREATE OR REPLACE FUNCTION mask_serial_last4(serial STRING)
RETURNS STRING
COMMENT 'Mask serial number showing last 4 characters'
RETURN CASE 
  WHEN serial IS NULL OR serial = '' THEN serial
  WHEN LENGTH(serial) <= 4 THEN REPEAT('X', LENGTH(serial))
  ELSE CONCAT(REPEAT('X', LENGTH(serial) - 4), RIGHT(serial, 4))
END;

-- =============================================================================
-- ROW FILTER FUNCTIONS (8)
-- =============================================================================

-- 1. Business Hours Filter - 9AM to 5PM
CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'Allow access only during business hours (9 AM - 5 PM UTC)'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

-- 2. Extended Hours Filter - 7AM to 9PM
CREATE OR REPLACE FUNCTION filter_extended_hours()
RETURNS BOOLEAN
COMMENT 'Allow access during extended hours (7 AM - 9 PM UTC)'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 7 AND 21;

-- 3. Maintenance Window Filter - 10PM to 6AM
CREATE OR REPLACE FUNCTION filter_maintenance_window()
RETURNS BOOLEAN
COMMENT 'Allow access during maintenance window (10 PM - 6 AM UTC)'
RETURN HOUR(CURRENT_TIMESTAMP()) >= 22 OR HOUR(CURRENT_TIMESTAMP()) < 6;

-- 4. High Value Filter - Amount exceeds threshold
CREATE OR REPLACE FUNCTION filter_high_value(amount DECIMAL(18,2))
RETURNS BOOLEAN
COMMENT 'Filter for high-value records exceeding $10,000'
RETURN amount > 10000;

-- 5. Flagged Records Filter - Show only flagged items
CREATE OR REPLACE FUNCTION filter_flagged_only(flag BOOLEAN)
RETURNS BOOLEAN
COMMENT 'Show only flagged/marked records'
RETURN flag = TRUE;

-- 6. Active Records Filter - Show only active items
CREATE OR REPLACE FUNCTION filter_active_only(status STRING)
RETURNS BOOLEAN
COMMENT 'Show only active records'
RETURN UPPER(status) = 'ACTIVE';

-- 7. Deny All Filter - Block all access
CREATE OR REPLACE FUNCTION filter_deny_all()
RETURNS BOOLEAN
COMMENT 'Deny all row access (returns FALSE)'
RETURN FALSE;

-- 8. Allow All Filter - Allow all access
CREATE OR REPLACE FUNCTION filter_allow_all()
RETURNS BOOLEAN
COMMENT 'Allow all row access (returns TRUE)'
RETURN TRUE;
"""

# =============================================================================
# STEP 2: TAG POLICY DEFINITIONS (8 generic policies, no industry suffix)
# =============================================================================
TAG_DEFINITIONS = [
    # PII Type - What kind of sensitive data
    ("pii_type", "Type of personally identifiable information", [
        "ssn", "email", "phone", "name", "address", "dob", "age",
        "credit_card", "account_number", "routing_number", 
        "ip_address", "device_id", "biometric",
        "license_number", "passport", "national_id",
        "medical_record", "genetic_data", "financial_record"
    ]),
    
    # Data Classification - Security level
    ("data_classification", "Data security classification level", [
        "Public", "Internal", "Confidential", "Restricted", "Top_Secret"
    ]),
    
    # Compliance Requirement - Regulatory framework
    ("compliance_requirement", "Regulatory compliance requirement", [
        "PCI_DSS", "HIPAA", "GDPR", "CCPA", "SOX", "GLBA", "FERPA", "COPPA", "ITAR", "None"
    ]),
    
    # Sensitivity Level - Business sensitivity
    ("sensitivity_level", "Business sensitivity level", [
        "Low", "Medium", "High", "Critical"
    ]),
    
    # Data Purpose - Intended use
    ("data_purpose", "Intended purpose for data access", [
        "Operations", "Analytics", "Reporting", "Audit", "Marketing", 
        "Research", "Support", "Compliance", "Legal", "HR"
    ]),
    
    # Access Restriction - Time/condition-based access
    ("access_restriction", "Access restriction type", [
        "Business_Hours", "Extended_Hours", "Maintenance_Window",
        "Region_Locked", "Flagged_Only", "Active_Only", "None"
    ]),
    
    # Retention Policy - Data retention period
    ("retention_policy", "Data retention period", [
        "30_Days", "90_Days", "1_Year", "3_Years", "7_Years", "Indefinite", "Delete_Immediately"
    ]),
    
    # Geographic Scope - Data residency
    ("geographic_scope", "Geographic scope for data access", [
        "Country_Only", "Region_Only", "Cross_Border_Approved", "Global"
    ])
]

# =============================================================================
# STEP 3: ABAC POLICY DEFINITIONS (15 policies at Catalog level)
# =============================================================================
ABAC_POLICIES_SQL = """
-- =============================================================================
-- COLUMN MASK POLICIES (12) - Based on pii_type tag
-- =============================================================================

-- Policy 1: SSN Masking
CREATE OR REPLACE POLICY mask_ssn_policy ON CATALOG {CATALOG}
COMMENT 'Mask SSN columns tagged with pii_type=ssn'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'ssn') AS ssn_col
ON COLUMN ssn_col;

-- Policy 2: Email Masking
CREATE OR REPLACE POLICY mask_email_policy ON CATALOG {CATALOG}
COMMENT 'Mask email columns tagged with pii_type=email'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'email') AS email_col
ON COLUMN email_col;

-- Policy 3: Phone Masking
CREATE OR REPLACE POLICY mask_phone_policy ON CATALOG {CATALOG}
COMMENT 'Mask phone columns tagged with pii_type=phone'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'phone') AS phone_col
ON COLUMN phone_col;

-- Policy 4: Name Masking
CREATE OR REPLACE POLICY mask_name_policy ON CATALOG {CATALOG}
COMMENT 'Mask name columns tagged with pii_type=name'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_name
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'name') AS name_col
ON COLUMN name_col;

-- Policy 5: Credit Card Masking (PCI-DSS)
CREATE OR REPLACE POLICY mask_credit_card_policy ON CATALOG {CATALOG}
COMMENT 'PCI-DSS compliant credit card masking for pii_type=credit_card'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_credit_card
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'credit_card') AS card_col
ON COLUMN card_col;

-- Policy 6: Account Number Masking
CREATE OR REPLACE POLICY mask_account_policy ON CATALOG {CATALOG}
COMMENT 'Mask account numbers tagged with pii_type=account_number'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_account_number
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'account_number') AS account_col
ON COLUMN account_col;

-- Policy 7: IP Address Masking
CREATE OR REPLACE POLICY mask_ip_policy ON CATALOG {CATALOG}
COMMENT 'Mask IP addresses tagged with pii_type=ip_address'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ip_address
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'ip_address') AS ip_col
ON COLUMN ip_col;

-- Policy 8: DOB Masking (HIPAA/Privacy)
CREATE OR REPLACE POLICY mask_dob_policy ON CATALOG {CATALOG}
COMMENT 'Mask DOB columns tagged with pii_type=dob'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_dob
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'dob') AS dob_col
ON COLUMN dob_col;

-- Policy 9: Financial Amount Bucketing
CREATE OR REPLACE POLICY mask_amount_policy ON CATALOG {CATALOG}
COMMENT 'Bucket financial amounts tagged with pii_type=financial_record'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_amount_bucket
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'financial_record') AS amount_col
ON COLUMN amount_col;

-- Policy 10: Salary Bucketing (HR)
CREATE OR REPLACE POLICY mask_salary_policy ON CATALOG {CATALOG}
COMMENT 'Bucket salary data for HR privacy'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_salary_bucket
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose', 'HR') AND hasTagValue('sensitivity_level', 'High') AS salary_col
ON COLUMN salary_col;

-- Policy 11: Serial/Device ID Masking
CREATE OR REPLACE POLICY mask_device_id_policy ON CATALOG {CATALOG}
COMMENT 'Mask device IDs and serial numbers'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_serial_last4
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'device_id') AS device_col
ON COLUMN device_col;

-- Policy 12: Timestamp Rounding (Privacy)
CREATE OR REPLACE POLICY mask_timestamp_policy ON CATALOG {CATALOG}
COMMENT 'Round timestamps for privacy protection'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_timestamp_round
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('sensitivity_level', 'High') AND hasTagValue('data_purpose', 'Audit') AS ts_col
ON COLUMN ts_col;

-- =============================================================================
-- ROW FILTER POLICIES (3) - Based on access_restriction tag
-- =============================================================================

-- Policy 13: Business Hours Access
CREATE OR REPLACE POLICY filter_business_hours_policy ON CATALOG {CATALOG}
COMMENT 'Restrict access to business hours for tagged tables'
ROW FILTER {CATALOG}.{SCHEMA}.filter_business_hours
TO `account users`
FOR TABLES
WHEN hasTagValue('access_restriction', 'Business_Hours');

-- Policy 14: Extended Hours Access
CREATE OR REPLACE POLICY filter_extended_hours_policy ON CATALOG {CATALOG}
COMMENT 'Restrict access to extended hours for tagged tables'
ROW FILTER {CATALOG}.{SCHEMA}.filter_extended_hours
TO `account users`
FOR TABLES
WHEN hasTagValue('access_restriction', 'Extended_Hours');

-- Policy 15: Maintenance Window Access
CREATE OR REPLACE POLICY filter_maintenance_policy ON CATALOG {CATALOG}
COMMENT 'Restrict access to maintenance window for tagged tables'
ROW FILTER {CATALOG}.{SCHEMA}.filter_maintenance_window
TO `account users`
FOR TABLES
WHEN hasTagValue('access_restriction', 'Maintenance_Window');
"""

# =============================================================================
# STEP 4: TEST TABLE CREATION (5 comprehensive tables)
# =============================================================================
TEST_TABLES_SQL = """
-- =============================================================================
-- TABLE 1: USERS - Customer/User PII data
-- =============================================================================
CREATE TABLE IF NOT EXISTS users_test (
  user_id STRING NOT NULL COMMENT 'Unique user identifier',
  first_name STRING NOT NULL COMMENT 'First name (PII)',
  last_name STRING NOT NULL COMMENT 'Last name (PII)',
  email STRING COMMENT 'Email address (PII)',
  phone STRING COMMENT 'Phone number (PII)',
  ssn STRING COMMENT 'Social Security Number (Sensitive PII)',
  date_of_birth DATE COMMENT 'Date of birth (PII)',
  street_address STRING COMMENT 'Street address (PII)',
  city STRING COMMENT 'City',
  state STRING COMMENT 'State/Province',
  zip_code STRING COMMENT 'Postal code',
  country STRING DEFAULT 'USA' COMMENT 'Country',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Last update timestamp',
  status STRING DEFAULT 'Active' COMMENT 'Account status',
  CONSTRAINT pk_users_test PRIMARY KEY (user_id)
) USING DELTA
COMMENT 'Test table: Customer/User PII data for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO users_test (user_id, first_name, last_name, email, phone, ssn, date_of_birth, street_address, city, state, zip_code) VALUES
('U-1001', 'John', 'Smith', 'john.smith@example.com', '555-123-4567', '123-45-6789', '1985-03-15', '123 Main Street', 'New York', 'NY', '10001'),
('U-1002', 'Sarah', 'Johnson', 'sarah.johnson@example.com', '555-234-5678', '234-56-7890', '1990-07-22', '456 Oak Avenue', 'Los Angeles', 'CA', '90001'),
('U-1003', 'Michael', 'Williams', 'mike.williams@example.com', '555-345-6789', '345-67-8901', '1982-11-30', '789 Pine Road', 'Chicago', 'IL', '60601'),
('U-1004', 'Emily', 'Brown', 'emily.brown@example.com', '555-456-7890', '456-78-9012', '1995-05-10', '321 Elm Street', 'Houston', 'TX', '77001'),
('U-1005', 'David', 'Jones', 'david.jones@example.com', '555-567-8901', '567-89-0123', '1978-09-05', '654 Maple Drive', 'Phoenix', 'AZ', '85001'),
('U-1006', 'Lisa', 'Garcia', 'lisa.garcia@example.com', '555-678-9012', '678-90-1234', '1988-12-18', '987 Cedar Lane', 'Philadelphia', 'PA', '19101'),
('U-1007', 'James', 'Miller', 'james.miller@example.com', '555-789-0123', '789-01-2345', '1992-04-25', '147 Birch Court', 'San Antonio', 'TX', '78201'),
('U-1008', 'Jennifer', 'Davis', 'jennifer.davis@example.com', '555-890-1234', '890-12-3456', '1987-08-08', '258 Spruce Way', 'San Diego', 'CA', '92101');

-- =============================================================================
-- TABLE 2: TRANSACTIONS - Financial transaction records
-- =============================================================================
CREATE TABLE IF NOT EXISTS transactions_test (
  transaction_id STRING NOT NULL COMMENT 'Unique transaction ID',
  user_id STRING NOT NULL COMMENT 'Foreign key to users',
  account_number STRING COMMENT 'Account number (PII)',
  card_number STRING COMMENT 'Credit card number (PCI)',
  transaction_type STRING COMMENT 'Type: Purchase, Refund, Transfer, etc.',
  amount DECIMAL(18,2) COMMENT 'Transaction amount',
  currency STRING DEFAULT 'USD' COMMENT 'Currency code',
  merchant_name STRING COMMENT 'Merchant/vendor name',
  merchant_category STRING COMMENT 'Merchant category code',
  ip_address STRING COMMENT 'Client IP address (PII)',
  device_id STRING COMMENT 'Device identifier',
  location_city STRING COMMENT 'Transaction city',
  location_country STRING COMMENT 'Transaction country',
  transaction_timestamp TIMESTAMP COMMENT 'Transaction date/time',
  fraud_flag BOOLEAN DEFAULT FALSE COMMENT 'Fraud indicator',
  status STRING DEFAULT 'Completed' COMMENT 'Transaction status',
  CONSTRAINT pk_transactions_test PRIMARY KEY (transaction_id)
) USING DELTA
COMMENT 'Test table: Financial transactions for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO transactions_test (transaction_id, user_id, account_number, card_number, transaction_type, amount, merchant_name, merchant_category, ip_address, device_id, location_city, location_country, transaction_timestamp, fraud_flag) VALUES
('TXN-10001', 'U-1001', '1234567890', '4532-1234-5678-9010', 'Purchase', 125.50, 'Amazon', 'Online Retail', '192.168.1.100', 'DEV-001-A', 'New York', 'USA', '2024-01-15 10:30:00', FALSE),
('TXN-10002', 'U-1001', '1234567890', '4532-1234-5678-9010', 'Purchase', 85.75, 'Whole Foods', 'Grocery', '192.168.1.101', 'DEV-001-A', 'New York', 'USA', '2024-01-15 14:22:00', FALSE),
('TXN-10003', 'U-1002', '2345678901', '5425-2345-6789-0123', 'Transfer', 5500.00, 'Wire Transfer', 'Banking', '10.0.1.50', 'DEV-002-B', 'Los Angeles', 'USA', '2024-01-16 09:15:00', FALSE),
('TXN-10004', 'U-1003', '3456789012', '3782-3456-7890-1234', 'Purchase', 15250.00, 'Best Buy', 'Electronics', '172.16.0.25', 'DEV-003-C', 'Chicago', 'USA', '2024-01-16 16:45:00', TRUE),
('TXN-10005', 'U-1001', '1234567890', '4532-1234-5678-9010', 'Refund', -250.00, 'Amazon', 'Online Retail', '192.168.1.102', 'DEV-001-A', 'New York', 'USA', '2024-01-17 11:00:00', FALSE),
('TXN-10006', 'U-1004', '4567890123', '4916-4567-8901-2345', 'Purchase', 2340.00, 'Delta Airlines', 'Travel', '192.168.2.50', 'DEV-004-D', 'Houston', 'USA', '2024-01-17 08:30:00', FALSE),
('TXN-10007', 'U-1005', '5678901234', '4024-5678-9012-3456', 'Purchase', 89.99, 'Netflix', 'Entertainment', '10.10.10.10', 'DEV-005-E', 'Phoenix', 'USA', '2024-01-18 19:00:00', FALSE),
('TXN-10008', 'U-1006', '6789012345', '5105-6789-0123-4567', 'Transfer', 25000.00, 'Investment Account', 'Financial', '192.168.3.75', 'DEV-006-F', 'Philadelphia', 'USA', '2024-01-18 10:00:00', FALSE),
('TXN-10009', 'U-1002', '2345678901', '5425-2345-6789-0123', 'Purchase', 450.00, 'Apple Store', 'Electronics', '10.0.1.51', 'DEV-002-B', 'Los Angeles', 'USA', '2024-01-19 13:30:00', FALSE),
('TXN-10010', 'U-1007', '7890123456', '4716-7890-1234-5678', 'Purchase', 67.50, 'Uber Eats', 'Food Delivery', '192.168.4.100', 'DEV-007-G', 'San Antonio', 'USA', '2024-01-19 20:15:00', FALSE);

-- =============================================================================
-- TABLE 3: EMPLOYEES - HR/Employee records
-- =============================================================================
CREATE TABLE IF NOT EXISTS employees_test (
  employee_id STRING NOT NULL COMMENT 'Unique employee ID',
  first_name STRING NOT NULL COMMENT 'First name (PII)',
  last_name STRING NOT NULL COMMENT 'Last name (PII)',
  email STRING COMMENT 'Work email (PII)',
  phone STRING COMMENT 'Phone number (PII)',
  ssn STRING COMMENT 'SSN (Sensitive PII)',
  date_of_birth DATE COMMENT 'DOB (PII)',
  hire_date DATE COMMENT 'Employment start date',
  department STRING COMMENT 'Department name',
  job_title STRING COMMENT 'Job title',
  manager_id STRING COMMENT 'Manager employee ID',
  salary DECIMAL(18,2) COMMENT 'Annual salary (Sensitive)',
  bonus DECIMAL(18,2) COMMENT 'Annual bonus (Sensitive)',
  office_location STRING COMMENT 'Office location',
  access_level STRING COMMENT 'Security clearance level',
  performance_rating STRING COMMENT 'Latest performance rating',
  status STRING DEFAULT 'Active' COMMENT 'Employment status',
  CONSTRAINT pk_employees_test PRIMARY KEY (employee_id)
) USING DELTA
COMMENT 'Test table: Employee/HR records for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO employees_test (employee_id, first_name, last_name, email, phone, ssn, date_of_birth, hire_date, department, job_title, manager_id, salary, bonus, office_location, access_level, performance_rating, status) VALUES
('EMP-001', 'Robert', 'Anderson', 'robert.anderson@company.com', '555-111-2222', '111-22-3333', '1980-06-15', '2015-03-01', 'Engineering', 'Senior Engineer', 'EMP-010', 125000.00, 15000.00, 'New York', 'L3', 'Exceeds', 'Active'),
('EMP-002', 'Maria', 'Martinez', 'maria.martinez@company.com', '555-222-3333', '222-33-4444', '1985-09-20', '2018-07-15', 'Engineering', 'Staff Engineer', 'EMP-001', 145000.00, 20000.00, 'New York', 'L3', 'Exceeds', 'Active'),
('EMP-003', 'William', 'Taylor', 'william.taylor@company.com', '555-333-4444', '333-44-5555', '1990-02-28', '2020-01-10', 'Engineering', 'Engineer', 'EMP-001', 95000.00, 8000.00, 'San Francisco', 'L2', 'Meets', 'Active'),
('EMP-004', 'Patricia', 'Thomas', 'patricia.thomas@company.com', '555-444-5555', '444-55-6666', '1975-11-05', '2010-05-20', 'Finance', 'Finance Director', 'EMP-010', 175000.00, 35000.00, 'Chicago', 'L4', 'Exceeds', 'Active'),
('EMP-005', 'Christopher', 'Jackson', 'chris.jackson@company.com', '555-555-6666', '555-66-7777', '1988-07-12', '2019-09-01', 'Marketing', 'Marketing Manager', 'EMP-010', 110000.00, 12000.00, 'Los Angeles', 'L2', 'Meets', 'Active'),
('EMP-006', 'Jessica', 'White', 'jessica.white@company.com', '555-666-7777', '666-77-8888', '1992-04-30', '2021-02-15', 'HR', 'HR Specialist', 'EMP-008', 75000.00, 5000.00, 'New York', 'L2', 'Meets', 'Active'),
('EMP-007', 'Daniel', 'Harris', 'daniel.harris@company.com', '555-777-8888', '777-88-9999', '1983-12-10', '2016-11-01', 'Legal', 'Legal Counsel', 'EMP-010', 165000.00, 25000.00, 'New York', 'L4', 'Exceeds', 'Active'),
('EMP-008', 'Nancy', 'Clark', 'nancy.clark@company.com', '555-888-9999', '888-99-0000', '1978-08-22', '2012-04-15', 'HR', 'HR Director', 'EMP-010', 155000.00, 22000.00, 'New York', 'L4', 'Exceeds', 'Active'),
('EMP-009', 'Matthew', 'Lewis', 'matthew.lewis@company.com', '555-999-0000', '999-00-1111', '1995-01-18', '2022-06-01', 'Engineering', 'Junior Engineer', 'EMP-003', 72000.00, 4000.00, 'San Francisco', 'L1', 'Meets', 'Active'),
('EMP-010', 'Elizabeth', 'Robinson', 'elizabeth.robinson@company.com', '555-000-1111', '000-11-2222', '1970-03-25', '2008-01-15', 'Executive', 'VP Operations', NULL, 250000.00, 75000.00, 'New York', 'L5', 'Exceeds', 'Active');

-- =============================================================================
-- TABLE 4: ASSETS - Inventory/Equipment tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS assets_test (
  asset_id STRING NOT NULL COMMENT 'Unique asset ID',
  asset_name STRING NOT NULL COMMENT 'Asset name/description',
  asset_type STRING COMMENT 'Type: Hardware, Software, Vehicle, etc.',
  serial_number STRING COMMENT 'Serial number (Sensitive)',
  manufacturer STRING COMMENT 'Manufacturer name',
  model STRING COMMENT 'Model number',
  purchase_date DATE COMMENT 'Acquisition date',
  purchase_cost DECIMAL(18,2) COMMENT 'Original cost (Sensitive)',
  current_value DECIMAL(18,2) COMMENT 'Depreciated value',
  location STRING COMMENT 'Physical location',
  assigned_to STRING COMMENT 'Employee ID if assigned',
  latitude DOUBLE COMMENT 'GPS latitude',
  longitude DOUBLE COMMENT 'GPS longitude',
  warranty_expiry DATE COMMENT 'Warranty end date',
  maintenance_schedule STRING COMMENT 'Maintenance frequency',
  criticality STRING COMMENT 'Business criticality: Low/Medium/High/Critical',
  status STRING DEFAULT 'Active' COMMENT 'Asset status',
  CONSTRAINT pk_assets_test PRIMARY KEY (asset_id)
) USING DELTA
COMMENT 'Test table: Asset/Inventory tracking for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO assets_test (asset_id, asset_name, asset_type, serial_number, manufacturer, model, purchase_date, purchase_cost, current_value, location, assigned_to, latitude, longitude, warranty_expiry, maintenance_schedule, criticality, status) VALUES
('AST-001', 'MacBook Pro 16', 'Hardware', 'SN-APPLE-001234', 'Apple', 'MacBook Pro 16 M3', '2024-01-10', 3499.00, 3200.00, 'New York Office', 'EMP-001', 40.7128, -74.0060, '2027-01-10', 'Annual', 'High', 'Active'),
('AST-002', 'Dell Server Rack', 'Hardware', 'SN-DELL-005678', 'Dell', 'PowerEdge R750', '2023-06-15', 15000.00, 12000.00, 'Data Center A', NULL, 37.7749, -122.4194, '2026-06-15', 'Quarterly', 'Critical', 'Active'),
('AST-003', 'Company Vehicle', 'Vehicle', 'VIN-12345678901234567', 'Tesla', 'Model Y', '2023-09-01', 55000.00, 48000.00, 'Los Angeles Office', 'EMP-005', 34.0522, -118.2437, '2027-09-01', 'Monthly', 'Medium', 'Active'),
('AST-004', 'Cisco Switch', 'Hardware', 'SN-CISCO-009012', 'Cisco', 'Catalyst 9300', '2022-03-20', 8500.00, 5500.00, 'Data Center B', NULL, 41.8781, -87.6298, '2025-03-20', 'Bi-Annual', 'Critical', 'Active'),
('AST-005', 'Salesforce License', 'Software', 'LIC-SF-2024-001', 'Salesforce', 'Enterprise Edition', '2024-01-01', 18000.00, 18000.00, 'Cloud', NULL, NULL, NULL, '2024-12-31', 'N/A', 'High', 'Active'),
('AST-006', 'Office Printer', 'Hardware', 'SN-HP-003456', 'HP', 'LaserJet Pro MFP', '2023-11-10', 1200.00, 1000.00, 'Chicago Office', NULL, 41.8781, -87.6298, '2025-11-10', 'Monthly', 'Low', 'Active'),
('AST-007', 'Conference Room System', 'Hardware', 'SN-ZOOM-007890', 'Zoom', 'Rooms Kit', '2023-08-05', 4500.00, 3800.00, 'New York Office', NULL, 40.7128, -74.0060, '2025-08-05', 'Quarterly', 'Medium', 'Active'),
('AST-008', 'Forklift', 'Vehicle', 'SN-CAT-112233', 'Caterpillar', 'DP25N', '2021-04-15', 35000.00, 22000.00, 'Warehouse A', 'EMP-009', 40.7282, -73.7949, '2024-04-15', 'Weekly', 'High', 'Active');

-- =============================================================================
-- TABLE 5: AUDIT_LOG - System access/activity log
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log_test (
  log_id STRING NOT NULL COMMENT 'Unique log entry ID',
  event_timestamp TIMESTAMP NOT NULL COMMENT 'Event timestamp',
  user_id STRING COMMENT 'User who performed action',
  user_email STRING COMMENT 'User email (PII)',
  ip_address STRING COMMENT 'Client IP (PII)',
  user_agent STRING COMMENT 'Browser/client info',
  action_type STRING COMMENT 'Action: Login, Logout, Read, Write, Delete, etc.',
  resource_type STRING COMMENT 'Resource type: Table, File, API, etc.',
  resource_name STRING COMMENT 'Resource identifier',
  action_status STRING COMMENT 'Success, Failure, Denied',
  error_message STRING COMMENT 'Error details if failed',
  session_id STRING COMMENT 'Session identifier',
  request_id STRING COMMENT 'Unique request ID',
  duration_ms INT COMMENT 'Action duration in milliseconds',
  data_accessed_bytes BIGINT COMMENT 'Data volume accessed',
  sensitive_data_flag BOOLEAN DEFAULT FALSE COMMENT 'Sensitive data accessed',
  CONSTRAINT pk_audit_log_test PRIMARY KEY (log_id)
) USING DELTA
COMMENT 'Test table: System audit/access log for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO audit_log_test (log_id, event_timestamp, user_id, user_email, ip_address, user_agent, action_type, resource_type, resource_name, action_status, error_message, session_id, request_id, duration_ms, data_accessed_bytes, sensitive_data_flag) VALUES
('LOG-000001', '2024-01-15 08:00:15', 'U-1001', 'john.smith@example.com', '192.168.1.100', 'Mozilla/5.0 Chrome/120', 'Login', 'System', 'auth_service', 'Success', NULL, 'SES-001', 'REQ-0001', 245, 0, FALSE),
('LOG-000002', '2024-01-15 08:05:30', 'U-1001', 'john.smith@example.com', '192.168.1.100', 'Mozilla/5.0 Chrome/120', 'Read', 'Table', 'customers', 'Success', NULL, 'SES-001', 'REQ-0002', 1250, 524288, TRUE),
('LOG-000003', '2024-01-15 08:10:45', 'U-1001', 'john.smith@example.com', '192.168.1.100', 'Mozilla/5.0 Chrome/120', 'Write', 'Table', 'orders', 'Success', NULL, 'SES-001', 'REQ-0003', 890, 2048, FALSE),
('LOG-000004', '2024-01-15 09:00:00', 'U-1002', 'sarah.johnson@example.com', '10.0.1.50', 'Mozilla/5.0 Firefox/121', 'Login', 'System', 'auth_service', 'Success', NULL, 'SES-002', 'REQ-0004', 198, 0, FALSE),
('LOG-000005', '2024-01-15 09:15:22', 'U-1002', 'sarah.johnson@example.com', '10.0.1.50', 'Mozilla/5.0 Firefox/121', 'Read', 'Table', 'transactions', 'Success', NULL, 'SES-002', 'REQ-0005', 2100, 1048576, TRUE),
('LOG-000006', '2024-01-15 09:30:00', 'U-1003', 'mike.williams@example.com', '172.16.0.25', 'Mozilla/5.0 Safari/17', 'Login', 'System', 'auth_service', 'Failure', 'Invalid password', NULL, 'REQ-0006', 156, 0, FALSE),
('LOG-000007', '2024-01-15 09:31:00', 'U-1003', 'mike.williams@example.com', '172.16.0.25', 'Mozilla/5.0 Safari/17', 'Login', 'System', 'auth_service', 'Failure', 'Invalid password', NULL, 'REQ-0007', 145, 0, FALSE),
('LOG-000008', '2024-01-15 09:32:00', 'U-1003', 'mike.williams@example.com', '172.16.0.25', 'Mozilla/5.0 Safari/17', 'Login', 'System', 'auth_service', 'Denied', 'Account locked', NULL, 'REQ-0008', 89, 0, FALSE),
('LOG-000009', '2024-01-15 10:00:00', 'EMP-004', 'patricia.thomas@company.com', '192.168.3.75', 'Internal API', 'Read', 'Table', 'employees', 'Success', NULL, 'SES-003', 'REQ-0009', 3500, 2097152, TRUE),
('LOG-000010', '2024-01-15 10:30:00', 'EMP-008', 'nancy.clark@company.com', '192.168.1.200', 'Internal API', 'Delete', 'Table', 'terminated_employees', 'Denied', 'Insufficient permissions', 'SES-004', 'REQ-0010', 45, 0, TRUE);
"""

# =============================================================================
# STEP 5: TAG APPLICATIONS (for test tables)
# =============================================================================
TAG_APPLICATIONS_SQL = """
-- =============================================================================
-- USERS_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn', 'data_classification' = 'Restricted', 'compliance_requirement' = 'GLBA');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN email SET TAGS ('pii_type' = 'email', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN phone SET TAGS ('pii_type' = 'phone', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN first_name SET TAGS ('pii_type' = 'name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN last_name SET TAGS ('pii_type' = 'name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN date_of_birth SET TAGS ('pii_type' = 'dob', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN street_address SET TAGS ('pii_type' = 'address', 'data_classification' = 'Confidential');

-- =============================================================================
-- TRANSACTIONS_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN account_number SET TAGS ('pii_type' = 'account_number', 'data_classification' = 'Restricted', 'compliance_requirement' = 'PCI_DSS');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN card_number SET TAGS ('pii_type' = 'credit_card', 'data_classification' = 'Restricted', 'compliance_requirement' = 'PCI_DSS');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN ip_address SET TAGS ('pii_type' = 'ip_address', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN device_id SET TAGS ('pii_type' = 'device_id', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN amount SET TAGS ('pii_type' = 'financial_record', 'sensitivity_level' = 'High');

-- =============================================================================
-- EMPLOYEES_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn', 'data_classification' = 'Restricted', 'data_purpose' = 'HR');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN email SET TAGS ('pii_type' = 'email', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN phone SET TAGS ('pii_type' = 'phone', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN first_name SET TAGS ('pii_type' = 'name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN last_name SET TAGS ('pii_type' = 'name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN date_of_birth SET TAGS ('pii_type' = 'dob', 'data_classification' = 'Confidential', 'data_purpose' = 'HR');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN salary SET TAGS ('sensitivity_level' = 'High', 'data_purpose' = 'HR', 'data_classification' = 'Restricted');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN bonus SET TAGS ('sensitivity_level' = 'High', 'data_purpose' = 'HR', 'data_classification' = 'Restricted');

-- =============================================================================
-- ASSETS_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN serial_number SET TAGS ('pii_type' = 'device_id', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN purchase_cost SET TAGS ('sensitivity_level' = 'Medium', 'data_purpose' = 'Operations');
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN latitude SET TAGS ('pii_type' = 'location', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN longitude SET TAGS ('pii_type' = 'location', 'data_classification' = 'Internal');

-- =============================================================================
-- AUDIT_LOG_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test ALTER COLUMN user_email SET TAGS ('pii_type' = 'email', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test ALTER COLUMN ip_address SET TAGS ('pii_type' = 'ip_address', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test ALTER COLUMN event_timestamp SET TAGS ('sensitivity_level' = 'High', 'data_purpose' = 'Audit');
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test SET TAGS ('access_restriction' = 'Business_Hours');
"""

# List of test tables created
TEST_TABLES = ["users_test", "transactions_test", "employees_test", "assets_test", "audit_log_test"]
