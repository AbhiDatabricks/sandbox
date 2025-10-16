-- =============================================
-- EXTENDED FINANCE TABLES
-- =============================================

USE CATALOG apscat;
USE SCHEMA finance;

-- =============================================
-- TABLE 3: CREDIT_CARDS (25 rows)
-- =============================================
DROP TABLE IF EXISTS credit_cards;
CREATE TABLE credit_cards (
  card_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  card_number STRING NOT NULL,
  card_type STRING NOT NULL,
  credit_limit DECIMAL(12,2),
  current_balance DECIMAL(12,2),
  available_credit DECIMAL(12,2),
  apr DECIMAL(5,2),
  issued_date DATE,
  expiry_date DATE,
  status STRING,
  CONSTRAINT pk_credit_cards PRIMARY KEY (card_id)
) USING DELTA
COMMENT 'Credit card accounts';

INSERT INTO credit_cards VALUES
('CC-8001', 'C-1001', '4532-1234-5678-9010', 'Visa', 10000.00, 2450.75, 7549.25, 18.99, '2020-02-01', '2025-02-01', 'Active'),
('CC-8002', 'C-1002', '5425-2345-6789-0123', 'Mastercard', 15000.00, 4200.50, 10799.50, 16.99, '2019-06-15', '2024-06-15', 'Active'),
('CC-8003', 'C-1003', '3782-3456-7890-1234', 'Amex', 5000.00, 1850.25, 3149.75, 22.99, '2021-04-10', '2025-04-10', 'Active'),
('CC-8004', 'C-1004', '6011-4567-8901-2345', 'Discover', 8000.00, 3100.00, 4900.00, 19.99, '2020-10-20', '2025-10-20', 'Active'),
('CC-8005', 'C-1005', '4532-5678-9012-3456', 'Visa', 25000.00, 8750.80, 16249.20, 15.99, '2018-12-05', '2024-12-05', 'Active'),
('CC-8006', 'C-1006', '5425-6789-0123-4567', 'Mastercard', 12000.00, 2940.60, 9059.40, 17.99, '2019-08-18', '2024-08-18', 'Active'),
('CC-8007', 'C-1007', '4532-7890-1234-5678', 'Visa', 18000.00, 6180.45, 11819.55, 16.49, '2020-03-25', '2025-03-25', 'Active'),
('CC-8008', 'C-1008', '5425-8901-2345-6789', 'Mastercard', 20000.00, 7325.90, 12674.10, 15.49, '2019-11-12', '2024-11-12', 'Active'),
('CC-8009', 'C-1009', '6011-9012-3456-7890', 'Discover', 6000.00, 3510.25, 2489.75, 20.99, '2021-02-08', '2026-02-08', 'Active'),
('CC-8010', 'C-1010', '4532-0123-4567-8901', 'Visa', 30000.00, 12400.50, 17599.50, 14.99, '2018-09-30', '2024-09-30', 'Active'),
('CC-8011', 'C-1011', '5425-1234-5678-9012', 'Mastercard', 10000.00, 4890.70, 5109.30, 18.49, '2020-07-15', '2025-07-15', 'Active'),
('CC-8012', 'C-1012', '4532-2345-6789-0123', 'Visa', 14000.00, 5670.85, 8329.15, 17.49, '2019-12-20', '2024-12-20', 'Active'),
('CC-8013', 'C-1013', '6011-3456-7890-1234', 'Discover', 7000.00, 3825.40, 3174.60, 19.49, '2020-12-08', '2025-12-08', 'Active'),
('CC-8014', 'C-1014', '5425-4567-8901-2345', 'Mastercard', 5000.00, 2950.20, 2049.80, 21.99, '2021-05-15', '2026-05-15', 'Active'),
('CC-8015', 'C-1015', '4532-5678-9012-3456', 'Visa', 16000.00, 7240.60, 8759.40, 16.99, '2019-10-22', '2024-10-22', 'Active'),
('CC-8016', 'C-1016', '3782-6789-0123-4567', 'Amex', 35000.00, 15600.75, 19399.25, 14.49, '2018-06-10', '2024-06-10', 'Active'),
('CC-8017', 'C-1017', '6011-7890-1234-5678', 'Discover', 5500.00, 3410.55, 2089.45, 20.49, '2020-11-18', '2025-11-18', 'Active'),
('CC-8018', 'C-1018', '4532-8901-2345-6789', 'Visa', 22000.00, 9850.40, 12149.60, 15.99, '2019-04-05', '2024-04-05', 'Active'),
('CC-8019', 'C-1019', '5425-9012-3456-7890', 'Mastercard', 13000.00, 6120.85, 6879.15, 17.49, '2020-08-12', '2025-08-12', 'Active'),
('CC-8020', 'C-1020', '4532-0123-4567-8901', 'Visa', 17000.00, 7750.90, 9249.10, 16.49, '2019-12-01', '2024-12-01', 'Active'),
('CC-8021', 'C-1005', '5425-1111-2222-3333', 'Mastercard', 20000.00, 5400.00, 14600.00, 15.49, '2019-01-15', '2024-01-15', 'Active'),
('CC-8022', 'C-1010', '6011-4444-5555-6666', 'Discover', 25000.00, 8200.50, 16799.50, 14.99, '2018-11-20', '2024-11-20', 'Active'),
('CC-8023', 'C-1016', '4532-7777-8888-9999', 'Visa', 40000.00, 12500.75, 27499.25, 13.99, '2018-08-05', '2024-08-05', 'Active'),
('CC-8024', 'C-1007', '5425-0000-1111-2222', 'Mastercard', 11000.00, 4200.30, 6799.70, 17.99, '2020-05-10', '2025-05-10', 'Active'),
('CC-8025', 'C-1012', '3782-3333-4444-5555', 'Amex', 15000.00, 6800.45, 8199.55, 15.99, '2020-01-25', '2025-01-25', 'Active');

-- =============================================
-- TABLE 4: TRANSACTIONS (30 rows)
-- =============================================
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
  transaction_id STRING NOT NULL,
  account_id STRING,
  card_id STRING,
  customer_id STRING NOT NULL,
  transaction_type STRING NOT NULL,
  amount DECIMAL(12,2),
  merchant_name STRING,
  merchant_category STRING,
  transaction_date TIMESTAMP,
  ip_address STRING,
  device_type STRING,
  fraud_flag BOOLEAN,
  status STRING,
  CONSTRAINT pk_transactions PRIMARY KEY (transaction_id)
) USING DELTA
COMMENT 'All financial transactions';

INSERT INTO transactions VALUES
('TXN-10001', 'A-5001', NULL, 'C-1001', 'Debit', 85.50, 'Amazon', 'Retail', timestamp('2024-03-01 10:15:30'), '192.168.1.100', 'Mobile', false, 'Completed'),
('TXN-10002', NULL, 'CC-8001', 'C-1001', 'Credit', 125.75, 'Whole Foods', 'Grocery', timestamp('2024-03-01 14:22:15'), '192.168.1.100', 'Mobile', false, 'Completed'),
('TXN-10003', 'A-5003', NULL, 'C-1002', 'Debit', 450.00, 'Best Buy', 'Electronics', timestamp('2024-03-02 11:30:45'), '10.0.0.50', 'Desktop', false, 'Completed'),
('TXN-10004', NULL, 'CC-8002', 'C-1002', 'Credit', 2500.00, 'Apple Store', 'Electronics', timestamp('2024-03-02 16:45:20'), '10.0.0.50', 'Desktop', false, 'Completed'),
('TXN-10005', 'A-5005', NULL, 'C-1003', 'Debit', 65.25, 'Shell Gas', 'Fuel', timestamp('2024-03-03 08:10:00'), '172.16.0.25', 'Mobile', false, 'Completed'),
('TXN-10006', NULL, 'CC-8003', 'C-1003', 'Credit', 1850.00, 'Delta Airlines', 'Travel', timestamp('2024-03-03 12:20:30'), '172.16.0.25', 'Tablet', false, 'Completed'),
('TXN-10007', 'A-5006', NULL, 'C-1004', 'Debit', 220.40, 'Target', 'Retail', timestamp('2024-03-04 09:35:15'), '192.168.2.75', 'Mobile', false, 'Completed'),
('TXN-10008', NULL, 'CC-8004', 'C-1004', 'Credit', 3100.00, 'Home Depot', 'Home Improvement', timestamp('2024-03-04 15:50:40'), '192.168.2.75', 'Desktop', false, 'Completed'),
('TXN-10009', 'A-5008', NULL, 'C-1005', 'Debit', 1200.00, 'Rent Payment', 'Housing', timestamp('2024-03-05 00:05:00'), '10.1.1.100', 'Desktop', false, 'Completed'),
('TXN-10010', NULL, 'CC-8005', 'C-1005', 'Credit', 8750.80, 'Tesla', 'Automotive', timestamp('2024-03-05 13:25:10'), '10.1.1.100', 'Desktop', true, 'Under Review'),
('TXN-10011', 'A-5010', NULL, 'C-1006', 'Debit', 95.60, 'Starbucks', 'Food & Beverage', timestamp('2024-03-06 07:40:25'), '192.168.3.120', 'Mobile', false, 'Completed'),
('TXN-10012', NULL, 'CC-8006', 'C-1006', 'Credit', 540.80, 'Macys', 'Clothing', timestamp('2024-03-06 18:15:50'), '192.168.3.120', 'Mobile', false, 'Completed'),
('TXN-10013', 'A-5011', NULL, 'C-1007', 'Debit', 180.25, 'Costco', 'Wholesale', timestamp('2024-03-07 10:50:30'), '172.16.5.80', 'Mobile', false, 'Completed'),
('TXN-10014', NULL, 'CC-8007', 'C-1007', 'Credit', 2200.00, 'Marriott Hotels', 'Travel', timestamp('2024-03-07 14:30:15'), '172.16.5.80', 'Desktop', false, 'Completed'),
('TXN-10015', 'A-5013', NULL, 'C-1008', 'Debit', 325.60, 'Walmart', 'Retail', timestamp('2024-03-08 11:20:40'), '10.2.2.50', 'Mobile', false, 'Completed'),
('TXN-10016', NULL, 'CC-8008', 'C-1008', 'Credit', 7325.90, 'Furniture Store', 'Home Furnishing', timestamp('2024-03-08 16:40:20'), '10.2.2.50', 'Desktop', false, 'Completed'),
('TXN-10017', 'A-5014', NULL, 'C-1009', 'Debit', 510.40, 'Insurance Premium', 'Insurance', timestamp('2024-03-09 00:10:00'), '192.168.4.90', 'Desktop', false, 'Completed'),
('TXN-10018', NULL, 'CC-8009', 'C-1009', 'Credit', 3000.00, 'Unauthorized Charge', 'Unknown', timestamp('2024-03-09 23:45:30'), '203.0.113.50', 'Mobile', true, 'Disputed'),
('TXN-10019', 'A-5015', NULL, 'C-1010', 'Debit', 2400.75, 'Property Tax', 'Government', timestamp('2024-03-10 09:00:15'), '10.3.3.100', 'Desktop', false, 'Completed'),
('TXN-10020', NULL, 'CC-8010', 'C-1010', 'Credit', 12400.50, 'Jewelry Store', 'Luxury', timestamp('2024-03-10 15:30:45'), '10.3.3.100', 'Desktop', false, 'Completed'),
('TXN-10021', 'A-5017', NULL, 'C-1011', 'Debit', 890.30, 'Utility Bill', 'Utilities', timestamp('2024-03-11 00:15:00'), '172.16.8.120', 'Desktop', false, 'Completed'),
('TXN-10022', NULL, 'CC-8011', 'C-1011', 'Credit', 4000.00, 'Suspicious Charge', 'Unknown', timestamp('2024-03-11 03:20:30'), '198.51.100.75', 'Mobile', true, 'Blocked'),
('TXN-10023', 'A-5018', NULL, 'C-1012', 'Debit', 670.90, 'Restaurant', 'Food & Beverage', timestamp('2024-03-12 19:45:15'), '192.168.5.150', 'Mobile', false, 'Completed'),
('TXN-10024', NULL, 'CC-8012', 'C-1012', 'Credit', 5670.85, 'Medical Services', 'Healthcare', timestamp('2024-03-12 14:10:40'), '192.168.5.150', 'Desktop', false, 'Completed'),
('TXN-10025', 'A-5020', NULL, 'C-1013', 'Debit', 325.15, 'Gas Station', 'Fuel', timestamp('2024-03-13 08:25:20'), '10.4.4.80', 'Mobile', false, 'Completed'),
('TXN-10026', 'A-5021', NULL, 'C-1014', 'Debit', 150.60, 'Pharmacy', 'Healthcare', timestamp('2024-03-14 12:40:35'), '172.16.10.90', 'Mobile', false, 'Completed'),
('TXN-10027', 'A-5022', NULL, 'C-1015', 'Debit', 1240.85, 'Car Payment', 'Automotive', timestamp('2024-03-15 00:05:00'), '192.168.6.110', 'Desktop', false, 'Completed'),
('TXN-10028', 'A-5023', NULL, 'C-1016', 'Debit', 5600.40, 'Investment Transfer', 'Investment', timestamp('2024-03-16 10:30:15'), '10.5.5.120', 'Desktop', false, 'Completed'),
('TXN-10029', 'A-5024', NULL, 'C-1017', 'Debit', 410.75, 'Grocery Store', 'Grocery', timestamp('2024-03-17 17:20:45'), '172.16.12.100', 'Mobile', false, 'Completed'),
('TXN-10030', 'A-5025', NULL, 'C-1018', 'Debit', 1850.20, 'Mortgage Payment', 'Housing', timestamp('2024-03-18 00:10:00'), '192.168.7.130', 'Desktop', false, 'Completed');

-- =============================================
-- TABLE 5: LOANS (20 rows)
-- =============================================
DROP TABLE IF EXISTS loans;
CREATE TABLE loans (
  loan_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  loan_type STRING NOT NULL,
  loan_amount DECIMAL(15,2),
  interest_rate DECIMAL(5,2),
  term_months INT,
  monthly_payment DECIMAL(10,2),
  outstanding_balance DECIMAL(15,2),
  origination_date DATE,
  maturity_date DATE,
  status STRING,
  CONSTRAINT pk_loans PRIMARY KEY (loan_id)
) USING DELTA
COMMENT 'Loan accounts';

INSERT INTO loans VALUES
('L-7001', 'C-1001', 'Personal', 15000.00, 8.99, 60, 311.38, 12450.00, '2022-01-15', '2027-01-15', 'Active'),
('L-7002', 'C-1002', 'Auto', 35000.00, 5.49, 72, 563.75, 28200.00, '2021-06-01', '2027-06-01', 'Active'),
('L-7003', 'C-1003', 'Personal', 10000.00, 10.49, 48, 256.89, 7850.00, '2022-03-10', '2026-03-10', 'Active'),
('L-7004', 'C-1005', 'Mortgage', 350000.00, 3.75, 360, 1621.00, 335000.00, '2019-01-01', '2049-01-01', 'Active'),
('L-7005', 'C-1007', 'Auto', 42000.00, 4.99, 60, 790.50, 32500.00, '2021-03-15', '2026-03-15', 'Active'),
('L-7006', 'C-1008', 'Personal', 25000.00, 9.49, 60, 524.75, 20100.00, '2022-05-20', '2027-05-20', 'Active'),
('L-7007', 'C-1010', 'Mortgage', 475000.00, 3.25, 360, 2067.00, 458000.00, '2018-09-01', '2048-09-01', 'Active'),
('L-7008', 'C-1012', 'Auto', 28000.00, 6.49, 60, 549.00, 21800.00, '2021-12-10', '2026-12-10', 'Active'),
('L-7009', 'C-1015', 'Personal', 20000.00, 8.49, 48, 495.50, 15200.00, '2022-10-05', '2026-10-05', 'Active'),
('L-7010', 'C-1016', 'Mortgage', 650000.00, 3.50, 360, 2918.00, 632000.00, '2018-06-15', '2048-06-15', 'Active'),
('L-7011', 'C-1018', 'Auto', 38000.00, 5.99, 72, 625.50, 30400.00, '2021-04-20', '2027-04-20', 'Active'),
('L-7012', 'C-1004', 'Personal', 8000.00, 11.99, 36, 265.00, 5200.00, '2022-09-15', '2025-09-15', 'Active'),
('L-7013', 'C-1006', 'Auto', 31000.00, 5.49, 60, 592.50, 24000.00, '2021-08-01', '2026-08-01', 'Active'),
('L-7014', 'C-1009', 'Personal', 12000.00, 9.99, 48, 304.50, 9450.00, '2022-02-28', '2026-02-28', 'Active'),
('L-7015', 'C-1011', 'Auto', 26000.00, 6.99, 60, 517.00, 20300.00, '2021-07-10', '2026-07-10', 'Active'),
('L-7016', 'C-1013', 'Personal', 7500.00, 10.99, 36, 245.75, 5100.00, '2022-12-01', '2025-12-01', 'Active'),
('L-7017', 'C-1014', 'Auto', 22000.00, 7.49, 60, 441.00, 17200.00, '2021-05-15', '2026-05-15', 'Active'),
('L-7018', 'C-1017', 'Personal', 18000.00, 9.49, 60, 378.00, 14500.00, '2022-11-20', '2027-11-20', 'Active'),
('L-7019', 'C-1019', 'Auto', 33000.00, 5.99, 72, 542.50, 26400.00, '2021-09-01', '2027-09-01', 'Active'),
('L-7020', 'C-1020', 'Personal', 16000.00, 8.99, 48, 399.00, 12200.00, '2022-08-10', '2026-08-10', 'Active');

-- Verify extended tables
SELECT 'credit_cards' AS table_name, COUNT(*) AS row_count FROM credit_cards
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL SELECT 'loans', COUNT(*) FROM loans
ORDER BY table_name;

