-- =============================================
-- MANUFACTURING ABAC POLICIES - COMPREHENSIVE TEST SCRIPT
-- =============================================
-- Purpose: Verify ABAC policies work correctly for different user groups
-- Expected behavior:
--   - 'users' group → See MASKED data (partial masking, bucketing, rounding)
--   - 'admins' group → See FULL unmasked data
-- 
-- HOW TO TEST:
-- 1. Run this script as a regular user (in 'users' group) → see masked data
-- 2. Run as admin (in 'admins' group) → see full data
-- 3. Compare outputs to verify masking is working
-- =============================================

USE CATALOG apscat;
USE SCHEMA manufacturing;

-- =============================================
-- TEST 1: Email Masking (PII Protection)
-- =============================================
-- Expected:
--   Users: m***@plantA.com (local part masked)
--   Admins: mike.a@plantA.com (full email)
SELECT 
  'TEST 1: Email Masking' AS test_name,
  event_id,
  technician_name,
  technician_email,  -- Tagged with 'ip_sensitivity' = 'Internal'
  event_type
FROM maintenance_events
WHERE event_id IN ('ME-1000', 'ME-1001', 'ME-1002')
ORDER BY event_id
LIMIT 5;

-- =============================================
-- TEST 2: Phone Number Masking (PII Protection)
-- =============================================
-- Expected:
--   Users: XXX-XXX-1001 (area/exchange masked)
--   Admins: 555-1001 (full phone)
SELECT 
  'TEST 2: Phone Masking' AS test_name,
  employee_id,
  full_name,
  phone,  -- Tagged with 'ip_sensitivity' = 'Internal'
  department,
  role
FROM employee_contacts
WHERE employee_id IN ('EMP-1001', 'EMP-1002', 'EMP-1003', 'EMP-1004', 'EMP-1005')
ORDER BY employee_id
LIMIT 5;

-- =============================================
-- TEST 3: Sensitive IP - Spec Text Masking
-- =============================================
-- Expected:
--   Users: "[REDACTED - Proprietary IP]"
--   Admins: Full spec text (e.g., "Proprietary aluminum alloy casting...")
SELECT 
  'TEST 3: IP Protection - Spec Text' AS test_name,
  spec_id,
  product_name,
  spec_text,  -- Tagged with 'ip_sensitivity' = 'Trade_Secret'
  tolerance
FROM product_specs
WHERE spec_id IN ('SPEC-001', 'SPEC-002', 'SPEC-003', 'SPEC-004', 'SPEC-005')
ORDER BY spec_id
LIMIT 5;

-- =============================================
-- TEST 4: Sensitive IP - CAD URI Hashing
-- =============================================
-- Expected:
--   Users: Hash like "sha256:a1b2c3d4..." (hashed URI)
--   Admins: Full URI "s3://cad/widget-alpha-v1.2.dwg"
SELECT 
  'TEST 4: IP Protection - CAD URI' AS test_name,
  spec_id,
  product_name,
  cad_file_uri,  -- Tagged with 'ip_sensitivity' = 'Trade_Secret'
  spec_version
FROM product_specs
WHERE spec_id IN ('SPEC-001', 'SPEC-006', 'SPEC-007', 'SPEC-008', 'SPEC-009')
ORDER BY spec_id
LIMIT 5;

-- =============================================
-- TEST 5: Cost Bucketing (Commercial Sensitivity)
-- =============================================
-- Expected:
--   Users: "$100-$500", "$0-$100" (cost ranges)
--   Admins: 125.50, 85.00 (exact amounts)
SELECT 
  'TEST 5: Cost Bucketing' AS test_name,
  event_id,
  event_type,
  cost,  -- Tagged with 'data_purpose' = 'SupplyChain'
  parts_used,
  hours_spent
FROM maintenance_events
WHERE cost > 0
ORDER BY cost DESC
LIMIT 10;

-- =============================================
-- TEST 6: Freight Cost Bucketing
-- =============================================
-- Expected:
--   Users: "$100-$250" (range)
--   Admins: 125.00, 185.00 (exact)
SELECT 
  'TEST 6: Freight Cost Protection' AS test_name,
  shipment_id,
  destination_plant,
  freight_cost,  -- Tagged with 'data_purpose' = 'SupplyChain'
  total_value,    -- Also tagged 'data_purpose' = 'SupplyChain'
  carrier,
  status
FROM shipments
WHERE shipment_id IN ('SHIP-5000', 'SHIP-5001', 'SHIP-5002', 'SHIP-5003', 'SHIP-5004')
ORDER BY shipment_id
LIMIT 5;

-- =============================================
-- TEST 7: Timestamp Rounding (Telemetry Precision)
-- =============================================
-- Expected:
--   Users: Rounded to 15-minute intervals (e.g., 08:00:00, 08:15:00)
--   Admins: Exact timestamps (e.g., 08:03:27, 08:17:42)
SELECT 
  'TEST 7: Timestamp Rounding' AS test_name,
  event_id,
  start_time,  -- Tagged with 'asset_criticality' = 'High'
  end_time,    -- Tagged with 'asset_criticality' = 'High'
  hours_spent,
  event_type
FROM maintenance_events
WHERE event_id IN ('ME-1000', 'ME-1004', 'ME-1011', 'ME-1016', 'ME-1021')
ORDER BY start_time
LIMIT 5;

-- =============================================
-- TEST 8: Supplier ID Hashing (Commercial Protection)
-- =============================================
-- Expected:
--   Users: Hashed supplier ID (e.g., "sha256:abc123...")
--   Admins: Real supplier ID (e.g., "SUP-10", "SUP-11")
SELECT 
  'TEST 8: Supplier Privacy' AS test_name,
  shipment_id,
  supplier_id,  -- Tagged with 'data_purpose' = 'Audit'
  destination_plant,
  total_value,
  ship_date
FROM shipments
WHERE shipment_id IN ('SHIP-5000', 'SHIP-5005', 'SHIP-5010', 'SHIP-5015', 'SHIP-5020')
ORDER BY ship_date
LIMIT 5;

-- =============================================
-- TEST 9: Tracking Number Masking (Last 4 Digits)
-- =============================================
-- Expected:
--   Users: ****0001 (last 4 only)
--   Admins: TRK-100001 (full tracking)
SELECT 
  'TEST 9: Tracking Number Masking' AS test_name,
  shipment_id,
  tracking_number,  -- Tagged with 'asset_criticality' = 'Medium'
  carrier,
  ship_date,
  status
FROM shipments
WHERE shipment_id IN ('SHIP-5000', 'SHIP-5001', 'SHIP-5002', 'SHIP-5003', 'SHIP-5004')
ORDER BY shipment_id
LIMIT 5;

-- =============================================
-- TEST 10: Multiple Masking on Same Row
-- =============================================
-- Expected: Multiple fields masked simultaneously
--   Users: Emails masked + phones masked + costs bucketed
--   Admins: All fields visible
SELECT 
  'TEST 10: Multi-Field Masking' AS test_name,
  event_id,
  technician_name,
  technician_email,   -- Masked
  technician_phone,   -- Masked
  cost,              -- Bucketed
  start_time,        -- Rounded
  event_type
FROM maintenance_events
WHERE event_id IN ('ME-1000', 'ME-1002', 'ME-1004', 'ME-1006', 'ME-1011')
ORDER BY event_id;

-- =============================================
-- TEST 11: Row Count Verification
-- =============================================
-- Expected: Same row counts for both users and admins (no row filtering)
SELECT 
  'TEST 11: Row Counts (No Filtering)' AS test_name,
  'maintenance_events' AS table_name, 
  COUNT(*) AS row_count 
FROM maintenance_events
UNION ALL
SELECT 
  'TEST 11: Row Counts (No Filtering)',
  'product_specs', 
  COUNT(*) 
FROM product_specs
UNION ALL
SELECT 
  'TEST 11: Row Counts (No Filtering)',
  'shipments', 
  COUNT(*) 
FROM shipments
UNION ALL
SELECT 
  'TEST 11: Row Counts (No Filtering)',
  'employee_contacts', 
  COUNT(*) 
FROM employee_contacts
UNION ALL
SELECT 
  'TEST 11: Row Counts (No Filtering)',
  'performance_metrics', 
  COUNT(*) 
FROM performance_metrics;

-- =============================================
-- TEST 12: Aggregations on Masked Data
-- =============================================
-- Expected: Aggregations work on masked data (though results may differ)
SELECT 
  'TEST 12: Aggregations' AS test_name,
  department,
  COUNT(*) AS employee_count,
  COUNT(DISTINCT role) AS unique_roles
FROM employee_contacts
GROUP BY department
ORDER BY employee_count DESC;

-- =============================================
-- TEST 13: Performance Metrics with Multiple Tags
-- =============================================
-- Expected: Maintenance costs bucketed, energy_kwh visible
SELECT 
  'TEST 13: Performance Metrics' AS test_name,
  metric_id,
  asset_id,
  metric_date,
  efficiency_percent,
  maintenance_cost,  -- Tagged 'data_purpose' = 'SupplyChain' → bucketed
  energy_kwh,        -- Tagged 'asset_criticality' = 'High' → visible
  output_units
FROM performance_metrics
WHERE metric_id IN ('PM-3000', 'PM-3003', 'PM-3011', 'PM-3012', 'PM-3021')
ORDER BY metric_date;

-- =============================================
-- TEST 14: Verify Policies are Active
-- =============================================
SELECT 
  'TEST 14: Active Policies' AS test_name,
  COUNT(*) AS policy_count
FROM (
  SHOW POLICIES ON SCHEMA apscat.manufacturing
);

-- =============================================
-- TEST 15: Assets Table (Original) with Tags
-- =============================================
-- Expected:
--   Users: asset_id masked, spec_text redacted, cad_uri hashed
--   Admins: All visible
SELECT 
  'TEST 15: Assets Table' AS test_name,
  asset_id,        -- Tagged 'asset_criticality' = 'High'
  asset_name,
  asset_type,
  site_region,
  spec_text,       -- Tagged 'ip_sensitivity' = 'Trade_Secret'
  cad_uri          -- Tagged 'ip_sensitivity' = 'Trade_Secret'
FROM assets
LIMIT 3;

-- =============================================
-- SUMMARY
-- =============================================
SELECT 
  '✅ ABAC TEST COMPLETE' AS status,
  'Compare results when run as different users' AS instruction,
  'users group = masked data | admins group = full data' AS expected_behavior;

