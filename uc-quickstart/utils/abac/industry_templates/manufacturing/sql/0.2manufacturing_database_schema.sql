-- =============================================
-- MANUFACTURING DATABASE SCHEMA FOR DATABRICKS
-- Purpose: Demonstration with synthetic data for ABAC
-- Usage: Replace ${CATALOG_NAME} with your actual catalog
-- =============================================

-- CONFIGURATION
-- REQUIRED: Replace ${CATALOG_NAME} with your actual catalog name
USE CATALOG apscat;
USE SCHEMA manufacturing;

-- =============================================
-- TABLE: assets (master data)
-- =============================================
DROP TABLE IF EXISTS assets;
CREATE TABLE assets (
  asset_id STRING NOT NULL,
  asset_name STRING NOT NULL,
  asset_type STRING NOT NULL,
  site_region STRING NOT NULL,
  asset_criticality STRING NOT NULL, -- High/Medium/Low
  export_control STRING,             -- ITAR/EAR99/Not_Controlled
  ip_sensitivity STRING,             -- Trade_Secret/Internal/Public
  install_date DATE,
  latitude DOUBLE,
  longitude DOUBLE,
  serial_number STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_assets PRIMARY KEY (asset_id)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Manufacturing assets across plants and regions';

INSERT INTO assets VALUES
('A-100', 'Conveyor-1', 'Conveyor', 'Plant_A', 'High',  'ITAR',   'Trade_Secret', '2020-01-05', 41.881, -87.623, 'SN-001-A', current_timestamp()),
('A-101', 'Furnace-2',  'Furnace',  'Plant_B', 'Medium','EAR99',  'Internal',     '2019-06-20', 34.052, -118.244,'SN-002-B', current_timestamp()),
('A-102', 'Robot-Arm',  'Robot',    'Plant_C', 'Low',   'Not_Controlled','Public','2021-04-11', 47.606, -122.332,'SN-003-C', current_timestamp());

-- =============================================
-- TABLE: sensors (telemetry)
-- =============================================
DROP TABLE IF EXISTS sensors;
CREATE TABLE sensors (
  sensor_id STRING NOT NULL,
  asset_id STRING NOT NULL,
  sensor_type STRING NOT NULL,
  unit STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_sensors PRIMARY KEY (sensor_id)
) USING DELTA
COMMENT 'Sensors mounted to assets';

INSERT INTO sensors VALUES
('S-500', 'A-100', 'temperature', 'C', current_timestamp()),
('S-501', 'A-100', 'vibration',   'mm/s', current_timestamp()),
('S-600', 'A-101', 'temperature', 'C', current_timestamp()),
('S-700', 'A-102', 'current',     'A', current_timestamp());

-- =============================================
-- TABLE: production_runs
-- =============================================
DROP TABLE IF EXISTS production_runs;
CREATE TABLE production_runs (
  run_id STRING NOT NULL,
  asset_id STRING NOT NULL,
  site_region STRING NOT NULL,
  shift_hours STRING NOT NULL,      -- Day/Swing/Night/Emergency_24x7
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  units_produced INT,
  scrap_units INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_runs PRIMARY KEY (run_id)
) USING DELTA
COMMENT 'Production runs by asset, site, and shift';

INSERT INTO production_runs VALUES
('R-900', 'A-100', 'Plant_A', 'Day',   timestamp('2024-03-01 08:00:00'), timestamp('2024-03-01 16:00:00'), 1000, 25, current_timestamp()),
('R-901', 'A-100', 'Plant_A', 'Night', timestamp('2024-03-01 22:00:00'), timestamp('2024-03-02 06:00:00'),  850, 30, current_timestamp()),
('R-902', 'A-101', 'Plant_B', 'Day',   timestamp('2024-03-02 08:00:00'), timestamp('2024-03-02 16:00:00'),  600, 18, current_timestamp());

-- =============================================
-- TABLE: work_orders (maintenance)
-- =============================================
DROP TABLE IF EXISTS work_orders;
CREATE TABLE work_orders (
  work_order_id STRING NOT NULL,
  asset_id STRING NOT NULL,
  description STRING,
  requested_by STRING,
  assigned_to STRING,
  status STRING,                    -- Open/InProgress/Closed
  scheduled_start TIMESTAMP,
  scheduled_end TIMESTAMP,
  actual_start TIMESTAMP,
  actual_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_work_orders PRIMARY KEY (work_order_id)
) USING DELTA
COMMENT 'Maintenance work orders with scheduling';

INSERT INTO work_orders VALUES
('WO-1000', 'A-100', 'Bearing replacement', 'op_jane@plantA', 'tech_mike@plantA', 'Closed', timestamp('2024-02-28 22:00:00'), timestamp('2024-02-28 23:00:00'), timestamp('2024-02-28 22:05:00'), timestamp('2024-02-28 22:50:00'), current_timestamp()),
('WO-1001', 'A-101', 'Thermocouple inspect', 'op_lee@plantB', 'tech_amy@plantB', 'Open', timestamp('2024-03-03 22:00:00'), timestamp('2024-03-03 23:00:00'), NULL, NULL, current_timestamp());

-- =============================================
-- TABLE: quality_inspections
-- =============================================
DROP TABLE IF EXISTS quality_inspections;
CREATE TABLE quality_inspections (
  inspection_id STRING NOT NULL,
  run_id STRING NOT NULL,
  defect_code STRING,
  severity STRING,                  -- Minor/Major/Critical
  disposition STRING,               -- Rework/Scrap/UseAsIs
  inspector STRING,
  notes STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_qi PRIMARY KEY (inspection_id)
) USING DELTA
COMMENT 'Quality inspections linked to production runs';

INSERT INTO quality_inspections VALUES
('QI-2000', 'R-900', 'D-01', 'Minor',    'Rework',  'qe_maria@plantA', 'Surface blemish', current_timestamp()),
('QI-2001', 'R-901', 'D-07', 'Critical', 'Scrap',   'qe_raj@plantA',   'Warping detected', current_timestamp());

-- =============================================
-- TABLE: suppliers
-- =============================================
DROP TABLE IF EXISTS suppliers;
CREATE TABLE suppliers (
  supplier_id STRING NOT NULL,
  supplier_name STRING,
  contact_email STRING,
  contact_phone STRING,
  site_region STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_suppliers PRIMARY KEY (supplier_id)
) USING DELTA
COMMENT 'Suppliers supporting plants';

INSERT INTO suppliers VALUES
('SUP-10', 'Acme Steel',     'sales@acme-steel.com',     '555-111-2222', 'AMER', current_timestamp()),
('SUP-11', 'Euro Bearings',  'orders@euro-bearings.eu',  '+49-555-2222', 'EMEA', current_timestamp());

-- =============================================
-- TABLE: bom (bill of materials)
-- =============================================
DROP TABLE IF EXISTS bom;
CREATE TABLE bom (
  bom_id STRING NOT NULL,
  asset_id STRING NOT NULL,
  supplier_id STRING NOT NULL,
  part_number STRING,
  unit_cost DECIMAL(18,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_bom PRIMARY KEY (bom_id)
) USING DELTA
COMMENT 'Bill of materials linking assets to supplier parts';

INSERT INTO bom VALUES
('BOM-3000', 'A-100', 'SUP-10', 'BRG-ACME-6204', 12.50, current_timestamp()),
('BOM-3001', 'A-101', 'SUP-11', 'TC-EB-100',      5.10, current_timestamp());

-- =============================================
-- VERIFICATION
-- =============================================
SHOW TABLES;

SELECT 'assets' AS table_name, COUNT(*) AS row_count FROM assets
UNION ALL SELECT 'sensors', COUNT(*) FROM sensors
UNION ALL SELECT 'production_runs', COUNT(*) FROM production_runs
UNION ALL SELECT 'work_orders', COUNT(*) FROM work_orders
UNION ALL SELECT 'quality_inspections', COUNT(*) FROM quality_inspections
UNION ALL SELECT 'suppliers', COUNT(*) FROM suppliers
UNION ALL SELECT 'bom', COUNT(*) FROM bom
ORDER BY table_name;


