-- TELCO TESTS
USE CATALOG apscat; USE SCHEMA telco;
SELECT '=== TABLES ===' AS sec;
SELECT 'subscribers' AS tbl, COUNT(*) FROM subscribers UNION ALL SELECT 'call_records', COUNT(*) FROM call_records;
SELECT '=== PHONE MASKING ===' AS sec;
SELECT phone_number AS orig, apscat.telco.mask_phone_number(phone_number) AS masked FROM subscribers;
SELECT '=== USAGE BUCKETING ===' AS sec;
SELECT data_gb AS orig, apscat.telco.mask_usage_bucket(data_gb) AS bucket FROM data_usage;
SELECT '✅ Telco tests complete!' AS status;
