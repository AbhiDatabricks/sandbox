-- =============================================
-- FINANCE ABAC MASKING FUNCTIONS
-- Purpose: Attribute-Based Access Control (ABAC) utility functions for financial data
-- Domain: Banking, Payments, Credit, Compliance
-- =============================================

USE CATALOG apscat;
USE SCHEMA finance;

-- =============================================
-- MASKING FUNCTIONS FOR FINANCIAL DATA
-- =============================================

-- =============================================
-- 1. CREDIT CARD MASKING (Last 4 digits)
-- Purpose: Show only last 4 digits of credit card (PCI-DSS compliance)
-- Usage: Credit card numbers for verification
-- =============================================
CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask credit card showing last 4 digits (PCI-DSS compliant)'
RETURN CASE 
  WHEN card_number IS NULL OR card_number = '' THEN card_number
  WHEN LENGTH(card_number) < 4 THEN REPEAT('*', LENGTH(card_number))
  ELSE CONCAT('****-****-****-', RIGHT(card_number, 4))
END;

-- =============================================
-- 2. ACCOUNT NUMBER MASKING (Last 4 digits)
-- Purpose: Mask bank account numbers showing last 4
-- Usage: Account verification without full exposure
-- =============================================
CREATE OR REPLACE FUNCTION mask_account_last4(account_number STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask account number showing last 4 digits'
RETURN CASE 
  WHEN account_number IS NULL OR account_number = '' THEN account_number
  WHEN LENGTH(account_number) < 4 THEN REPEAT('*', LENGTH(account_number))
  ELSE CONCAT('****', RIGHT(account_number, 4))
END;

-- =============================================
-- 3. SSN MASKING (Last 4 digits)
-- Purpose: Mask SSN showing last 4 for identity verification
-- Usage: Customer identification
-- =============================================
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask SSN showing last 4 digits (XXX-XX-1234)'
RETURN CASE 
  WHEN ssn IS NULL OR ssn = '' THEN ssn
  WHEN LENGTH(ssn) < 4 THEN REPEAT('*', LENGTH(ssn))
  ELSE CONCAT('XXX-XX-', RIGHT(REPLACE(ssn, '-', ''), 4))
END;

-- =============================================
-- 4. AMOUNT BUCKETING (Transaction amounts)
-- Purpose: Group transaction amounts into ranges
-- Usage: Analytics without exact amounts
-- =============================================
CREATE OR REPLACE FUNCTION mask_amount_bucket(amount DECIMAL(18,2))
RETURNS STRING
COMMENT 'ABAC utility: Bucket transaction amounts into ranges'
RETURN CASE
  WHEN amount IS NULL THEN 'Unknown'
  WHEN amount < 0 THEN 'Negative'
  WHEN amount = 0 THEN '$0'
  WHEN amount < 100 THEN '$0-$100'
  WHEN amount < 500 THEN '$100-$500'
  WHEN amount < 1000 THEN '$500-$1K'
  WHEN amount < 5000 THEN '$1K-$5K'
  WHEN amount < 10000 THEN '$5K-$10K'
  WHEN amount < 50000 THEN '$10K-$50K'
  WHEN amount < 100000 THEN '$50K-$100K'
  ELSE '$100K+'
END;

-- =============================================
-- 5. ROUTING NUMBER MASKING
-- Purpose: Mask routing numbers for bank transfers
-- Usage: Payment processing
-- =============================================
CREATE OR REPLACE FUNCTION mask_routing_number(routing STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask routing number showing last 3 digits'
RETURN CASE 
  WHEN routing IS NULL OR routing = '' THEN routing
  WHEN LENGTH(routing) < 3 THEN REPEAT('*', LENGTH(routing))
  ELSE CONCAT('XXXXX', RIGHT(routing, 3))
END;

-- =============================================
-- 6. EMAIL MASKING
-- Purpose: Mask email addresses for privacy
-- Usage: Customer contact information
-- =============================================
CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask email local part'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN email NOT LIKE '%@%' THEN '****'
  ELSE CONCAT('****@', SPLIT(email, '@')[1])
END;

-- =============================================
-- 7. PHONE MASKING
-- Purpose: Mask phone numbers
-- Usage: Customer contact information
-- =============================================
CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask phone number showing last 4 digits'
RETURN CASE 
  WHEN phone IS NULL OR phone = '' THEN phone
  WHEN LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '')) < 4 THEN 'XXXX'
  ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4))
END;

-- =============================================
-- 8. TRANSACTION ID HASHING
-- Purpose: Hash transaction IDs for privacy
-- Usage: Transaction tracking without exposure
-- =============================================
CREATE OR REPLACE FUNCTION mask_transaction_hash(txn_id STRING)
RETURNS STRING
COMMENT 'ABAC utility: Hash transaction ID using SHA-256'
RETURN CASE 
  WHEN txn_id IS NULL OR txn_id = '' THEN txn_id
  ELSE CONCAT('TXN_', SUBSTRING(SHA2(txn_id, 256), 1, 16))
END;

-- =============================================
-- 9. CUSTOMER ID DETERMINISTIC MASKING
-- Purpose: Deterministic masking for cross-table joins
-- Usage: Customer analytics while preserving privacy
-- =============================================
CREATE OR REPLACE FUNCTION mask_customer_id_deterministic(customer_id STRING)
RETURNS STRING
COMMENT 'ABAC utility: Deterministic customer ID masking for joins'
RETURN CASE 
  WHEN customer_id IS NULL OR customer_id = '' THEN customer_id
  ELSE CONCAT('CUST_', SUBSTRING(SHA2(customer_id, 256), 1, 12))
END;

-- =============================================
-- 10. IP ADDRESS MASKING (Last octet)
-- Purpose: Mask IP addresses showing network portion only
-- Usage: Fraud detection without full IP exposure
-- =============================================
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask last octet of IP address'
RETURN CASE 
  WHEN ip IS NULL OR ip = '' THEN ip
  WHEN ip NOT LIKE '%.%.%.%' THEN '***'
  ELSE CONCAT(
    SPLIT(ip, '\\.')[0], '.',
    SPLIT(ip, '\\.')[1], '.',
    SPLIT(ip, '\\.')[2], '.***'
  )
END;

-- =============================================
-- 11. ADDRESS PARTIAL MASKING
-- Purpose: Show only city/state, hide street address
-- Usage: Geographic analysis without full address
-- =============================================
CREATE OR REPLACE FUNCTION mask_address_city_state(full_address STRING)
RETURNS STRING
COMMENT 'ABAC utility: Extract city/state from full address'
RETURN CASE 
  WHEN full_address IS NULL OR full_address = '' THEN full_address
  WHEN full_address LIKE '%,%' THEN 
    -- Assume format: "Street, City, State ZIP"
    CONCAT(
      COALESCE(SPLIT(full_address, ',')[1], '***'), ', ',
      COALESCE(SUBSTRING(SPLIT(full_address, ',')[2], 1, 2), '**')
    )
  ELSE '[REDACTED]'
END;

-- =============================================
-- 12. SALARY/INCOME BUCKETING
-- Purpose: Group salary/income into ranges
-- Usage: Credit analysis without exact figures
-- =============================================
CREATE OR REPLACE FUNCTION mask_income_bracket(income DECIMAL(18,2))
RETURNS STRING
COMMENT 'ABAC utility: Bucket income into ranges'
RETURN CASE
  WHEN income IS NULL THEN 'Unknown'
  WHEN income < 0 THEN 'Invalid'
  WHEN income < 25000 THEN 'Under $25K'
  WHEN income < 50000 THEN '$25K-$50K'
  WHEN income < 75000 THEN '$50K-$75K'
  WHEN income < 100000 THEN '$75K-$100K'
  WHEN income < 150000 THEN '$100K-$150K'
  WHEN income < 250000 THEN '$150K-$250K'
  ELSE '$250K+'
END;

-- =============================================
-- ROW FILTER FUNCTIONS
-- =============================================

-- =============================================
-- 13. BUSINESS HOURS FILTER
-- Purpose: Restrict access to business hours (9AM-5PM EST)
-- Usage: Compliance with data access policies
-- =============================================
CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

-- =============================================
-- 14. HIGH VALUE TRANSACTION FILTER
-- Purpose: Filter transactions above certain threshold
-- Usage: Junior analysts see only regular transactions
-- =============================================
CREATE OR REPLACE FUNCTION filter_high_value_transactions()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Filter out high-value transactions'
RETURN TRUE;  -- Placeholder; actual implementation uses transaction amount column

-- =============================================
-- 15. FRAUD INVESTIGATION FILTER
-- Purpose: Show only flagged/suspicious transactions
-- Usage: Fraud team access
-- =============================================
CREATE OR REPLACE FUNCTION filter_fraud_flagged_only()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Show only fraud-flagged records'
RETURN TRUE;  -- Placeholder; actual implementation checks fraud_flag column

-- =============================================
-- 16. REGIONAL ACCESS FILTER
-- Purpose: Restrict data by geographic region
-- Usage: Regional compliance (GDPR, state regulations)
-- =============================================
CREATE OR REPLACE FUNCTION filter_by_region()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Filter data by user region'
RETURN TRUE;  -- Placeholder; actual implementation uses user session attributes

-- Verify all functions created
SHOW FUNCTIONS IN apscat.finance LIKE 'mask_%';
SHOW FUNCTIONS IN apscat.finance LIKE 'filter_%';

SELECT '✅ Finance ABAC functions created successfully!' AS status;

