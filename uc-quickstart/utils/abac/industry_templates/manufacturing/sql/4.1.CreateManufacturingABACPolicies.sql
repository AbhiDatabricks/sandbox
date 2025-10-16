-- Databricks notebook source
-- MAGIC %md
-- MAGIC # 🔐 Manufacturing ABAC Policies - Catalog Level

-- Set catalog context
USE CATALOG users;
USE SCHEMA abhishekpratap_singh;

-- Verify functions exist
SHOW FUNCTIONS IN users.abhishekpratap_singh LIKE 'mask_*';
SHOW FUNCTIONS IN users.abhishekpratap_singh LIKE '%filter%';

SELECT "Ready to create manufacturing ABAC policies" AS status;

-- =============================================
-- POLICY 1: IP protection for specs/CAD (mask for most roles)
CREATE OR REPLACE POLICY users_mfg_ip_protection_specs
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Mask spec_text and CAD refs for IP sensitivity; unmask only for RnD_Scientist and Site_Lead'
COLUMN MASK users.abhishekpratap_singh.mask_spec_text
TO `Plant_Operator`, `Quality_Engineer`, `Maintenance_Tech`, `Supply_Chain_Manager`, `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Trade_Secret') OR hasTagValue('ip_sensitivity','Internal') AS ip_cols
ON COLUMN ip_cols;

CREATE OR REPLACE POLICY users_mfg_ip_protection_cad
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Hash CAD references for non-authorized roles'
COLUMN MASK users.abhishekpratap_singh.mask_cad_reference
TO `Plant_Operator`, `Quality_Engineer`, `Maintenance_Tech`, `Supply_Chain_Manager`, `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Trade_Secret') OR hasTagValue('ip_sensitivity','Internal') AS cad_cols
ON COLUMN cad_cols;

-- =============================================
-- POLICY 2: Site/region sovereignty (row filter by residency)
CREATE OR REPLACE POLICY users_mfg_site_region_residency
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Enforce site/region residency requirements on manufacturing data'
ROW FILTER users.abhishekpratap_singh.sensitive_asset_filter
TO `Plant_Operator`, `Quality_Engineer`, `Maintenance_Tech`, `Supply_Chain_Manager`
FOR TABLES
WHEN hasTagValue('data_residency','Country_Only') OR hasTagValue('data_residency','EU_Only');

-- =============================================
-- POLICY 3: Maintenance windows (night-shift filter)
CREATE OR REPLACE POLICY users_mfg_maintenance_window
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Restrict high-granularity telemetry to maintenance windows for Maintenance_Tech'
ROW FILTER users.abhishekpratap_singh.maintenance_hours_filter
TO `Maintenance_Tech`
FOR TABLES
WHEN hasTagValue('shift_hours','Night') OR hasTagValue('shift_hours','Emergency_24x7');

-- =============================================
-- POLICY 4: Export control gate
CREATE OR REPLACE POLICY users_mfg_export_control
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Restrict ITAR/EAR data exposure for non-authorized personas'
ROW FILTER users.abhishekpratap_singh.no_rows
TO `Plant_Operator`, `Quality_Engineer`, `Maintenance_Tech`, `Supply_Chain_Manager`, `Supplier_Auditor`
FOR TABLES
WHEN hasTagValue('export_control','ITAR') OR hasTagValue('export_control','EAR99');

-- =============================================
-- POLICY 5: Critical asset data minimization
CREATE OR REPLACE POLICY users_mfg_critical_assets_serial
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Mask asset serials for non-lead roles on High criticality'
COLUMN MASK users.abhishekpratap_singh.mask_serial_last4
TO `Plant_Operator`, `Quality_Engineer`, `Supply_Chain_Manager`, `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('asset_criticality','High') AS serial_cols
ON COLUMN serial_cols;

CREATE OR REPLACE POLICY users_mfg_critical_assets_gps
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Reduce GPS precision for non-lead roles on High criticality'
COLUMN MASK users.abhishekpratap_singh.mask_gps_precision
TO `Plant_Operator`, `Quality_Engineer`, `Supply_Chain_Manager`, `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('asset_criticality','High') AS gps_cols
ON COLUMN gps_cols;

CREATE OR REPLACE POLICY users_mfg_critical_assets_time
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Round telemetry timestamps for non-ops roles on High criticality'
COLUMN MASK users.abhishekpratap_singh.mask_timestamp_15min
TO `Supply_Chain_Manager`, `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('asset_criticality','High') AS time_cols
ON COLUMN time_cols;

-- =============================================
-- POLICY 6: Supplier auditor least-privilege (temporary)
CREATE OR REPLACE POLICY users_mfg_supplier_auditor_cost
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Bucketize costs and anonymize suppliers for Supplier_Auditor during audits'
COLUMN MASK users.abhishekpratap_singh.mask_cost_bucket
TO `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose','Audit') AS cost_cols
ON COLUMN cost_cols;

CREATE OR REPLACE POLICY users_mfg_supplier_auditor_suppliername
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Hash supplier names for Supplier_Auditor'
COLUMN MASK users.abhishekpratap_singh.mask_string_hash
TO `Supplier_Auditor`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose','Audit') AS sup_cols
ON COLUMN sup_cols;

-- =============================================
-- POLICY 7: Quality non-conformance focused exposure
CREATE OR REPLACE POLICY users_mfg_quality_nc_only
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Quality Engineer focused access for non-conformance contexts'
ROW FILTER users.abhishekpratap_singh.quality_nc_only
TO `Quality_Engineer`
FOR TABLES
WHEN hasTagValue('data_purpose','Quality');

-- =============================================
-- POLICY 8: Deterministic analytics joins for operations
CREATE OR REPLACE POLICY users_mfg_ops_deterministic_ids
ON SCHEMA users.abhishekpratap_singh
COMMENT 'Deterministic masking of identifiers to preserve join capability for Operations analytics'
COLUMN MASK users.abhishekpratap_singh.mask_id_referential
TO `Plant_Operator`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose','Operations') AS id_cols
ON COLUMN id_cols;

-- Verify catalog-level policies
SHOW POLICIES ON SCHEMA users.abhishekpratap_singh;


