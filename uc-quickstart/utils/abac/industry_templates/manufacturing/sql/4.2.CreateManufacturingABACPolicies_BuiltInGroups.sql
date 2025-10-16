-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 🔐 Manufacturing ABAC Policies - Using Built-in Groups
-- MAGIC
-- MAGIC This version uses workspace built-in groups (users, admins) instead of custom groups
-- MAGIC
-- MAGIC ## Group Mapping:
-- MAGIC - `users` group = Regular workspace users (operators, engineers, analysts)
-- MAGIC - `admins` group = Workspace administrators (site leads, managers)

-- Set catalog context
USE CATALOG apscat;
USE SCHEMA manufacturing;

-- Verify functions exist
SHOW FUNCTIONS IN apscat.manufacturing LIKE 'mask_*';
SHOW FUNCTIONS IN apscat.manufacturing LIKE '%filter%';

SELECT "Ready to create manufacturing ABAC policies with built-in groups" AS status;

-- =============================================
-- POLICY 1: IP protection - Specs masked for regular users
-- =============================================
CREATE OR REPLACE POLICY mfg_ip_protection_specs
ON SCHEMA apscat.manufacturing
COMMENT 'Mask spec_text for regular users; admins see full data'
COLUMN MASK apscat.manufacturing.mask_spec_text
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Trade_Secret') OR hasTagValue('ip_sensitivity','Internal') AS ip_cols
ON COLUMN ip_cols;

-- =============================================
-- POLICY 2: CAD references hashed for regular users
-- =============================================
CREATE OR REPLACE POLICY mfg_ip_protection_cad
ON SCHEMA apscat.manufacturing
COMMENT 'Hash CAD references for regular users; admins see full URIs'
COLUMN MASK apscat.manufacturing.mask_cad_reference
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Trade_Secret') OR hasTagValue('ip_sensitivity','Internal') AS cad_cols
ON COLUMN cad_cols;

-- =============================================
-- POLICY 3: Serial numbers - last 4 only for regular users
-- =============================================
CREATE OR REPLACE POLICY mfg_serial_masking
ON SCHEMA apscat.manufacturing
COMMENT 'Show only last 4 of serial numbers to regular users'
COLUMN MASK apscat.manufacturing.mask_serial_last4
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('asset_criticality','High') OR hasTagValue('asset_criticality','Medium') AS serial_cols
ON COLUMN serial_cols;

-- =============================================
-- POLICY 4: GPS precision reduction for regular users
-- =============================================
CREATE OR REPLACE POLICY mfg_gps_precision
ON SCHEMA apscat.manufacturing
COMMENT 'Reduce GPS precision for regular users on critical assets'
COLUMN MASK apscat.manufacturing.mask_gps_precision
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('asset_criticality','High') AS gps_cols
ON COLUMN gps_cols;

-- =============================================
-- POLICY 5: Cost bucketing for regular users
-- =============================================
CREATE OR REPLACE POLICY mfg_cost_bucketing
ON SCHEMA apscat.manufacturing
COMMENT 'Show cost ranges instead of exact amounts to regular users'
COLUMN MASK apscat.manufacturing.mask_cost_bucket
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose','SupplyChain') OR hasTagValue('data_purpose','Audit') AS cost_cols
ON COLUMN cost_cols;

-- =============================================
-- POLICY 6: Supplier name hashing for privacy
-- =============================================
CREATE OR REPLACE POLICY mfg_supplier_privacy
ON SCHEMA apscat.manufacturing
COMMENT 'Hash supplier names for regular users to protect commercial relationships'
COLUMN MASK apscat.manufacturing.mask_string_hash
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose','Audit') AS supplier_cols
ON COLUMN supplier_cols;

-- =============================================
-- POLICY 7: Email masking
-- =============================================
CREATE OR REPLACE POLICY mfg_email_privacy
ON SCHEMA apscat.manufacturing
COMMENT 'Mask email addresses for regular users'
COLUMN MASK apscat.manufacturing.mask_email
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Internal') OR hasTagValue('data_purpose','SupplyChain') AS email_cols
ON COLUMN email_cols;

-- =============================================
-- POLICY 8: Phone number masking
-- =============================================
CREATE OR REPLACE POLICY mfg_phone_privacy
ON SCHEMA apscat.manufacturing
COMMENT 'Mask phone numbers for regular users'
COLUMN MASK apscat.manufacturing.mask_phone
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Internal') OR hasTagValue('data_purpose','SupplyChain') AS phone_cols
ON COLUMN phone_cols;

-- =============================================
-- POLICY 9: Timestamp rounding for regular users
-- =============================================
CREATE OR REPLACE POLICY mfg_timestamp_rounding
ON SCHEMA apscat.manufacturing
COMMENT 'Round telemetry timestamps to 15-min intervals for regular users'
COLUMN MASK apscat.manufacturing.mask_timestamp_15min
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('asset_criticality','High') AS timestamp_cols
ON COLUMN timestamp_cols;

-- =============================================
-- POLICY 10: Business hours access control
-- =============================================
CREATE OR REPLACE POLICY mfg_business_hours_access
ON SCHEMA apscat.manufacturing
COMMENT 'Restrict sensitive data access to business hours for regular users'
ROW FILTER apscat.manufacturing.business_hours_filter
TO `users`
FOR TABLES
WHEN hasTagValue('shift_hours','Day') OR hasTagValue('shift_hours','Standard_Business');

-- Verify policies created
SHOW POLICIES ON SCHEMA apscat.manufacturing;

SELECT "✅ Manufacturing ABAC policies created successfully with built-in groups!" AS status;

-- MAGIC %md
-- MAGIC ## 🎯 Policy Summary
-- MAGIC
-- MAGIC ### Column Masking Policies (9):
-- MAGIC 1. **IP protection** - Specs/CAD masked for users
-- MAGIC 2. **Serial numbers** - Last 4 only for users
-- MAGIC 3. **GPS precision** - Reduced for users
-- MAGIC 4. **Cost bucketing** - Ranges instead of exact amounts
-- MAGIC 5. **Supplier privacy** - Names hashed
-- MAGIC 6. **Email masking** - Local part hidden
-- MAGIC 7. **Phone masking** - Partial visibility
-- MAGIC 8. **Timestamp rounding** - 15-min intervals
-- MAGIC
-- MAGIC ### Row Filter Policies (1):
-- MAGIC 9. **Business hours** - Time-based access restriction
-- MAGIC
-- MAGIC ### Access Model:
-- MAGIC - **`users` group**: See masked/filtered data
-- MAGIC - **`admins` group**: See full unmasked data
-- MAGIC
-- MAGIC This demonstrates role-based ABAC without requiring custom group creation!

