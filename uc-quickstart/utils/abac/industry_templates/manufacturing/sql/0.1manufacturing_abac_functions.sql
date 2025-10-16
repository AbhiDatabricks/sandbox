-- =============================================
-- DATABRICKS UNITY CATALOG ABAC FUNCTIONS (Manufacturing)
-- Purpose: Attribute-Based Access Control (ABAC) utility functions
-- Domain: Manufacturing (operations, maintenance, quality, supply chain)
-- Usage: Replace <<your_catalog_name>> with your actual catalog name
-- =============================================

-- CONFIGURATION
-- REQUIRED: Replace <<your_catalog_name>> with your actual catalog name (e.g., 'apscat', 'main')
USE CATALOG apscat;
USE SCHEMA manufacturing;

-- =============================================
-- MASKING FUNCTIONS
-- =============================================

-- 1) Partial string masking (e.g., names)
CREATE OR REPLACE FUNCTION mask_string_partial(input STRING)
RETURNS STRING
COMMENT 'ABAC utility: Partial string masking showing first and last characters'
RETURN CASE 
  WHEN input IS NULL OR input = '' THEN input
  WHEN LENGTH(input) <= 2 THEN REPEAT('*', LENGTH(input))
  WHEN LENGTH(input) = 3 THEN CONCAT(LEFT(input, 1), '*', RIGHT(input, 1))
  ELSE CONCAT(LEFT(input, 1), REPEAT('*', LENGTH(input) - 2), RIGHT(input, 1))
END;

-- 2) Email masking (preserve domain)
CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask email local part while preserving domain'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN LOCATE('@', email) > 0 THEN CONCAT('****', SUBSTRING(email, LOCATE('@', email)))
  ELSE '****'
END;

-- 3) Phone masking (preserve last 4)
CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask phone number leaving last 4 visible'
RETURN CASE 
  WHEN phone IS NULL OR phone = '' THEN phone
  WHEN LENGTH(phone) >= 4 THEN CONCAT(REPEAT('X', LENGTH(phone) - 4), RIGHT(phone, 4))
  ELSE REPEAT('X', LENGTH(phone))
END;

-- 4) One-way hash for strings (referential but anonymized)
CREATE OR REPLACE FUNCTION mask_string_hash(input STRING)
RETURNS STRING
COMMENT 'ABAC utility: One-way SHA-256 hash for anonymization'
RETURN sha2(input, 256);

-- 5) Deterministic referential masking for IDs (string)
CREATE OR REPLACE FUNCTION mask_id_referential(input STRING)
RETURNS STRING
COMMENT 'ABAC utility: Deterministic masking for string identifiers to preserve joins'
RETURN sha2(coalesce(input, ''), 256);

-- 6) Deterministic referential masking for numeric IDs
CREATE OR REPLACE FUNCTION fast_deterministic_multiplier(id DECIMAL)
RETURNS DECIMAL
COMMENT 'ABAC utility: Deterministic multiplier helper (1.001..2.000)'
RETURN 1 + MOD(CRC32(CAST(CAST(id AS STRING) AS BINARY)), 1000) * 0.001;

CREATE OR REPLACE FUNCTION mask_decimal_referential(id DECIMAL)
RETURNS DECIMAL
COMMENT 'ABAC utility: Deterministically mask numeric IDs while preserving referential integrity'
RETURN id * fast_deterministic_multiplier(id);

-- 7) Redact sensitive specification text
CREATE OR REPLACE FUNCTION mask_spec_text(input STRING)
RETURNS STRING
COMMENT 'ABAC utility: Redact sensitive specification text'
RETURN CASE WHEN input IS NULL THEN NULL ELSE 'REDACTED_SPEC' END;

-- 8) Redact or hash CAD file references
CREATE OR REPLACE FUNCTION mask_cad_reference(uri STRING)
RETURNS STRING
COMMENT 'ABAC utility: Hash CAD/PLM file references for non-authorized roles'
RETURN CASE WHEN uri IS NULL THEN NULL ELSE sha2(uri, 256) END;

-- 9) Cost bucketing
CREATE OR REPLACE FUNCTION mask_cost_bucket(amount DECIMAL(18,2))
RETURNS STRING
COMMENT 'ABAC utility: Bucketize costs into Low/Medium/High'
RETURN CASE 
  WHEN amount IS NULL THEN NULL
  WHEN amount < 100 THEN 'Low'
  WHEN amount < 1000 THEN 'Medium'
  ELSE 'High'
END;

-- 10) Serial last-4 display
CREATE OR REPLACE FUNCTION mask_serial_last4(serial STRING)
RETURNS STRING
COMMENT 'ABAC utility: Show only last 4 characters of serial'
RETURN CASE 
  WHEN serial IS NULL OR serial = '' THEN serial
  WHEN LENGTH(serial) >= 4 THEN CONCAT(REPEAT('X', GREATEST(LENGTH(serial) - 4, 0)), RIGHT(serial, 4))
  ELSE REPEAT('X', LENGTH(serial))
END;

-- 11) GPS precision reduction (round to 2 decimals)
CREATE OR REPLACE FUNCTION mask_gps_precision(lat DOUBLE, lon DOUBLE)
RETURNS STRING
COMMENT 'ABAC utility: Reduce GPS precision by rounding to 2 decimals'
RETURN CONCAT(CAST(ROUND(lat, 2) AS STRING), ',', CAST(ROUND(lon, 2) AS STRING));

-- 12) Timestamp rounding to 15-minute bins
CREATE OR REPLACE FUNCTION mask_timestamp_15min(ts TIMESTAMP)
RETURNS TIMESTAMP
COMMENT 'ABAC utility: Floor timestamp to 15-minute intervals'
RETURN to_timestamp((unix_timestamp(ts) - (unix_timestamp(ts) % 900)));

-- =============================================
-- ROW FILTER FUNCTIONS
-- =============================================

-- A) Business hours filter (8AM - 6PM Chicago time)
CREATE OR REPLACE FUNCTION business_hours_filter()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours (8AM-6PM America/Chicago)'
RETURN hour(from_utc_timestamp(current_timestamp(), 'America/Chicago')) BETWEEN 8 AND 18;

-- B) Maintenance night-shift window (10PM-6AM Chicago time)
CREATE OR REPLACE FUNCTION maintenance_hours_filter()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access during maintenance window (22:00-06:00 America/Chicago)'
RETURN (
  hour(from_utc_timestamp(current_timestamp(), 'America/Chicago')) >= 22
  OR hour(from_utc_timestamp(current_timestamp(), 'America/Chicago')) < 6
);

-- C) Hard deny (no rows)
CREATE OR REPLACE FUNCTION no_rows()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Returns FALSE to deny all rows'
RETURN FALSE;

-- D) Placeholder filters for tag-driven scenarios (return TRUE; policy tags/grouproles drive binding)
CREATE OR REPLACE FUNCTION sensitive_asset_filter()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Placeholder for sensitive asset contexts (policy-driven)'
RETURN TRUE;

CREATE OR REPLACE FUNCTION quality_nc_only()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Placeholder to expose only non-conformance contexts (policy-driven)'
RETURN TRUE;

-- =============================================
-- FUNCTION INVENTORY
-- =============================================
-- SHOW USER FUNCTIONS;  -- uncomment to list functions after execution


