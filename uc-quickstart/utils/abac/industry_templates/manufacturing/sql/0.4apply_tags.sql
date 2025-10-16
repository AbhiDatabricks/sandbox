-- =============================================
-- APPLY ABAC TAGS TO MANUFACTURING TABLES
-- =============================================

USE CATALOG apscat;
USE SCHEMA manufacturing;

-- =============================================
-- TAGS FOR: maintenance_events (PII + Cost data)
-- =============================================
ALTER TABLE maintenance_events
  ALTER COLUMN technician_email SET TAGS ('ip_sensitivity' = 'Internal');

ALTER TABLE maintenance_events
  ALTER COLUMN technician_phone SET TAGS ('ip_sensitivity' = 'Internal');

ALTER TABLE maintenance_events
  ALTER COLUMN cost SET TAGS ('data_purpose' = 'SupplyChain');

ALTER TABLE maintenance_events
  ALTER COLUMN start_time SET TAGS ('asset_criticality' = 'High');

ALTER TABLE maintenance_events
  ALTER COLUMN end_time SET TAGS ('asset_criticality' = 'High');

-- =============================================
-- TAGS FOR: product_specs (Sensitive IP)
-- =============================================
ALTER TABLE product_specs
  ALTER COLUMN spec_text SET TAGS ('ip_sensitivity' = 'Trade_Secret');

ALTER TABLE product_specs
  ALTER COLUMN cad_file_uri SET TAGS ('ip_sensitivity' = 'Trade_Secret');

ALTER TABLE product_specs
  ALTER COLUMN material_composition SET TAGS ('ip_sensitivity' = 'Internal');

ALTER TABLE product_specs
  ALTER COLUMN created_by SET TAGS ('ip_sensitivity' = 'Internal');

-- =============================================
-- TAGS FOR: shipments (Cost + Supplier data)
-- =============================================
ALTER TABLE shipments
  ALTER COLUMN freight_cost SET TAGS ('data_purpose' = 'SupplyChain');

ALTER TABLE shipments
  ALTER COLUMN total_value SET TAGS ('data_purpose' = 'SupplyChain');

ALTER TABLE shipments
  ALTER COLUMN supplier_id SET TAGS ('data_purpose' = 'Audit');

ALTER TABLE shipments
  ALTER COLUMN tracking_number SET TAGS ('asset_criticality' = 'Medium');

-- =============================================
-- TAGS FOR: employee_contacts (PII)
-- =============================================
ALTER TABLE employee_contacts
  ALTER COLUMN email SET TAGS ('ip_sensitivity' = 'Internal');

ALTER TABLE employee_contacts
  ALTER COLUMN phone SET TAGS ('ip_sensitivity' = 'Internal');

ALTER TABLE employee_contacts
  ALTER COLUMN full_name SET TAGS ('data_purpose' = 'SupplyChain');

-- =============================================
-- TAGS FOR: performance_metrics (Operational data)
-- =============================================
ALTER TABLE performance_metrics
  ALTER COLUMN maintenance_cost SET TAGS ('data_purpose' = 'SupplyChain');

ALTER TABLE performance_metrics
  ALTER COLUMN energy_kwh SET TAGS ('asset_criticality' = 'High');

ALTER TABLE performance_metrics
  ALTER COLUMN metric_date SET TAGS ('shift_hours' = 'Day');

-- =============================================
-- TAGS FOR: assets (from original schema)
-- =============================================
ALTER TABLE assets
  ALTER COLUMN asset_id SET TAGS ('asset_criticality' = 'High');

ALTER TABLE assets
  ALTER COLUMN spec_text SET TAGS ('ip_sensitivity' = 'Trade_Secret');

ALTER TABLE assets
  ALTER COLUMN cad_uri SET TAGS ('ip_sensitivity' = 'Trade_Secret');

-- =============================================
-- VERIFICATION: Show all tags
-- =============================================
SELECT 
  'Tags applied successfully! Policies can now bind to tagged columns.' AS status;

-- Show sample tagged columns
DESCRIBE TABLE EXTENDED maintenance_events;
DESCRIBE TABLE EXTENDED product_specs;
DESCRIBE TABLE EXTENDED shipments;
DESCRIBE TABLE EXTENDED employee_contacts;
DESCRIBE TABLE EXTENDED performance_metrics;

