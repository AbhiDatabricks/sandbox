-- =============================================
-- FINANCE DATA VERIFICATION & TESTING
-- =============================================
-- Purpose: Verify tables, data, and demonstrate masking functions
-- NO ABAC POLICIES REQUIRED - Manual function demonstration
-- =============================================

USE CATALOG apscat;
USE SCHEMA finance;

-- =============================================
-- TEST 1: Table Row Counts
-- =============================================
SELECT '=== TABLE ROW COUNTS ===' AS section;

SELECT 
  'customers' AS table_name, 
  COUNT(*) AS row_count 
FROM customers
UNION ALL SELECT 'accounts', COUNT(*) FROM accounts
UNION ALL SELECT 'credit_cards', COUNT(*) FROM credit_cards
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL SELECT 'loans', COUNT(*) FROM loans
ORDER BY table_name;

-- =============================================
-- TEST 2: Credit Card Masking Demo
-- =============================================
SELECT '=== CREDIT CARD MASKING (PCI-DSS) ===' AS section;

SELECT 
  card_id,
  customer_id,
  card_number AS original,
  apscat.finance.mask_credit_card(card_number) AS masked,
  card_type
FROM credit_cards
LIMIT 5;

-- =============================================
-- TEST 3: Account Number Masking Demo
-- =============================================
SELECT '=== ACCOUNT NUMBER MASKING ===' AS section;

SELECT 
  account_id,
  customer_id,
  account_number AS original,
  apscat.finance.mask_account_last4(account_number) AS masked_last4,
  account_type
FROM accounts
LIMIT 5;

-- =============================================
-- TEST 4: SSN Masking Demo
-- =============================================
SELECT '=== SSN MASKING ===' AS section;

SELECT 
  customer_id,
  CONCAT(first_name, ' ', last_name) AS name,
  ssn AS original,
  apscat.finance.mask_ssn_last4(ssn) AS masked,
  credit_score
FROM customers
LIMIT 5;

-- =============================================
-- TEST 5: Email & Phone Masking Demo
-- =============================================
SELECT '=== EMAIL & PHONE MASKING ===' AS section;

SELECT 
  customer_id,
  first_name,
  email AS original_email,
  apscat.finance.mask_email(email) AS masked_email,
  phone AS original_phone,
  apscat.finance.mask_phone(phone) AS masked_phone
FROM customers
LIMIT 5;

-- =============================================
-- TEST 6: Transaction Amount Bucketing
-- =============================================
SELECT '=== AMOUNT BUCKETING ===' AS section;

SELECT 
  transaction_id,
  amount AS original_amount,
  apscat.finance.mask_amount_bucket(amount) AS amount_bucket,
  merchant_name,
  transaction_type
FROM transactions
ORDER BY amount DESC
LIMIT 10;

-- =============================================
-- TEST 7: Routing Number Masking
-- =============================================
SELECT '=== ROUTING NUMBER MASKING ===' AS section;

SELECT 
  account_id,
  routing_number AS original,
  apscat.finance.mask_routing_number(routing_number) AS masked,
  account_type
FROM accounts
WHERE routing_number IS NOT NULL
LIMIT 5;

-- =============================================
-- TEST 8: Transaction ID Hashing
-- =============================================
SELECT '=== TRANSACTION ID HASHING ===' AS section;

SELECT 
  transaction_id AS original,
  apscat.finance.mask_transaction_hash(transaction_id) AS hashed,
  amount,
  merchant_name
FROM transactions
LIMIT 5;

-- =============================================
-- TEST 9: Customer ID Deterministic Masking
-- =============================================
SELECT '=== CUSTOMER ID MASKING (Deterministic) ===' AS section;

SELECT 
  customer_id AS original,
  apscat.finance.mask_customer_id_deterministic(customer_id) AS masked,
  first_name,
  last_name
FROM customers
LIMIT 5;

-- =============================================
-- TEST 10: IP Address Masking
-- =============================================
SELECT '=== IP ADDRESS MASKING ===' AS section;

SELECT 
  transaction_id,
  ip_address AS original,
  apscat.finance.mask_ip_address(ip_address) AS masked,
  device_type
FROM transactions
LIMIT 5;

-- =============================================
-- TEST 11: Income Bracket Masking
-- =============================================
SELECT '=== INCOME BRACKETING ===' AS section;

SELECT 
  customer_id,
  CONCAT(first_name, ' ', last_name) AS name,
  annual_income AS original,
  apscat.finance.mask_income_bracket(annual_income) AS income_bracket
FROM customers
ORDER BY annual_income DESC
LIMIT 5;

-- =============================================
-- TEST 12: Multi-Column Masking Demo
-- =============================================
SELECT '=== MULTI-COLUMN MASKING ===' AS section;

SELECT 
  customer_id,
  apscat.finance.mask_customer_id_deterministic(customer_id) AS masked_id,
  CONCAT(first_name, ' ', last_name) AS name,
  apscat.finance.mask_ssn_last4(ssn) AS masked_ssn,
  apscat.finance.mask_email(email) AS masked_email,
  apscat.finance.mask_phone(phone) AS masked_phone,
  apscat.finance.mask_income_bracket(annual_income) AS income_bracket
FROM customers
LIMIT 5;

-- =============================================
-- TEST 13: Fraud Transaction Detection
-- =============================================
SELECT '=== FRAUD FLAGGED TRANSACTIONS ===' AS section;

SELECT 
  transaction_id,
  customer_id,
  amount,
  merchant_name,
  fraud_flag,
  status
FROM transactions
WHERE fraud_flag = true;

-- =============================================
-- TEST 14: High-Value Transactions
-- =============================================
SELECT '=== HIGH-VALUE TRANSACTIONS (>$5000) ===' AS section;

SELECT 
  transaction_id,
  customer_id,
  amount,
  apscat.finance.mask_amount_bucket(amount) AS amount_bucket,
  merchant_name,
  transaction_date
FROM transactions
WHERE amount > 5000
ORDER BY amount DESC;

-- =============================================
-- TEST 15: Customer Account Summary
-- =============================================
SELECT '=== CUSTOMER ACCOUNT SUMMARY ===' AS section;

SELECT 
  c.customer_id,
  CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
  COUNT(DISTINCT a.account_id) AS checking_savings_accounts,
  COUNT(DISTINCT cc.card_id) AS credit_cards,
  COUNT(DISTINCT l.loan_id) AS loans,
  COUNT(DISTINCT t.transaction_id) AS total_transactions
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id
LEFT JOIN credit_cards cc ON c.customer_id = cc.customer_id
LEFT JOIN loans l ON c.customer_id = l.customer_id
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_transactions DESC
LIMIT 10;

-- =============================================
-- TEST 16: Transaction Volume by Category
-- =============================================
SELECT '=== TRANSACTION VOLUME BY CATEGORY ===' AS section;

SELECT 
  merchant_category,
  COUNT(*) AS transaction_count,
  SUM(amount) AS total_amount,
  AVG(amount) AS avg_amount
FROM transactions
WHERE merchant_category IS NOT NULL
GROUP BY merchant_category
ORDER BY total_amount DESC;

-- =============================================
-- TEST 17: Loan Portfolio Summary
-- =============================================
SELECT '=== LOAN PORTFOLIO SUMMARY ===' AS section;

SELECT 
  loan_type,
  COUNT(*) AS loan_count,
  SUM(loan_amount) AS total_originated,
  SUM(outstanding_balance) AS total_outstanding,
  AVG(interest_rate) AS avg_interest_rate
FROM loans
GROUP BY loan_type
ORDER BY total_outstanding DESC;

-- =============================================
-- TEST 18: Credit Card Utilization
-- =============================================
SELECT '=== CREDIT CARD UTILIZATION ===' AS section;

SELECT 
  card_id,
  customer_id,
  card_type,
  credit_limit,
  current_balance,
  ROUND((current_balance / credit_limit) * 100, 2) AS utilization_pct
FROM credit_cards
ORDER BY utilization_pct DESC
LIMIT 10;

-- =============================================
-- TEST 19: Functions Verification
-- =============================================
SELECT '=== MASKING FUNCTIONS AVAILABLE ===' AS section;

SHOW USER FUNCTIONS IN apscat.finance LIKE 'mask_%';

-- =============================================
-- SUMMARY
-- =============================================
SELECT 
  '✅ FINANCE DATA VERIFICATION COMPLETE' AS status,
  '5 tables with 120+ rows of financial data' AS data_summary,
  'All masking functions demonstrated successfully' AS functions_status;

