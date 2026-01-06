"""
Default Industry ABAC Template
Generic SQL definitions that work across all industries
"""

# Industry metadata
INDUSTRY_NAME = "Default"
INDUSTRY_DESCRIPTION = "Generic ABAC template with common masking functions applicable to any industry"

# Step 1: Function Definitions
FUNCTIONS_SQL = """
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask SSN showing last 4 digits (XXX-XX-1234)'
RETURN CASE 
  WHEN ssn IS NULL THEN ssn 
  ELSE CONCAT('XXX-XX-', RIGHT(REPLACE(ssn, '-', ''), 4)) 
END;

CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask email local part, shows domain'
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
  ELSE CONCAT('XXX-XXX-', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4))
END;

CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask credit card number showing only last 4 digits'
RETURN CASE
  WHEN card_number IS NULL THEN card_number
  ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card_number, '[^0-9]', ''), 4))
END;

CREATE OR REPLACE FUNCTION mask_account_last4(account_number STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask account number showing only last 4 digits'
RETURN CASE
  WHEN account_number IS NULL THEN account_number
  ELSE CONCAT('********', RIGHT(account_number, 4))
END;

CREATE OR REPLACE FUNCTION mask_id_hash(id STRING)
RETURNS STRING
COMMENT 'ABAC utility: Deterministic ID masking for joins'
RETURN CONCAT('ID_', SUBSTRING(SHA2(id, 256), 1, 12));

CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask IP address to subnet level'
RETURN CASE
  WHEN ip IS NULL THEN ip
  ELSE CONCAT(SPLIT(ip, '\\\\.')[0], '.', SPLIT(ip, '\\\\.')[1], '.***.***')
END;

CREATE OR REPLACE FUNCTION mask_amount_bucket(amount DECIMAL(18,2))
RETURNS STRING
COMMENT 'ABAC utility: Bucket amounts into ranges'
RETURN CASE 
  WHEN amount IS NULL THEN 'Unknown' 
  WHEN amount < 100 THEN '$0-$100'
  WHEN amount < 1000 THEN '$100-$1K'
  WHEN amount < 10000 THEN '$1K-$10K' 
  WHEN amount < 100000 THEN '$10K-$100K' 
  ELSE '$100K+' 
END;

CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours (9 AM - 5 PM UTC)'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

CREATE OR REPLACE FUNCTION filter_high_value(amount DECIMAL(18,2))
RETURNS BOOLEAN
COMMENT 'ABAC utility: Filter for high-value records (> $10000)'
RETURN amount > 10000;
"""

# Step 2: Tag Policy Definitions (tag_key, description, allowed_values)
TAG_DEFINITIONS = [
    ("pii_type", "PII field types for data masking", 
     ["ssn", "email", "phone", "credit_card", "account", "id", "ip_address", "amount"]),
    
    ("data_classification", "Data classification level",
     ["Public", "Internal", "Confidential", "Restricted"]),
    
    ("compliance_type", "Compliance requirement type",
     ["PCI", "HIPAA", "GDPR", "SOX", "None"]),
    
    ("sensitivity_level", "Data sensitivity level",
     ["Low", "Medium", "High", "Critical"])
]

# Step 3: ABAC Policy Definitions (at Catalog level)
ABAC_POLICIES_SQL = """
-- SSN Column Mask Policy (Catalog Level)
CREATE OR REPLACE POLICY ssn_mask ON CATALOG {CATALOG}
COMMENT 'Mask SSN columns tagged with pii_type=ssn'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type','ssn') AS ssn
ON COLUMN ssn;

-- Email Column Mask Policy (Catalog Level)
CREATE OR REPLACE POLICY email_mask ON CATALOG {CATALOG}
COMMENT 'Mask email columns tagged with pii_type=email'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type','email') AS email
ON COLUMN email;

-- Phone Column Mask Policy (Catalog Level)
CREATE OR REPLACE POLICY phone_mask ON CATALOG {CATALOG}
COMMENT 'Mask phone columns tagged with pii_type=phone'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type','phone') AS phone
ON COLUMN phone;

-- Credit Card Column Mask Policy (Catalog Level)
CREATE OR REPLACE POLICY card_mask ON CATALOG {CATALOG}
COMMENT 'Mask credit card columns tagged with pii_type=credit_card'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_credit_card 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type','credit_card') AS card
ON COLUMN card;

-- Account Number Column Mask Policy (Catalog Level)
CREATE OR REPLACE POLICY account_mask ON CATALOG {CATALOG}
COMMENT 'Mask account columns tagged with pii_type=account'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_account_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type','account') AS account
ON COLUMN account;

-- ID Hash Column Mask Policy (Catalog Level)
CREATE OR REPLACE POLICY id_mask ON CATALOG {CATALOG}
COMMENT 'Hash ID columns tagged with pii_type=id'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_id_hash 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type','id') AS id_col
ON COLUMN id_col;
"""

# Step 4: Test Table Creation (Optional - with _test suffix)
TEST_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS users_test (
  user_id STRING, 
  first_name STRING, 
  last_name STRING, 
  ssn STRING,
  email STRING, 
  phone STRING,
  created_at TIMESTAMP,
  CONSTRAINT pk_users PRIMARY KEY (user_id)
) USING DELTA;

INSERT INTO users_test VALUES
('U-1001', 'John', 'Smith', '123-45-6789', 'john@example.com', '555-123-4567', current_timestamp()),
('U-1002', 'Sarah', 'Johnson', '234-56-7890', 'sarah@example.com', '555-234-5678', current_timestamp()),
('U-1003', 'Mike', 'Williams', '345-67-8901', 'mike@example.com', '555-345-6789', current_timestamp()),
('U-1004', 'Emily', 'Brown', '456-78-9012', 'emily@example.com', '555-456-7890', current_timestamp()),
('U-1005', 'David', 'Jones', '567-89-0123', 'david@example.com', '555-567-8901', current_timestamp());

CREATE TABLE IF NOT EXISTS accounts_test (
  account_id STRING,
  user_id STRING,
  account_number STRING,
  account_type STRING,
  balance DECIMAL(18,2),
  status STRING,
  CONSTRAINT pk_accounts PRIMARY KEY (account_id)
) USING DELTA;

INSERT INTO accounts_test VALUES
('A-5001', 'U-1001', '1234567890', 'Checking', 5420.50, 'Active'),
('A-5002', 'U-1001', '0987654321', 'Savings', 15000.00, 'Active'),
('A-5003', 'U-1002', '1122334455', 'Checking', 8750.25, 'Active'),
('A-5004', 'U-1003', '5566778899', 'Savings', 25000.00, 'Active'),
('A-5005', 'U-1004', '9988776655', 'Checking', 3200.75, 'Active');

CREATE TABLE IF NOT EXISTS transactions_test (
  transaction_id STRING,
  account_id STRING,
  user_id STRING,
  amount DECIMAL(18,2),
  transaction_type STRING,
  merchant STRING,
  ip_address STRING,
  transaction_date TIMESTAMP,
  CONSTRAINT pk_transactions PRIMARY KEY (transaction_id)
) USING DELTA;

INSERT INTO transactions_test VALUES
('TXN-1001', 'A-5001', 'U-1001', 125.50, 'Purchase', 'Amazon', '192.168.1.100', current_timestamp()),
('TXN-1002', 'A-5001', 'U-1001', 85.75, 'Purchase', 'Whole Foods', '192.168.1.101', current_timestamp()),
('TXN-1003', 'A-5003', 'U-1002', 5500.00, 'Transfer', 'Wire Transfer', '10.0.1.50', current_timestamp()),
('TXN-1004', 'A-5004', 'U-1003', 15000.00, 'Deposit', 'Direct Deposit', '172.16.0.25', current_timestamp()),
('TXN-1005', 'A-5002', 'U-1001', 250.00, 'Withdrawal', 'ATM', '192.168.1.102', current_timestamp());
"""

# Step 5: Tag Applications (Optional - for test tables only)
TAG_APPLICATIONS_SQL = """
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN email SET TAGS ('pii_type' = 'email');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN phone SET TAGS ('pii_type' = 'phone');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN user_id SET TAGS ('pii_type' = 'id');

ALTER TABLE {CATALOG}.{SCHEMA}.accounts_test ALTER COLUMN account_number SET TAGS ('pii_type' = 'account', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.accounts_test ALTER COLUMN user_id SET TAGS ('pii_type' = 'id');

ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN ip_address SET TAGS ('pii_type' = 'ip_address');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN amount SET TAGS ('pii_type' = 'amount');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN user_id SET TAGS ('pii_type' = 'id');
"""

# List of test tables created
TEST_TABLES = ["users_test", "accounts_test", "transactions_test"]

