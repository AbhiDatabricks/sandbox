-- =============================================
-- APPLY ABAC TAGS TO FINANCE TABLES
-- =============================================

USE CATALOG apscat;
USE SCHEMA finance;

-- =============================================
-- TAGS FOR: customers (PII data)
-- =============================================
ALTER TABLE customers ALTER COLUMN ssn SET TAGS ('pii_level' = 'High', 'pci_compliance' = 'Not_Required');
ALTER TABLE customers ALTER COLUMN email SET TAGS ('pii_level' = 'Medium');
ALTER TABLE customers ALTER COLUMN phone SET TAGS ('pii_level' = 'Medium');
ALTER TABLE customers ALTER COLUMN address SET TAGS ('pii_level' = 'High');
ALTER TABLE customers ALTER COLUMN annual_income SET TAGS ('data_classification' = 'Confidential');

-- =============================================
-- TAGS FOR: accounts (Account numbers)
-- =============================================
ALTER TABLE accounts ALTER COLUMN account_number SET TAGS ('pii_level' = 'High', 'data_classification' = 'Confidential');
ALTER TABLE accounts ALTER COLUMN routing_number SET TAGS ('pii_level' = 'Medium', 'data_classification' = 'Confidential');

-- =============================================
-- TAGS FOR: credit_cards (PCI-DSS data)
-- =============================================
ALTER TABLE credit_cards ALTER COLUMN card_number SET TAGS ('pii_level' = 'High', 'pci_compliance' = 'Required');

-- =============================================
-- TAGS FOR: transactions (Transaction data)
-- =============================================
ALTER TABLE transactions ALTER COLUMN ip_address SET TAGS ('pii_level' = 'Medium');
ALTER TABLE transactions ALTER COLUMN amount SET TAGS ('data_classification' = 'Confidential');

SELECT '✅ Tags applied successfully to finance tables!' AS status;

