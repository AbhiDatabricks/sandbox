-- TELCO EXTENDED
USE CATALOG apscat; USE SCHEMA telco;

DROP TABLE IF EXISTS devices;
CREATE TABLE devices (device_id STRING, subscriber_id STRING, imei STRING, device_model STRING,
PRIMARY KEY (device_id)) USING DELTA;
INSERT INTO devices VALUES
('D-1', 'S-1001', '123456789012345', 'iPhone 14'),
('D-2', 'S-1002', '234567890123456', 'Samsung S23'),
('D-3', 'S-1003', '345678901234567', 'Google Pixel');

SELECT 'devices' AS tbl, COUNT(*) AS cnt FROM devices;
