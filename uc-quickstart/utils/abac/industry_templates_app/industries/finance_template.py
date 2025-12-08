"""
Finance Industry ABAC Template
All SQL definitions for finance industry
"""

# Industry metadata
INDUSTRY_NAME = "Finance"
INDUSTRY_DESCRIPTION = "Banking, credit cards, loans, and financial transactions"

# Step 1: Function Definitions
FUNCTIONS_SQL = """
CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'Masks credit card number showing only last 4 digits'
RETURN CONCAT('****-****-****-', SUBSTRING(card_number, -4, 4));

CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING)
RETURNS STRING
COMMENT 'Masks SSN showing only last 4 digits'
RETURN CONCAT('***-**-', SUBSTRING(ssn, -4, 4));

CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'Masks email local part, shows domain'
RETURN CONCAT('***@', SPLIT(email, '@')[1]);

CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'Masks phone number showing only last 4 digits'
RETURN CONCAT('***-***-', SUBSTRING(phone, -4, 4));

CREATE OR REPLACE FUNCTION mask_account_last4(account_number STRING)
RETURNS STRING
COMMENT 'Masks account number showing only last 4 digits'
RETURN CONCAT('********', SUBSTRING(account_number, -4, 4));

CREATE OR REPLACE FUNCTION mask_routing_number(routing_number STRING)
RETURNS STRING
COMMENT 'Masks routing number showing only last 2 digits'
RETURN CONCAT('*******', SUBSTRING(routing_number, -2, 2));

CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'Masks IP address to subnet level'
RETURN CONCAT(
    SPLIT(ip, '\\\\.')[0], '.',
    SPLIT(ip, '\\\\.')[1], '.',
    '***', '.',
    '***'
);

CREATE OR REPLACE FUNCTION mask_income_bracket(income DECIMAL(18,2))
RETURNS DECIMAL(18,2)
COMMENT 'Masks income by rounding to nearest bracket (returns 0 for privacy)'
RETURN CAST(0 AS DECIMAL(18,2));

CREATE OR REPLACE FUNCTION filter_fraud_flagged_only(fraud_flag BOOLEAN)
RETURNS BOOLEAN
COMMENT 'Row filter to show only fraud-flagged transactions'
RETURN fraud_flag = TRUE;

CREATE OR REPLACE FUNCTION filter_high_value_transactions(amount DECIMAL(18,2))
RETURNS BOOLEAN
COMMENT 'Row filter for transactions over $5000'
RETURN amount > 5000;
"""

# Step 2: Tag Policy Definitions (tag_key, description, allowed_values)
TAG_DEFINITIONS = [
    ("pii_type_finance", "PII field types for finance industry", 
     ["ssn", "email", "location", "phone", "income", "account", "routing_number", 
      "ip_address", "credit_card", "transaction_amount", "transaction_id", "id"]),
    
    ("pci_compliance_finance", "PCI-DSS compliance requirement for finance",
     ["Required", "Not_Required"]),
    
    ("data_classification_finance", "Data classification level for finance",
     ["Confidential", "Internal", "Public"]),
    
    ("fraud_detection_finance", "Fraud detection flag for finance",
     ["true", "false"])
]

# Step 3: ABAC Policy Definitions
# Syntax per https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/policies
ABAC_POLICIES_SQL = """
-- SSN Column Mask Policy
CREATE OR REPLACE POLICY ssn_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask SSN columns tagged with pii_type_finance=ssn'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn_last4
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'ssn') AS ssn_col
ON COLUMN ssn_col;

-- Email Column Mask Policy
CREATE OR REPLACE POLICY email_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask email columns tagged with pii_type_finance=email'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'email') AS email_col
ON COLUMN email_col;

-- Phone Column Mask Policy
CREATE OR REPLACE POLICY phone_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask phone columns tagged with pii_type_finance=phone'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'phone') AS phone_col
ON COLUMN phone_col;

-- Credit Card Column Mask Policy
CREATE OR REPLACE POLICY card_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask credit card columns tagged with pii_type_finance=credit_card'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_credit_card
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'credit_card') AS card_col
ON COLUMN card_col;

-- Account Number Column Mask Policy
CREATE OR REPLACE POLICY account_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask account columns tagged with pii_type_finance=account'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_account_last4
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'account') AS account_col
ON COLUMN account_col;

-- Income Bracket Column Mask Policy
CREATE OR REPLACE POLICY income_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask income columns tagged with pii_type_finance=income'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_income_bracket
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'income') AS income_col
ON COLUMN income_col;
"""

# Step 4: Test Table Creation (Optional - with _test suffix)
TEST_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS customers_test (
  customer_id STRING NOT NULL,
  first_name STRING NOT NULL,
  last_name STRING NOT NULL,
  ssn STRING,
  date_of_birth DATE,
  email STRING,
  phone STRING,
  address STRING,
  city STRING,
  state STRING,
  zip_code STRING,
  annual_income DECIMAL(18,2),
  credit_score INT,
  customer_since DATE
);

INSERT INTO customers_test VALUES
('C-1001', 'John', 'Smith', '123-45-6789', '1985-03-15', 'john.smith@email.com', '234-555-0101', '123 Main St', 'New York', 'NY', '10001', 75000.00, 720, '2020-01-15'),
('C-1002', 'Sarah', 'Johnson', '234-56-7890', '1990-07-22', 'sarah.j@email.com', '232-555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001', 95000.00, 780, '2019-05-20'),
('C-1003', 'Michael', 'Williams', '345-67-8901', '1982-11-30', 'mike.w@email.com', '232-555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601', 82000.00, 705, '2021-03-10');

CREATE TABLE IF NOT EXISTS accounts_test (
  account_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  account_type STRING,
  account_number STRING,
  routing_number STRING,
  balance DECIMAL(18,2),
  opened_date DATE,
  status STRING
);

INSERT INTO accounts_test VALUES
('A-5001', 'C-1001', 'Checking', '1001234567', '021000021', 5420.50, '2020-01-15', 'Active'),
('A-5002', 'C-1001', 'Savings', '1001234568', '021000021', 15000.00, '2020-01-15', 'Active'),
('A-5003', 'C-1002', 'Checking', '1002345678', '121000248', 8750.25, '2019-05-20', 'Active');

CREATE TABLE IF NOT EXISTS credit_cards_test (
  card_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  card_number STRING,
  card_type STRING,
  credit_limit DECIMAL(18,2),
  current_balance DECIMAL(18,2),
  available_credit DECIMAL(18,2),
  apr_rate DECIMAL(5,2),
  card_opened_date DATE,
  expiration_date DATE,
  status STRING
);

INSERT INTO credit_cards_test VALUES
('CC-8001', 'C-1001', '4532-1234-5678-9010', 'Visa', 10000.00, 2450.75, 7549.25, 18.99, '2020-02-01', '2025-02-01', 'Active'),
('CC-8002', 'C-1002', '5425-2345-6789-0123', 'Mastercard', 15000.00, 4200.50, 10799.50, 16.99, '2019-06-15', '2024-06-15', 'Active');

CREATE TABLE IF NOT EXISTS transactions_test (
  transaction_id STRING NOT NULL,
  account_id STRING,
  card_id STRING,
  customer_id STRING NOT NULL,
  transaction_type STRING,
  amount DECIMAL(18,2),
  merchant_name STRING,
  merchant_category STRING,
  transaction_date TIMESTAMP,
  ip_address STRING,
  device_type STRING,
  fraud_flag BOOLEAN,
  status STRING
);

INSERT INTO transactions_test VALUES
('TXN-10001', 'A-5001', NULL, 'C-1001', 'Debit', 85.50, 'Amazon', 'Retail', timestamp('2024-03-01 10:15:30'), '192.168.1.100', 'Mobile', false, 'Completed'),
('TXN-10002', NULL, 'CC-8001', 'C-1001', 'Credit', 125.75, 'Whole Foods', 'Grocery', timestamp('2024-03-01 14:22:15'), '192.168.1.100', 'Mobile', false, 'Completed'),
('TXN-10003', 'A-5003', NULL, 'C-1002', 'Debit', 5500.00, 'Apple Store', 'Electronics', timestamp('2024-03-02 11:30:00'), '10.0.1.50', 'Desktop', false, 'Completed'),
('TXN-10004', NULL, 'CC-8002', 'C-1002', 'Credit', 450.00, 'Southwest Airlines', 'Travel', timestamp('2024-03-03 08:45:00'), '10.0.1.50', 'Desktop', false, 'Completed'),
('TXN-10005', 'A-5001', NULL, 'C-1001', 'Debit', 15.25, 'Starbucks', 'Food', timestamp('2024-03-04 07:30:00'), '192.168.1.101', 'Mobile', false, 'Completed'),
('TXN-10006', NULL, 'CC-8001', 'C-1001', 'Credit', 8500.00, 'Suspicious Merchant', 'Unknown', timestamp('2024-03-05 02:15:00'), '203.0.113.0', 'Desktop', true, 'Flagged');
"""

# Step 5: Tag Applications (Optional - for test tables only)
# Uses {CATALOG}.{SCHEMA} placeholders for fully qualified names
TAG_APPLICATIONS_SQL = """
ALTER TABLE {CATALOG}.{SCHEMA}.customers_test ALTER COLUMN ssn SET TAGS ('pii_type_finance' = 'ssn', 'pci_compliance_finance' = 'Required');
ALTER TABLE {CATALOG}.{SCHEMA}.customers_test ALTER COLUMN email SET TAGS ('pii_type_finance' = 'email');
ALTER TABLE {CATALOG}.{SCHEMA}.customers_test ALTER COLUMN phone SET TAGS ('pii_type_finance' = 'phone');
ALTER TABLE {CATALOG}.{SCHEMA}.customers_test ALTER COLUMN annual_income SET TAGS ('pii_type_finance' = 'income', 'data_classification_finance' = 'Confidential');

ALTER TABLE {CATALOG}.{SCHEMA}.accounts_test ALTER COLUMN account_number SET TAGS ('pii_type_finance' = 'account', 'data_classification_finance' = 'Confidential');

ALTER TABLE {CATALOG}.{SCHEMA}.credit_cards_test ALTER COLUMN card_number SET TAGS ('pii_type_finance' = 'credit_card', 'pci_compliance_finance' = 'Required');

ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN ip_address SET TAGS ('pii_type_finance' = 'ip_address');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN amount SET TAGS ('pii_type_finance' = 'transaction_amount');
"""

# List of test tables created
TEST_TABLES = ["customers_test", "accounts_test", "credit_cards_test", "transactions_test"]
