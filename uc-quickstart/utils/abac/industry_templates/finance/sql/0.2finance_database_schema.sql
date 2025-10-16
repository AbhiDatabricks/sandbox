-- =============================================
-- FINANCE DATABASE SCHEMA FOR DATABRICKS
-- Purpose: Financial services data for ABAC demonstration
-- Domain: Banking, Payments, Credit, Compliance
-- =============================================

USE CATALOG apscat;
CREATE SCHEMA IF NOT EXISTS finance
COMMENT 'Financial services data schema for ABAC demonstration';
USE SCHEMA finance;

-- =============================================
-- TABLE 1: CUSTOMERS (20 rows)
-- =============================================
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
  customer_id STRING NOT NULL,
  first_name STRING NOT NULL,
  last_name STRING NOT NULL,
  ssn STRING,
  date_of_birth DATE,
  email STRING,
  phone STRING,
  address STRING,
  city STRING,
  state STRING,
  zip_code STRING,
  annual_income DECIMAL(12,2),
  credit_score INT,
  customer_since DATE,
  CONSTRAINT pk_customers PRIMARY KEY (customer_id)
) USING DELTA
COMMENT 'Customer master data with PII';

INSERT INTO customers VALUES
('C-1001', 'John', 'Smith', '123-45-6789', '1985-03-15', 'john.smith@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001', 75000.00, 720, '2020-01-15'),
('C-1002', 'Sarah', 'Johnson', '234-56-7890', '1990-07-22', 'sarah.j@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001', 95000.00, 780, '2019-05-20'),
('C-1003', 'Michael', 'Williams', '345-67-8901', '1982-11-10', 'mwilliams@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601', 62000.00, 690, '2021-03-08'),
('C-1004', 'Emily', 'Brown', '456-78-9012', '1995-02-28', 'ebrown@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001', 58000.00, 710, '2020-09-12'),
('C-1005', 'David', 'Jones', '567-89-0123', '1988-06-18', 'djones@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 110000.00, 800, '2018-11-30'),
('C-1006', 'Jennifer', 'Garcia', '678-90-1234', '1992-09-05', 'jgarcia@email.com', '555-0106', '987 Cedar Ln', 'Philadelphia', 'PA', '19101', 72000.00, 740, '2019-07-15'),
('C-1007', 'Robert', 'Martinez', '789-01-2345', '1980-12-20', 'rmartinez@email.com', '555-0107', '147 Birch Way', 'San Antonio', 'TX', '78201', 85000.00, 760, '2020-02-28'),
('C-1008', 'Lisa', 'Rodriguez', '890-12-3456', '1987-04-12', 'lrodriguez@email.com', '555-0108', '258 Spruce Ct', 'San Diego', 'CA', '92101', 98000.00, 770, '2019-10-05'),
('C-1009', 'James', 'Wilson', '901-23-4567', '1993-08-25', 'jwilson@email.com', '555-0109', '369 Ash Blvd', 'Dallas', 'TX', '75201', 67000.00, 700, '2021-01-18'),
('C-1010', 'Maria', 'Anderson', '012-34-5678', '1986-05-30', 'manderson@email.com', '555-0110', '741 Willow Pl', 'San Jose', 'CA', '95101', 125000.00, 820, '2018-08-22'),
('C-1011', 'William', 'Thomas', '111-22-3333', '1991-10-08', 'wthomas@email.com', '555-0111', '852 Poplar Ave', 'Austin', 'TX', '78701', 78000.00, 730, '2020-06-10'),
('C-1012', 'Jessica', 'Taylor', '222-33-4444', '1984-01-14', 'jtaylor@email.com', '555-0112', '963 Cherry St', 'Jacksonville', 'FL', '32099', 88000.00, 750, '2019-12-03'),
('C-1013', 'Christopher', 'Moore', '333-44-5555', '1989-07-19', 'cmoore@email.com', '555-0113', '159 Hickory Dr', 'Fort Worth', 'TX', '76101', 71000.00, 720, '2020-11-25'),
('C-1014', 'Amanda', 'Jackson', '444-55-6666', '1994-03-22', 'ajackson@email.com', '555-0114', '357 Dogwood Ln', 'Columbus', 'OH', '43081', 64000.00, 710, '2021-04-08'),
('C-1015', 'Daniel', 'Martin', '555-66-7777', '1983-11-27', 'dmartin@email.com', '555-0115', '753 Magnolia Way', 'Charlotte', 'NC', '28201', 92000.00, 765, '2019-09-14'),
('C-1016', 'Ashley', 'Lee', '666-77-8888', '1996-06-03', 'alee@email.com', '555-0116', '951 Redwood Ct', 'San Francisco', 'CA', '94101', 135000.00, 810, '2018-05-20'),
('C-1017', 'Matthew', 'Perez', '777-88-9999', '1981-12-09', 'mperez@email.com', '555-0117', '246 Sycamore Blvd', 'Indianapolis', 'IN', '46201', 69000.00, 695, '2020-10-11'),
('C-1018', 'Michelle', 'Thompson', '888-99-0000', '1990-08-16', 'mthompson@email.com', '555-0118', '468 Beech Pl', 'Seattle', 'WA', '98101', 105000.00, 790, '2019-03-28'),
('C-1019', 'Joshua', 'White', '999-00-1111', '1987-02-21', 'jwhite@email.com', '555-0119', '680 Fir Ave', 'Denver', 'CO', '80201', 81000.00, 745, '2020-07-19'),
('C-1020', 'Stephanie', 'Harris', '000-11-2222', '1992-10-04', 'sharris@email.com', '555-0120', '802 Pine St', 'Boston', 'MA', '02101', 97000.00, 775, '2019-11-06');

-- =============================================
-- TABLE 2: ACCOUNTS (25 rows)
-- =============================================
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
  account_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  account_type STRING NOT NULL,
  account_number STRING NOT NULL,
  routing_number STRING,
  balance DECIMAL(15,2),
  opened_date DATE,
  status STRING,
  CONSTRAINT pk_accounts PRIMARY KEY (account_id)
) USING DELTA
COMMENT 'Bank accounts';

INSERT INTO accounts VALUES
('A-5001', 'C-1001', 'Checking', '1001234567', '021000021', 5420.50, '2020-01-15', 'Active'),
('A-5002', 'C-1001', 'Savings', '1001234568', '021000021', 15000.00, '2020-01-15', 'Active'),
('A-5003', 'C-1002', 'Checking', '1002345678', '121000248', 3250.75, '2019-05-20', 'Active'),
('A-5004', 'C-1002', 'Savings', '1002345679', '121000248', 28500.00, '2019-05-20', 'Active'),
('A-5005', 'C-1003', 'Checking', '1003456789', '071000013', 1875.25, '2021-03-08', 'Active'),
('A-5006', 'C-1004', 'Checking', '1004567890', '111000025', 4620.00, '2020-09-12', 'Active'),
('A-5007', 'C-1004', 'Savings', '1004567891', '111000025', 12300.00, '2020-09-12', 'Active'),
('A-5008', 'C-1005', 'Checking', '1005678901', '122100024', 8750.50, '2018-11-30', 'Active'),
('A-5009', 'C-1005', 'Savings', '1005678902', '122100024', 45600.00, '2018-11-30', 'Active'),
('A-5010', 'C-1006', 'Checking', '1006789012', '031100209', 2940.80, '2019-07-15', 'Active'),
('A-5011', 'C-1007', 'Checking', '1007890123', '111000025', 6180.25, '2020-02-28', 'Active'),
('A-5012', 'C-1007', 'Savings', '1007890124', '111000025', 21500.00, '2020-02-28', 'Active'),
('A-5013', 'C-1008', 'Checking', '1008901234', '121000248', 7325.60, '2019-10-05', 'Active'),
('A-5014', 'C-1009', 'Checking', '1009012345', '111000025', 3510.40, '2021-01-18', 'Active'),
('A-5015', 'C-1010', 'Checking', '1010123456', '121000248', 12400.75, '2018-08-22', 'Active'),
('A-5016', 'C-1010', 'Savings', '1010123457', '121000248', 67800.00, '2018-08-22', 'Active'),
('A-5017', 'C-1011', 'Checking', '1011234567', '111000025', 4890.30, '2020-06-10', 'Active'),
('A-5018', 'C-1012', 'Checking', '1012345678', '063100277', 5670.90, '2019-12-03', 'Active'),
('A-5019', 'C-1012', 'Savings', '1012345679', '063100277', 19200.00, '2019-12-03', 'Active'),
('A-5020', 'C-1013', 'Checking', '1013456789', '111000025', 3825.15, '2020-11-25', 'Active'),
('A-5021', 'C-1014', 'Checking', '1014567890', '044000037', 2950.60, '2021-04-08', 'Active'),
('A-5022', 'C-1015', 'Checking', '1015678901', '053000196', 7240.85, '2019-09-14', 'Active'),
('A-5023', 'C-1016', 'Checking', '1016789012', '121000248', 15600.40, '2018-05-20', 'Active'),
('A-5024', 'C-1017', 'Checking', '1017890123', '071000013', 3410.75, '2020-10-11', 'Active'),
('A-5025', 'C-1018', 'Checking', '1018901234', '125000024', 9850.20, '2019-03-28', 'Active');

-- Verify table creation
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'accounts', COUNT(*) FROM accounts
ORDER BY table_name;

