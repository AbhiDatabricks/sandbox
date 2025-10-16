-- GOVERNMENT TESTS
USE CATALOG apscat; USE SCHEMA government;
SELECT '=== TABLES ===' AS sec;
SELECT 'citizens' AS tbl, COUNT(*) FROM citizens UNION ALL SELECT 'tax_records', COUNT(*) FROM tax_records;
SELECT '=== SSN MASKING ===' AS sec;
SELECT ssn AS orig, apscat.government.mask_ssn_last4(ssn) AS masked FROM citizens;
SELECT '=== TAX BUCKETING ===' AS sec;
SELECT tax_owed AS orig, apscat.government.mask_tax_amount_bucket(tax_owed) AS bucket FROM tax_records;
SELECT '✅ Government tests complete!' AS status;
