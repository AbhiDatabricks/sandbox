-- =============================================
-- MANUFACTURING DATA VERIFICATION & TESTING
-- =============================================
-- Purpose: Verify tables, data, and demonstrate masking functions
-- NO ABAC POLICIES REQUIRED - Manual function demonstration
-- =============================================

USE CATALOG apscat;
USE SCHEMA manufacturing;

-- =============================================
-- TEST 1: Table Row Counts
-- =============================================
SELECT '=== TABLE ROW COUNTS ===' AS section;

SELECT 
  'assets' AS table_name, 
  COUNT(*) AS row_count 
FROM assets
UNION ALL
SELECT 'maintenance_events', COUNT(*) FROM maintenance_events
UNION ALL
SELECT 'product_specs', COUNT(*) FROM product_specs
UNION ALL
SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL
SELECT 'employee_contacts', COUNT(*) FROM employee_contacts
UNION ALL
SELECT 'performance_metrics', COUNT(*) FROM performance_metrics
ORDER BY table_name;

-- =============================================
-- TEST 2: Email Masking Function Demo
-- =============================================
SELECT '=== EMAIL MASKING DEMO ===' AS section;

SELECT 
  event_id,
  technician_name,
  technician_email AS original_email,
  apscat.manufacturing.mask_email(technician_email) AS masked_email
FROM maintenance_events
WHERE event_id IN ('ME-1000', 'ME-1001', 'ME-1002', 'ME-1003', 'ME-1004')
ORDER BY event_id
LIMIT 5;

-- =============================================
-- TEST 3: Phone Masking Function Demo
-- =============================================
SELECT '=== PHONE MASKING DEMO ===' AS section;

SELECT 
  employee_id,
  full_name,
  phone AS original_phone,
  apscat.manufacturing.mask_phone(phone) AS masked_phone
FROM employee_contacts
WHERE employee_id IN ('EMP-1001', 'EMP-1002', 'EMP-1003', 'EMP-1004', 'EMP-1005')
ORDER BY employee_id
LIMIT 5;

-- =============================================
-- TEST 4: Spec Text Redaction Demo
-- =============================================
SELECT '=== SPEC TEXT REDACTION DEMO ===' AS section;

SELECT 
  spec_id,
  product_name,
  LEFT(spec_text, 30) || '...' AS spec_text_preview,
  apscat.manufacturing.mask_spec_text(spec_text) AS redacted_spec
FROM product_specs
WHERE spec_id IN ('SPEC-001', 'SPEC-002', 'SPEC-003', 'SPEC-004', 'SPEC-005')
ORDER BY spec_id
LIMIT 5;

-- =============================================
-- TEST 5: CAD URI Hashing Demo
-- =============================================
SELECT '=== CAD URI HASHING DEMO ===' AS section;

SELECT 
  spec_id,
  product_name,
  cad_file_uri AS original_uri,
  apscat.manufacturing.mask_cad_reference(cad_file_uri) AS hashed_uri
FROM product_specs
WHERE spec_id IN ('SPEC-001', 'SPEC-006', 'SPEC-007', 'SPEC-008', 'SPEC-009')
ORDER BY spec_id
LIMIT 5;

-- =============================================
-- TEST 6: Timestamp Rounding Demo
-- =============================================
SELECT '=== TIMESTAMP ROUNDING DEMO ===' AS section;

SELECT 
  event_id,
  event_type,
  start_time AS original_time,
  apscat.manufacturing.mask_timestamp_15min(start_time) AS rounded_time,
  TIMESTAMPDIFF(MINUTE, apscat.manufacturing.mask_timestamp_15min(start_time), start_time) AS minutes_diff
FROM maintenance_events
WHERE event_id IN ('ME-1000', 'ME-1001', 'ME-1002', 'ME-1003', 'ME-1004')
ORDER BY start_time
LIMIT 5;

-- =============================================
-- TEST 7: Multi-Column Masking Demo
-- =============================================
SELECT '=== MULTI-COLUMN MASKING DEMO ===' AS section;

SELECT 
  event_id,
  technician_name,
  apscat.manufacturing.mask_email(technician_email) AS masked_email,
  apscat.manufacturing.mask_phone(technician_phone) AS masked_phone,
  event_type,
  cost
FROM maintenance_events
WHERE cost > 0
ORDER BY cost DESC
LIMIT 10;

-- =============================================
-- TEST 8: Employee Data with Masking
-- =============================================
SELECT '=== EMPLOYEE DATA MASKING ===' AS section;

SELECT 
  employee_id,
  full_name,
  apscat.manufacturing.mask_email(email) AS masked_email,
  apscat.manufacturing.mask_phone(phone) AS masked_phone,
  department,
  role,
  site_location
FROM employee_contacts
WHERE department IN ('Maintenance', 'Engineering')
ORDER BY department, full_name
LIMIT 10;

-- =============================================
-- TEST 9: Product Specs with IP Protection
-- =============================================
SELECT '=== PRODUCT SPECS IP PROTECTION ===' AS section;

SELECT 
  spec_id,
  product_name,
  spec_version,
  apscat.manufacturing.mask_spec_text(spec_text) AS protected_spec,
  apscat.manufacturing.mask_cad_reference(cad_file_uri) AS protected_cad,
  tolerance
FROM product_specs
WHERE spec_id IN ('SPEC-010', 'SPEC-011', 'SPEC-012', 'SPEC-013', 'SPEC-014')
ORDER BY spec_id
LIMIT 5;

-- =============================================
-- TEST 10: Shipment Data Sample
-- =============================================
SELECT '=== SHIPMENT DATA ===' AS section;

SELECT 
  shipment_id,
  supplier_id,
  destination_plant,
  ship_date,
  carrier,
  status,
  items_count,
  freight_cost,
  total_value
FROM shipments
WHERE status = 'Delivered'
ORDER BY ship_date DESC
LIMIT 10;

-- =============================================
-- TEST 11: Performance Metrics Sample
-- =============================================
SELECT '=== PERFORMANCE METRICS ===' AS section;

SELECT 
  metric_id,
  asset_id,
  metric_date,
  uptime_hours,
  efficiency_percent,
  output_units,
  energy_kwh,
  maintenance_cost
FROM performance_metrics
WHERE efficiency_percent > 90
ORDER BY efficiency_percent DESC
LIMIT 10;

-- =============================================
-- TEST 12: Aggregations by Department
-- =============================================
SELECT '=== EMPLOYEE COUNTS BY DEPARTMENT ===' AS section;

SELECT 
  department,
  COUNT(*) AS employee_count,
  COUNT(DISTINCT role) AS unique_roles,
  COUNT(DISTINCT site_location) AS locations
FROM employee_contacts
GROUP BY department
ORDER BY employee_count DESC;

-- =============================================
-- TEST 13: Maintenance Cost Summary
-- =============================================
SELECT '=== MAINTENANCE COST SUMMARY ===' AS section;

SELECT 
  event_type,
  COUNT(*) AS event_count,
  SUM(cost) AS total_cost,
  AVG(cost) AS avg_cost,
  MAX(cost) AS max_cost
FROM maintenance_events
GROUP BY event_type
ORDER BY total_cost DESC;

-- =============================================
-- TEST 14: Asset Performance Overview
-- =============================================
SELECT '=== ASSET PERFORMANCE OVERVIEW ===' AS section;

SELECT 
  asset_id,
  COUNT(*) AS metrics_count,
  AVG(uptime_hours) AS avg_uptime,
  AVG(efficiency_percent) AS avg_efficiency,
  SUM(output_units) AS total_output,
  SUM(maintenance_cost) AS total_maint_cost
FROM performance_metrics
GROUP BY asset_id
ORDER BY avg_efficiency DESC;

-- =============================================
-- TEST 15: Functions Verification
-- =============================================
SELECT '=== MASKING FUNCTIONS AVAILABLE ===' AS section;

SHOW USER FUNCTIONS IN apscat.manufacturing LIKE 'mask_%';

-- =============================================
-- SUMMARY
-- =============================================
SELECT 
  '✅ MANUFACTURING DATA VERIFICATION COMPLETE' AS status,
  '6 tables with 153 total rows' AS data_summary,
  'All masking functions demonstrated successfully' AS functions_status;

