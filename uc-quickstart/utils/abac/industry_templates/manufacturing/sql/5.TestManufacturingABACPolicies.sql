-- =============================================
-- TESTS: Manufacturing ABAC Policies Verification
-- =============================================

USE CATALOG users;
USE SCHEMA abhishekpratap_singh;

-- 1) Table existence and counts
SHOW TABLES;

SELECT 'assets' AS table_name, COUNT(*) AS row_count FROM assets
UNION ALL SELECT 'sensors', COUNT(*) FROM sensors
UNION ALL SELECT 'production_runs', COUNT(*) FROM production_runs
UNION ALL SELECT 'work_orders', COUNT(*) FROM work_orders
UNION ALL SELECT 'quality_inspections', COUNT(*) FROM quality_inspections
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'bom', COUNT(*) FROM bom
ORDER BY table_name;

-- 2) Join preservation via deterministic IDs (visual spot-check)
SELECT 
  a.asset_id,
  a.asset_name,
  pr.run_id,
  pr.units_produced
FROM assets a
JOIN production_runs pr ON a.asset_id = pr.asset_id
LIMIT 10;

-- 3) IP masking checks (spec_text/cad_uri when present) - placeholder columns if tagged
-- DESCRIBE TABLE assets; -- verify columns and tags

-- 4) Residency filter sanity (depends on tag bindings)
-- SELECT * FROM assets LIMIT 10;

-- 5) Supplier auditor masking (cost bucket and supplier name hash) - placeholder where applied
-- SELECT supplier_name, unit_cost FROM bom LIMIT 10;


