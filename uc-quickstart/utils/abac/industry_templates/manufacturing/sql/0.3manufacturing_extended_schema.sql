-- =============================================
-- EXTENDED MANUFACTURING TABLES (5 additional tables with 20+ rows each)
-- =============================================

USE CATALOG apscat;
USE SCHEMA manufacturing;

-- =============================================
-- TABLE 8: MAINTENANCE_EVENTS (25 rows)
-- =============================================
DROP TABLE IF EXISTS maintenance_events;
CREATE TABLE maintenance_events (
  event_id STRING NOT NULL,
  asset_id STRING NOT NULL,
  work_order_id STRING,
  event_type STRING NOT NULL,
  technician_name STRING,
  technician_email STRING,
  technician_phone STRING,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  hours_spent DECIMAL(5,2),
  parts_used STRING,
  notes STRING,
  cost DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_maintenance_events PRIMARY KEY (event_id)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Maintenance events and technician activities';

INSERT INTO maintenance_events VALUES
('ME-1000', 'A-100', 'WO-1000', 'Preventive', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-01 08:00:00'), timestamp('2024-03-01 10:00:00'), 2.0, 'Bearing-6204', 'Replaced worn bearing', 125.50, current_timestamp()),
('ME-1001', 'A-100', NULL, 'Inspection', 'Sarah Lee', 'sarah.l@plantA.com', '555-1002', timestamp('2024-03-02 09:00:00'), timestamp('2024-03-02 09:30:00'), 0.5, NULL, 'Visual inspection OK', 0.00, current_timestamp()),
('ME-1002', 'A-101', 'WO-1001', 'Corrective', 'Amy Chen', 'amy.c@plantB.com', '555-1003', timestamp('2024-03-03 14:00:00'), timestamp('2024-03-03 16:30:00'), 2.5, 'TC-EB-100', 'Replaced thermocouple', 85.00, current_timestamp()),
('ME-1003', 'A-102', NULL, 'Preventive', 'John Davis', 'john.d@plantC.com', '555-1004', timestamp('2024-03-04 10:00:00'), timestamp('2024-03-04 11:00:00'), 1.0, 'Lubricant-500ml', 'Lubrication service', 45.00, current_timestamp()),
('ME-1004', 'A-100', NULL, 'Emergency', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-05 22:00:00'), timestamp('2024-03-05 23:30:00'), 1.5, 'Relay-220V', 'Emergency relay replacement', 220.00, current_timestamp()),
('ME-1005', 'A-101', NULL, 'Inspection', 'Amy Chen', 'amy.c@plantB.com', '555-1003', timestamp('2024-03-06 08:00:00'), timestamp('2024-03-06 08:15:00'), 0.25, NULL, 'Pre-shift inspection', 0.00, current_timestamp()),
('ME-1006', 'A-102', NULL, 'Corrective', 'John Davis', 'john.d@plantC.com', '555-1004', timestamp('2024-03-07 13:00:00'), timestamp('2024-03-07 15:00:00'), 2.0, 'Motor-2HP', 'Motor replacement', 450.00, current_timestamp()),
('ME-1007', 'A-100', NULL, 'Preventive', 'Sarah Lee', 'sarah.l@plantA.com', '555-1002', timestamp('2024-03-08 09:00:00'), timestamp('2024-03-08 10:30:00'), 1.5, 'Filter-HEPA', 'Filter replacement', 95.00, current_timestamp()),
('ME-1008', 'A-101', NULL, 'Inspection', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-09 11:00:00'), timestamp('2024-03-09 11:20:00'), 0.33, NULL, 'Monthly safety check', 0.00, current_timestamp()),
('ME-1009', 'A-102', NULL, 'Preventive', 'Amy Chen', 'amy.c@plantB.com', '555-1003', timestamp('2024-03-10 10:00:00'), timestamp('2024-03-10 11:00:00'), 1.0, 'Belt-V-2000', 'Belt replacement', 78.00, current_timestamp()),
('ME-1010', 'A-100', NULL, 'Corrective', 'John Davis', 'john.d@plantC.com', '555-1004', timestamp('2024-03-11 15:00:00'), timestamp('2024-03-11 17:00:00'), 2.0, 'Sensor-Temp', 'Sensor calibration', 150.00, current_timestamp()),
('ME-1011', 'A-101', NULL, 'Emergency', 'Sarah Lee', 'sarah.l@plantA.com', '555-1002', timestamp('2024-03-12 03:00:00'), timestamp('2024-03-12 05:00:00'), 2.0, 'Valve-3inch', 'Emergency valve repair', 380.00, current_timestamp()),
('ME-1012', 'A-102', NULL, 'Preventive', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-13 08:00:00'), timestamp('2024-03-13 09:00:00'), 1.0, 'Oil-Hydraulic-5L', 'Hydraulic oil change', 120.00, current_timestamp()),
('ME-1013', 'A-100', NULL, 'Inspection', 'Amy Chen', 'amy.c@plantB.com', '555-1003', timestamp('2024-03-14 10:00:00'), timestamp('2024-03-14 10:30:00'), 0.5, NULL, 'Quarterly inspection', 0.00, current_timestamp()),
('ME-1014', 'A-101', NULL, 'Corrective', 'John Davis', 'john.d@plantC.com', '555-1004', timestamp('2024-03-15 14:00:00'), timestamp('2024-03-15 16:00:00'), 2.0, 'Gasket-Set', 'Gasket replacement', 65.00, current_timestamp()),
('ME-1015', 'A-102', NULL, 'Preventive', 'Sarah Lee', 'sarah.l@plantA.com', '555-1002', timestamp('2024-03-16 09:00:00'), timestamp('2024-03-16 10:00:00'), 1.0, 'Coolant-10L', 'Coolant flush', 85.00, current_timestamp()),
('ME-1016', 'A-100', NULL, 'Emergency', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-17 23:00:00'), timestamp('2024-03-18 01:00:00'), 2.0, 'Fuse-100A', 'Emergency power restoration', 200.00, current_timestamp()),
('ME-1017', 'A-101', NULL, 'Inspection', 'Amy Chen', 'amy.c@plantB.com', '555-1003', timestamp('2024-03-18 08:00:00'), timestamp('2024-03-18 08:20:00'), 0.33, NULL, 'Pre-shift check', 0.00, current_timestamp()),
('ME-1018', 'A-102', NULL, 'Corrective', 'John Davis', 'john.d@plantC.com', '555-1004', timestamp('2024-03-19 13:00:00'), timestamp('2024-03-19 15:30:00'), 2.5, 'PLC-Module', 'PLC module replacement', 550.00, current_timestamp()),
('ME-1019', 'A-100', NULL, 'Preventive', 'Sarah Lee', 'sarah.l@plantA.com', '555-1002', timestamp('2024-03-20 09:00:00'), timestamp('2024-03-20 10:30:00'), 1.5, 'Chain-Drive', 'Drive chain replacement', 145.00, current_timestamp()),
('ME-1020', 'A-101', NULL, 'Inspection', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-21 11:00:00'), timestamp('2024-03-21 11:15:00'), 0.25, NULL, 'Visual inspection', 0.00, current_timestamp()),
('ME-1021', 'A-102', NULL, 'Emergency', 'Amy Chen', 'amy.c@plantB.com', '555-1003', timestamp('2024-03-22 02:00:00'), timestamp('2024-03-22 04:30:00'), 2.5, 'Pump-Hydraulic', 'Hydraulic pump repair', 680.00, current_timestamp()),
('ME-1022', 'A-100', NULL, 'Preventive', 'John Davis', 'john.d@plantC.com', '555-1004', timestamp('2024-03-23 10:00:00'), timestamp('2024-03-23 11:00:00'), 1.0, 'Filter-Air', 'Air filter change', 55.00, current_timestamp()),
('ME-1023', 'A-101', NULL, 'Corrective', 'Sarah Lee', 'sarah.l@plantA.com', '555-1002', timestamp('2024-03-24 14:00:00'), timestamp('2024-03-24 16:30:00'), 2.5, 'Switch-Limit', 'Limit switch replacement', 95.00, current_timestamp()),
('ME-1024', 'A-102', NULL, 'Inspection', 'Mike Anderson', 'mike.a@plantA.com', '555-1001', timestamp('2024-03-25 08:00:00'), timestamp('2024-03-25 08:45:00'), 0.75, NULL, 'End-of-quarter audit', 0.00, current_timestamp());

-- =============================================
-- TABLE 9: PRODUCT_SPECIFICATIONS (25 rows with sensitive IP)
-- =============================================
DROP TABLE IF EXISTS product_specs;
CREATE TABLE product_specs (
  spec_id STRING NOT NULL,
  product_name STRING NOT NULL,
  spec_version STRING NOT NULL,
  spec_text STRING,
  cad_file_uri STRING,
  material_composition STRING,
  tolerance STRING,
  created_by STRING,
  created_at TIMESTAMP,
  CONSTRAINT pk_product_specs PRIMARY KEY (spec_id)
) USING DELTA
COMMENT 'Product specifications with sensitive IP';

INSERT INTO product_specs VALUES
('SPEC-001', 'Widget-Alpha', 'v1.2', 'Proprietary aluminum alloy casting with precision CNC machining', 's3://cad/widget-alpha-v1.2.dwg', 'Al-6061-T6 with proprietary heat treatment', '±0.01mm', 'eng_smith@company.com', current_timestamp()),
('SPEC-002', 'Bracket-Beta', 'v2.0', 'Steel bracket with specialized coating process', 's3://cad/bracket-beta-v2.0.dwg', 'AISI 4140 steel', '±0.05mm', 'eng_jones@company.com', current_timestamp()),
('SPEC-003', 'Housing-Gamma', 'v1.5', 'Composite housing with embedded sensors', 's3://cad/housing-gamma-v1.5.dwg', 'Carbon fiber reinforced polymer', '±0.02mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-004', 'Gear-Delta', 'v3.1', 'Precision gear with proprietary tooth profile', 's3://cad/gear-delta-v3.1.dwg', 'Tool steel with carburizing', '±0.001mm', 'eng_smith@company.com', current_timestamp()),
('SPEC-005', 'Shaft-Epsilon', 'v1.0', 'Hardened shaft with specialty surface finish', 's3://cad/shaft-epsilon-v1.0.dwg', 'SAE 1045 carbon steel', '±0.005mm', 'eng_jones@company.com', current_timestamp()),
('SPEC-006', 'Valve-Zeta', 'v2.2', 'High-pressure valve assembly', 's3://cad/valve-zeta-v2.2.dwg', 'Stainless steel 316', '±0.02mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-007', 'Bearing-Eta', 'v1.8', 'Custom bearing with extended life design', 's3://cad/bearing-eta-v1.8.dwg', 'Chrome steel with PTFE coating', '±0.002mm', 'eng_smith@company.com', current_timestamp()),
('SPEC-008', 'Motor-Theta', 'v4.0', 'High-efficiency motor design', 's3://cad/motor-theta-v4.0.dwg', 'Copper windings with rare-earth magnets', '±0.1mm', 'eng_jones@company.com', current_timestamp()),
('SPEC-009', 'Sensor-Iota', 'v2.5', 'Precision temperature sensor assembly', 's3://cad/sensor-iota-v2.5.dwg', 'Silicon with platinum RTD', '±0.01°C', 'eng_wang@company.com', current_timestamp()),
('SPEC-010', 'Filter-Kappa', 'v1.3', 'Multi-stage filtration system', 's3://cad/filter-kappa-v1.3.dwg', 'Sintered bronze with polymer membrane', '±0.05mm', 'eng_smith@company.com', current_timestamp()),
('SPEC-011', 'Pump-Lambda', 'v3.0', 'Variable speed pump mechanism', 's3://cad/pump-lambda-v3.0.dwg', 'Cast iron with ceramic seals', '±0.02mm', 'eng_jones@company.com', current_timestamp()),
('SPEC-012', 'Controller-Mu', 'v5.1', 'Programmable logic controller', 's3://cad/controller-mu-v5.1.dwg', 'PCB with ARM processor', '±0.1mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-013', 'Heater-Nu', 'v2.0', 'Industrial heating element', 's3://cad/heater-nu-v2.0.dwg', 'Nichrome wire with ceramic insulation', '±5W', 'eng_smith@company.com', current_timestamp()),
('SPEC-014', 'Cooler-Xi', 'v1.7', 'Heat exchanger assembly', 's3://cad/cooler-xi-v1.7.dwg', 'Copper tubes with aluminum fins', '±0.5°C', 'eng_jones@company.com', current_timestamp()),
('SPEC-015', 'Actuator-Omicron', 'v2.8', 'Pneumatic actuator system', 's3://cad/actuator-omicron-v2.8.dwg', 'Anodized aluminum with rubber seals', '±0.1mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-016', 'Display-Pi', 'v3.2', 'Industrial touchscreen display', 's3://cad/display-pi-v3.2.dwg', 'Tempered glass with ITO coating', '±1px', 'eng_smith@company.com', current_timestamp()),
('SPEC-017', 'Cable-Rho', 'v1.1', 'Shielded cable assembly', 's3://cad/cable-rho-v1.1.dwg', 'Copper conductor with braided shield', '±0.5ohm', 'eng_jones@company.com', current_timestamp()),
('SPEC-018', 'Connector-Sigma', 'v2.3', 'Industrial connector with IP67 rating', 's3://cad/connector-sigma-v2.3.dwg', 'Nickel-plated brass with silicone seal', '±0.02mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-019', 'Switch-Tau', 'v1.9', 'Heavy-duty limit switch', 's3://cad/switch-tau-v1.9.dwg', 'Steel housing with silver contacts', '±0.5N', 'eng_smith@company.com', current_timestamp()),
('SPEC-020', 'Spring-Upsilon', 'v1.4', 'Compression spring with fatigue resistance', 's3://cad/spring-upsilon-v1.4.dwg', 'Music wire ASTM A228', '±5%', 'eng_jones@company.com', current_timestamp()),
('SPEC-021', 'Fastener-Phi', 'v2.1', 'High-strength bolt assembly', 's3://cad/fastener-phi-v2.1.dwg', 'Grade 8 steel with zinc coating', '±0.02mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-022', 'Plate-Chi', 'v1.6', 'Mounting plate with precision holes', 's3://cad/plate-chi-v1.6.dwg', 'Cold-rolled steel', '±0.1mm', 'eng_smith@company.com', current_timestamp()),
('SPEC-023', 'Tube-Psi', 'v2.4', 'Precision tubing for hydraulics', 's3://cad/tube-psi-v2.4.dwg', 'Seamless steel SAE J524', '±0.01mm', 'eng_jones@company.com', current_timestamp()),
('SPEC-024', 'Gasket-Omega', 'v1.2', 'High-temperature gasket material', 's3://cad/gasket-omega-v1.2.dwg', 'Graphite with stainless steel core', '±0.05mm', 'eng_wang@company.com', current_timestamp()),
('SPEC-025', 'Seal-Alpha2', 'v3.0', 'Dynamic seal for rotating shafts', 's3://cad/seal-alpha2-v3.0.dwg', 'Viton with PTFE lip', '±0.02mm', 'eng_smith@company.com', current_timestamp());

-- =============================================
-- TABLE 10: SHIPMENTS (25 rows with supplier/cost data)
-- =============================================
DROP TABLE IF EXISTS shipments;
CREATE TABLE shipments (
  shipment_id STRING NOT NULL,
  supplier_id STRING NOT NULL,
  destination_plant STRING NOT NULL,
  tracking_number STRING,
  ship_date DATE NOT NULL,
  expected_delivery DATE,
  actual_delivery DATE,
  carrier STRING,
  freight_cost DECIMAL(10,2),
  items_count INT,
  total_value DECIMAL(12,2),
  status STRING,
  created_at TIMESTAMP,
  CONSTRAINT pk_shipments PRIMARY KEY (shipment_id)
) USING DELTA
COMMENT 'Inbound shipments from suppliers';

INSERT INTO shipments VALUES
('SHIP-5000', 'SUP-10', 'Plant_A', 'TRK-100001', '2024-03-01', '2024-03-05', '2024-03-04', 'FedEx', 125.00, 50, 2500.00, 'Delivered', current_timestamp()),
('SHIP-5001', 'SUP-11', 'Plant_B', 'TRK-100002', '2024-03-02', '2024-03-08', '2024-03-08', 'UPS', 185.00, 30, 1850.00, 'Delivered', current_timestamp()),
('SHIP-5002', 'SUP-10', 'Plant_C', 'TRK-100003', '2024-03-03', '2024-03-07', NULL, 'DHL', 145.00, 40, 3200.00, 'In Transit', current_timestamp()),
('SHIP-5003', 'SUP-11', 'Plant_A', 'TRK-100004', '2024-03-04', '2024-03-09', '2024-03-09', 'FedEx', 165.00, 25, 1520.00, 'Delivered', current_timestamp()),
('SHIP-5004', 'SUP-10', 'Plant_B', 'TRK-100005', '2024-03-05', '2024-03-10', NULL, 'UPS', 195.00, 60, 4100.00, 'In Transit', current_timestamp()),
('SHIP-5005', 'SUP-11', 'Plant_C', 'TRK-100006', '2024-03-06', '2024-03-11', '2024-03-10', 'DHL', 175.00, 35, 2750.00, 'Delivered', current_timestamp()),
('SHIP-5006', 'SUP-10', 'Plant_A', 'TRK-100007', '2024-03-07', '2024-03-12', NULL, 'FedEx', 135.00, 45, 2890.00, 'In Transit', current_timestamp()),
('SHIP-5007', 'SUP-11', 'Plant_B', 'TRK-100008', '2024-03-08', '2024-03-13', '2024-03-12', 'UPS', 205.00, 55, 3650.00, 'Delivered', current_timestamp()),
('SHIP-5008', 'SUP-10', 'Plant_C', 'TRK-100009', '2024-03-09', '2024-03-14', NULL, 'DHL', 155.00, 30, 1980.00, 'Pending', current_timestamp()),
('SHIP-5009', 'SUP-11', 'Plant_A', 'TRK-100010', '2024-03-10', '2024-03-15', '2024-03-14', 'FedEx', 185.00, 42, 3150.00, 'Delivered', current_timestamp()),
('SHIP-5010', 'SUP-10', 'Plant_B', 'TRK-100011', '2024-03-11', '2024-03-16', NULL, 'UPS', 165.00, 38, 2480.00, 'In Transit', current_timestamp()),
('SHIP-5011', 'SUP-11', 'Plant_C', 'TRK-100012', '2024-03-12', '2024-03-17', '2024-03-16', 'DHL', 145.00, 28, 1740.00, 'Delivered', current_timestamp()),
('SHIP-5012', 'SUP-10', 'Plant_A', 'TRK-100013', '2024-03-13', '2024-03-18', NULL, 'FedEx', 175.00, 52, 3580.00, 'Pending', current_timestamp()),
('SHIP-5013', 'SUP-11', 'Plant_B', 'TRK-100014', '2024-03-14', '2024-03-19', '2024-03-18', 'UPS', 195.00, 48, 3120.00, 'Delivered', current_timestamp()),
('SHIP-5014', 'SUP-10', 'Plant_C', 'TRK-100015', '2024-03-15', '2024-03-20', NULL, 'DHL', 165.00, 35, 2240.00, 'In Transit', current_timestamp()),
('SHIP-5015', 'SUP-11', 'Plant_A', 'TRK-100016', '2024-03-16', '2024-03-21', '2024-03-20', 'FedEx', 185.00, 44, 2960.00, 'Delivered', current_timestamp()),
('SHIP-5016', 'SUP-10', 'Plant_B', 'TRK-100017', '2024-03-17', '2024-03-22', NULL, 'UPS', 145.00, 31, 1890.00, 'Pending', current_timestamp()),
('SHIP-5017', 'SUP-11', 'Plant_C', 'TRK-100018', '2024-03-18', '2024-03-23', '2024-03-22', 'DHL', 175.00, 47, 3380.00, 'Delivered', current_timestamp()),
('SHIP-5018', 'SUP-10', 'Plant_A', 'TRK-100019', '2024-03-19', '2024-03-24', NULL, 'FedEx', 205.00, 58, 4250.00, 'In Transit', current_timestamp()),
('SHIP-5019', 'SUP-11', 'Plant_B', 'TRK-100020', '2024-03-20', '2024-03-25', '2024-03-24', 'UPS', 155.00, 33, 2110.00, 'Delivered', current_timestamp()),
('SHIP-5020', 'SUP-10', 'Plant_C', 'TRK-100021', '2024-03-21', '2024-03-26', NULL, 'DHL', 165.00, 41, 2770.00, 'Pending', current_timestamp()),
('SHIP-5021', 'SUP-11', 'Plant_A', 'TRK-100022', '2024-03-22', '2024-03-27', '2024-03-26', 'FedEx', 195.00, 49, 3420.00, 'Delivered', current_timestamp()),
('SHIP-5022', 'SUP-10', 'Plant_B', 'TRK-100023', '2024-03-23', '2024-03-28', NULL, 'UPS', 175.00, 36, 2340.00, 'In Transit', current_timestamp()),
('SHIP-5023', 'SUP-11', 'Plant_C', 'TRK-100024', '2024-03-24', '2024-03-29', '2024-03-28', 'DHL', 185.00, 43, 2990.00, 'Delivered', current_timestamp()),
('SHIP-5024', 'SUP-10', 'Plant_A', 'TRK-100025', '2024-03-25', '2024-03-30', NULL, 'FedEx', 145.00, 29, 1850.00, 'Pending', current_timestamp());

-- =============================================
-- TABLE 11: EMPLOYEE_CONTACTS (25 rows with PII)
-- =============================================
DROP TABLE IF EXISTS employee_contacts;
CREATE TABLE employee_contacts (
  employee_id STRING NOT NULL,
  full_name STRING NOT NULL,
  email STRING NOT NULL,
  phone STRING,
  department STRING NOT NULL,
  role STRING NOT NULL,
  site_location STRING NOT NULL,
  hire_date DATE,
  created_at TIMESTAMP,
  CONSTRAINT pk_employee_contacts PRIMARY KEY (employee_id)
) USING DELTA
COMMENT 'Employee contact information with PII';

INSERT INTO employee_contacts VALUES
('EMP-1001', 'Mike Anderson', 'mike.anderson@company.com', '555-1001', 'Maintenance', 'Technician', 'Plant_A', '2020-01-15', current_timestamp()),
('EMP-1002', 'Sarah Lee', 'sarah.lee@company.com', '555-1002', 'Maintenance', 'Technician', 'Plant_A', '2019-03-22', current_timestamp()),
('EMP-1003', 'Amy Chen', 'amy.chen@company.com', '555-1003', 'Maintenance', 'Technician', 'Plant_B', '2021-07-10', current_timestamp()),
('EMP-1004', 'John Davis', 'john.davis@company.com', '555-1004', 'Maintenance', 'Technician', 'Plant_C', '2018-11-05', current_timestamp()),
('EMP-1005', 'Maria Rodriguez', 'maria.rodriguez@company.com', '555-1005', 'Operations', 'Plant Operator', 'Plant_A', '2020-05-18', current_timestamp()),
('EMP-1006', 'David Kim', 'david.kim@company.com', '555-1006', 'Operations', 'Plant Operator', 'Plant_B', '2019-09-12', current_timestamp()),
('EMP-1007', 'Jennifer Taylor', 'jennifer.taylor@company.com', '555-1007', 'Operations', 'Plant Operator', 'Plant_C', '2021-02-28', current_timestamp()),
('EMP-1008', 'Robert Wilson', 'robert.wilson@company.com', '555-1008', 'Quality', 'Quality Engineer', 'Plant_A', '2018-06-14', current_timestamp()),
('EMP-1009', 'Lisa Brown', 'lisa.brown@company.com', '555-1009', 'Quality', 'Quality Engineer', 'Plant_B', '2020-10-03', current_timestamp()),
('EMP-1010', 'James Miller', 'james.miller@company.com', '555-1010', 'Quality', 'Quality Engineer', 'Plant_C', '2019-12-20', current_timestamp()),
('EMP-1011', 'Patricia Garcia', 'patricia.garcia@company.com', '555-1011', 'Engineering', 'R&D Engineer', 'Plant_A', '2017-04-08', current_timestamp()),
('EMP-1012', 'Michael Smith', 'michael.smith@company.com', '555-1012', 'Engineering', 'R&D Engineer', 'Plant_A', '2016-08-25', current_timestamp()),
('EMP-1013', 'Linda Jones', 'linda.jones@company.com', '555-1013', 'Engineering', 'R&D Engineer', 'Plant_B', '2018-01-17', current_timestamp()),
('EMP-1014', 'William Wang', 'william.wang@company.com', '555-1014', 'Engineering', 'R&D Engineer', 'Plant_B', '2019-05-30', current_timestamp()),
('EMP-1015', 'Elizabeth Martinez', 'elizabeth.martinez@company.com', '555-1015', 'Supply Chain', 'Supply Chain Manager', 'Plant_A', '2017-11-09', current_timestamp()),
('EMP-1016', 'Charles Thompson', 'charles.thompson@company.com', '555-1016', 'Supply Chain', 'Supply Chain Manager', 'Plant_B', '2018-03-21', current_timestamp()),
('EMP-1017', 'Barbara White', 'barbara.white@company.com', '555-1017', 'Supply Chain', 'Supply Chain Manager', 'Plant_C', '2020-08-14', current_timestamp()),
('EMP-1018', 'Joseph Harris', 'joseph.harris@company.com', '555-1018', 'Management', 'Site Lead', 'Plant_A', '2015-02-10', current_timestamp()),
('EMP-1019', 'Susan Clark', 'susan.clark@company.com', '555-1019', 'Management', 'Site Lead', 'Plant_B', '2016-06-18', current_timestamp()),
('EMP-1020', 'Thomas Lewis', 'thomas.lewis@company.com', '555-1020', 'Management', 'Site Lead', 'Plant_C', '2017-09-25', current_timestamp()),
('EMP-1021', 'Nancy Walker', 'nancy.walker@company.com', '555-1021', 'Maintenance', 'Supervisor', 'Plant_A', '2018-12-07', current_timestamp()),
('EMP-1022', 'Daniel Hall', 'daniel.hall@company.com', '555-1022', 'Operations', 'Supervisor', 'Plant_B', '2019-04-16', current_timestamp()),
('EMP-1023', 'Karen Allen', 'karen.allen@company.com', '555-1023', 'Quality', 'Supervisor', 'Plant_C', '2020-07-22', current_timestamp()),
('EMP-1024', 'Steven Young', 'steven.young@company.com', '555-1024', 'Engineering', 'Senior Engineer', 'Plant_A', '2015-10-11', current_timestamp()),
('EMP-1025', 'Betty King', 'betty.king@company.com', '555-1025', 'Supply Chain', 'Analyst', 'Plant_B', '2021-01-29', current_timestamp());

-- =============================================
-- TABLE 12: PERFORMANCE_METRICS (25 rows with operational data)
-- =============================================
DROP TABLE IF EXISTS performance_metrics;
CREATE TABLE performance_metrics (
  metric_id STRING NOT NULL,
  asset_id STRING NOT NULL,
  metric_date DATE NOT NULL,
  uptime_hours DECIMAL(5,2),
  downtime_hours DECIMAL(5,2),
  efficiency_percent DECIMAL(5,2),
  defect_rate DECIMAL(5,4),
  output_units INT,
  energy_kwh DECIMAL(10,2),
  maintenance_cost DECIMAL(10,2),
  created_at TIMESTAMP,
  CONSTRAINT pk_performance_metrics PRIMARY KEY (metric_id)
) USING DELTA
COMMENT 'Daily performance metrics by asset';

INSERT INTO performance_metrics VALUES
('PM-3000', 'A-100', '2024-03-01', 22.5, 1.5, 93.75, 0.0250, 1000, 450.25, 125.50, current_timestamp()),
('PM-3001', 'A-101', '2024-03-01', 21.0, 3.0, 87.50, 0.0300, 600, 380.50, 85.00, current_timestamp()),
('PM-3002', 'A-102', '2024-03-01', 23.0, 1.0, 95.83, 0.0150, 850, 520.75, 45.00, current_timestamp()),
('PM-3003', 'A-100', '2024-03-02', 20.0, 4.0, 83.33, 0.0350, 850, 425.00, 220.00, current_timestamp()),
('PM-3004', 'A-101', '2024-03-02', 22.0, 2.0, 91.67, 0.0200, 580, 370.25, 0.00, current_timestamp()),
('PM-3005', 'A-102', '2024-03-02', 23.5, 0.5, 97.92, 0.0100, 870, 535.50, 0.00, current_timestamp()),
('PM-3006', 'A-100', '2024-03-03', 21.5, 2.5, 89.58, 0.0280, 920, 440.75, 0.00, current_timestamp()),
('PM-3007', 'A-101', '2024-03-03', 19.0, 5.0, 79.17, 0.0400, 550, 360.00, 85.00, current_timestamp()),
('PM-3008', 'A-102', '2024-03-03', 22.5, 1.5, 93.75, 0.0180, 840, 515.25, 0.00, current_timestamp()),
('PM-3009', 'A-100', '2024-03-04', 22.0, 2.0, 91.67, 0.0220, 950, 445.50, 0.00, current_timestamp()),
('PM-3010', 'A-101', '2024-03-04', 21.5, 2.5, 89.58, 0.0240, 590, 375.75, 0.00, current_timestamp()),
('PM-3011', 'A-102', '2024-03-04', 23.0, 1.0, 95.83, 0.0160, 855, 525.00, 450.00, current_timestamp()),
('PM-3012', 'A-100', '2024-03-05', 18.5, 5.5, 77.08, 0.0380, 800, 410.25, 220.00, current_timestamp()),
('PM-3013', 'A-101', '2024-03-05', 22.5, 1.5, 93.75, 0.0190, 610, 385.50, 0.00, current_timestamp()),
('PM-3014', 'A-102', '2024-03-05', 22.0, 2.0, 91.67, 0.0210, 830, 510.75, 0.00, current_timestamp()),
('PM-3015', 'A-100', '2024-03-06', 21.0, 3.0, 87.50, 0.0300, 880, 435.00, 0.00, current_timestamp()),
('PM-3016', 'A-101', '2024-03-06', 20.5, 3.5, 85.42, 0.0320, 570, 365.25, 0.00, current_timestamp()),
('PM-3017', 'A-102', '2024-03-06', 23.5, 0.5, 97.92, 0.0120, 865, 530.50, 0.00, current_timestamp()),
('PM-3018', 'A-100', '2024-03-07', 22.5, 1.5, 93.75, 0.0230, 940, 448.75, 95.00, current_timestamp()),
('PM-3019', 'A-101', '2024-03-07', 21.0, 3.0, 87.50, 0.0290, 585, 372.00, 0.00, current_timestamp()),
('PM-3020', 'A-100', '2024-03-08', 20.0, 4.0, 83.33, 0.0350, 870, 430.25, 0.00, current_timestamp()),
('PM-3021', 'A-101', '2024-03-08', 22.5, 1.5, 93.75, 0.0200, 605, 390.50, 380.00, current_timestamp()),
('PM-3022', 'A-102', '2024-03-08', 22.0, 2.0, 91.67, 0.0220, 845, 518.75, 0.00, current_timestamp()),
('PM-3023', 'A-100', '2024-03-09', 21.5, 2.5, 89.58, 0.0270, 910, 442.50, 0.00, current_timestamp()),
('PM-3024', 'A-101', '2024-03-09', 20.0, 4.0, 83.33, 0.0340, 565, 368.25, 0.00, current_timestamp());

-- =============================================
-- VERIFICATION
-- =============================================
SELECT 'maintenance_events' AS table_name, COUNT(*) AS row_count FROM maintenance_events
UNION ALL SELECT 'product_specs', COUNT(*) FROM product_specs
UNION ALL SELECT 'shipments', COUNT(*) FROM shipments
UNION ALL SELECT 'employee_contacts', COUNT(*) FROM employee_contacts
UNION ALL SELECT 'performance_metrics', COUNT(*) FROM performance_metrics
ORDER BY table_name;

