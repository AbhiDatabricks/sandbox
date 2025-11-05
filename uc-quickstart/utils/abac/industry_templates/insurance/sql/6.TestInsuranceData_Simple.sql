-- INSURANCE TESTS
USE CATALOG apscat; USE SCHEMA insurance;
SELECT '=== TABLES ===' AS sec;
SELECT 'policyholders' AS tbl, COUNT(*) FROM policyholders UNION ALL SELECT 'claims', COUNT(*) FROM claims;
SELECT '=== SSN MASKING ===' AS sec;
SELECT ssn AS orig, mask_ssn_last4(ssn) AS masked FROM policyholders;
SELECT '=== CLAIM BUCKETING ===' AS sec;
SELECT claim_amount AS orig, mask_claim_amount_bucket(claim_amount) AS bucket FROM claims;
SELECT '✅ Insurance tests complete!' AS status;
