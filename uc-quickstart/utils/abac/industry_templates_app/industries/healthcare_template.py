"""
Healthcare Industry ABAC Template
"""

INDUSTRY_NAME = "Healthcare"
INDUSTRY_DESCRIPTION = "Healthcare/medical data protection with HIPAA compliance"

FUNCTIONS_SQL = """

CREATE OR REPLACE FUNCTION mask_string_partial(input STRING)
RETURNS STRING
COMMENT 'ABAC utility: Partial string masking showing first and last characters'
RETURN CASE 
    WHEN input IS NULL OR input = '' THEN input
    WHEN LENGTH(input) <= 2 THEN REPEAT('*', LENGTH(input))
    WHEN LENGTH(input) = 3 THEN CONCAT(LEFT(input, 1), '*', RIGHT(input, 1))
    ELSE CONCAT(LEFT(input, 1), REPEAT('*', LENGTH(input) - 2), RIGHT(input, 1))
END;

CREATE OR REPLACE FUNCTION mask_policy_number_last4(policy STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Mask policy number showing last 4 digits'
RETURN CASE 
  WHEN policy IS NULL THEN policy 
  ELSE CONCAT('****', RIGHT(policy, 4)) 
END;

CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask email local part while preserving domain'
RETURN CASE 
    WHEN email IS NULL OR email = '' THEN email
    WHEN LOCATE('@', email) > 0 THEN 
        CONCAT('****', SUBSTRING(email, LOCATE('@', email)))
    ELSE '****'
END;

CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask phone numbers while preserving format structure'
RETURN CASE 
    WHEN phone IS NULL OR phone = '' THEN phone
    WHEN LENGTH(phone) >= 4 THEN 
        CONCAT(REPEAT('X', LENGTH(phone) - 4), RIGHT(phone, 4))
    ELSE REPEAT('X', LENGTH(phone))
END;

CREATE OR REPLACE FUNCTION mask_string_hash(input STRING)
RETURNS STRING
COMMENT 'ABAC utility: One-way hash masking using SHA-256 for complete anonymization'
RETURN sha2(input, 256);

CREATE OR REPLACE FUNCTION mask_date_year_only(input_date DATE)
RETURNS DATE
COMMENT 'ABAC utility: Mask date to show only year (January 1st of same year)'
RETURN CASE 
    WHEN input_date IS NULL THEN NULL
    ELSE DATE(CONCAT(YEAR(input_date), '-01-01'))
END;

CREATE OR REPLACE FUNCTION mask_address_city_state(address STRING, city STRING, state STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask street address, show only city and state'
RETURN CASE 
    WHEN city IS NULL AND state IS NULL THEN '***'
    WHEN city IS NULL THEN state
    WHEN state IS NULL THEN city
    ELSE CONCAT(city, ', ', state)
END;

CREATE OR REPLACE FUNCTION mask_for_all_roles(id DECIMAL)
RETURNS DECIMAL
COMMENT 'ABAC utility: Completely mask numeric values by returning NULL'
RETURN NULL;

CREATE OR REPLACE FUNCTION business_hours_filter()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours (9 AM - 6 PM Melbourne time)'
RETURN hour(from_utc_timestamp(current_timestamp(), 'Australia/Melbourne')) BETWEEN 9 AND 18;

CREATE OR REPLACE FUNCTION no_rows()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Returns FALSE to filter out all rows for complete data hiding'
RETURN FALSE;

CREATE OR REPLACE FUNCTION filter_by_region(region STRING)
RETURNS BOOLEAN
COMMENT 'ABAC utility: Filter data by user region'
RETURN region = 'North';

"""

TAG_DEFINITIONS = [
    ("pii_type_healthcare", "Healthcare PII data types", [
        "patient_name", "patient_id", "ssn", "dob", "email", "phone",
        "address", "medical_record_number", "diagnosis", "treatment"
    ]),
    ("phi_level_healthcare", "Protected Health Information level", [
        "High", "Medium", "Low", "Public"
    ]),
    ("hipaa_compliance_healthcare", "HIPAA compliance requirement", [
        "Required", "Not_Required"
    ]),
    ("data_sensitivity_healthcare", "Data sensitivity classification", [
        "Highly_Sensitive", "Sensitive", "Internal", "Public"
    ]),
    ("shift_hours_healthcare", "Time-based access control (Standard_Business=8AM-6PM)", [
        "Standard_Business", "Extended_Hours", "Night_Shift", "Emergency_24x7"
    ])
]

ABAC_POLICIES_SQL = """
-- POLICY 1: Patient ID Masking for Cross-Table Analytics
CREATE OR REPLACE POLICY healthcare_patient_id_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_string_hash
TO `account users`
FOR TABLES
MATCH COLUMNS 
    hasTagValue('pii_type_healthcare', 'patient_id') AND hasTagValue('phi_level_healthcare', 'High') AS patient_id_cols
ON COLUMN patient_id_cols;

-- POLICY 2: Business Hours Access for Lab Data
CREATE OR REPLACE POLICY healthcare_business_hours_filter
ON SCHEMA {CATALOG}.{SCHEMA}
ROW FILTER {CATALOG}.{SCHEMA}.business_hours_filter
TO `account users`
FOR TABLES
WHEN hasTagValue('shift_hours_healthcare', 'Standard_Business');

-- POLICY 3: Partial Name Masking for Privacy
CREATE OR REPLACE POLICY healthcare_name_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_string_partial
TO `account users`
FOR TABLES
MATCH COLUMNS 
    hasTagValue('pii_type_healthcare', 'patient_name') AS name_cols
ON COLUMN name_cols;

-- POLICY 4: Email Masking
CREATE OR REPLACE POLICY healthcare_email_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email
TO `account users`
FOR TABLES
MATCH COLUMNS 
    hasTagValue('data_sensitivity_healthcare', 'Internal') AND hasTagValue('pii_type_healthcare', 'email') AS email_cols
ON COLUMN email_cols;

-- POLICY 5: Phone Number Masking
CREATE OR REPLACE POLICY healthcare_phone_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone
TO `account users`
FOR TABLES
MATCH COLUMNS 
    hasTagValue('data_sensitivity_healthcare', 'Sensitive') AND hasTagValue('pii_type_healthcare', 'phone') AS phone_cols
ON COLUMN phone_cols;

-- POLICY 6: Insurance Number Masking
CREATE OR REPLACE POLICY healthcare_insurance_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_policy_number_last4
TO `account users`
FOR TABLES
MATCH COLUMNS 
    hasTagValue('data_sensitivity_healthcare', 'Sensitive') AND hasTagValue('phi_level_healthcare', 'Medium') AS insurance_cols
ON COLUMN insurance_cols;

-- POLICY 7: Age Group Masking for Research
CREATE OR REPLACE POLICY healthcare_age_group_masking
ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_date_year_only
TO `account users`
FOR TABLES
MATCH COLUMNS 
    hasTagValue('pii_type_healthcare', 'dob') AND hasTagValue('phi_level_healthcare', 'High') AS dob_cols
ON COLUMN dob_cols;

"""

TEST_TABLES_SQL = """

CREATE TABLE IF NOT EXISTS patients_test (
    PatientID STRING NOT NULL,
    FirstName STRING NOT NULL,
    LastName STRING NOT NULL,
    DateOfBirth DATE NOT NULL,
    Gender STRING NOT NULL,
    PhoneNumber STRING,
    Email STRING,
    Address STRING,
    City STRING,
    State STRING,
    ZipCode STRING,
    EmergencyContact STRING,
    EmergencyPhone STRING,
    BloodType STRING,
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_patients PRIMARY KEY (PatientID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Patient demographics and contact information for healthcare system';
INSERT INTO patients_test VALUES
('PAT001', 'John', 'Smith', '1975-03-15', 'Male', '122-555-0101', 'john.smith@email.com', '123 Main St', 'Seattle', 'WA', '98101', 'Jane Smith', '121-555-0102', 'O+', '2024-01-01 10:00:00'),
('PAT002', 'Sarah', 'Johnson', '1982-07-22', 'Female', '220-555-0201', 'sarah.j@email.com', '456 Oak Ave', 'Portland', 'OR', '97201', 'Mike Johnson', '599-555-0202', 'A+', '2024-01-02 11:00:00'),
('PAT003', 'Michael', 'Brown', '1990-11-08', 'Male', '508-555-0301', 'mbrown@email.com', '789 Pine St', 'San Francisco', 'CA', '94101', 'Lisa Brown', '392-555-0302', 'B+', '2024-01-03 12:00:00'),
('PAT004', 'Emily', 'Davis', '1988-05-12', 'Female', '502-555-0401', 'emily.davis@email.com', '321 Elm St', 'Los Angeles', 'CA', '90210', 'Tom Davis', '445-555-0402', 'AB+', '2024-01-04 13:00:00'),
('PAT005', 'David', 'Wilson', '1965-09-30', 'Male', '140-555-0501', 'dwilson@email.com', '654 Maple Dr', 'Phoenix', 'AZ', '85001', 'Carol Wilson', '808-555-0502', 'O-', '2024-01-05 14:00:00'),
('PAT006', 'Jennifer', 'Martinez', '1993-12-18', 'Female', '252-555-0601', 'jmartinez@email.com', '987 Cedar Ln', 'Denver', 'CO', '80201', 'Carlos Martinez', '439-555-0602', 'A-', '2024-01-06 15:00:00'),
('PAT007', 'Robert', 'Anderson', '1978-04-25', 'Male', '999-555-0701', 'randerson@email.com', '147 Birch Ave', 'Austin', 'TX', '73301', 'Mary Anderson', '472-555-0702', 'B-', '2024-01-07 16:00:00'),
('PAT008', 'Lisa', 'Taylor', '1985-08-14', 'Female', '484-555-0801', 'ltaylor@email.com', '258 Spruce St', 'Miami', 'FL', '33101', 'John Taylor', '765-555-0802', 'AB-', '2024-01-08 17:00:00'),
('PAT009', 'Christopher', 'Thomas', '1972-01-07', 'Male', '743-555-0901', 'cthomas@email.com', '369 Willow Rd', 'Chicago', 'IL', '60601', 'Susan Thomas', '292-555-0902', 'O+', '2024-01-09 18:00:00'),
('PAT010', 'Amanda', 'Jackson', '1991-06-03', 'Female', '985-555-1001', 'ajackson@email.com', '741 Aspen Ct', 'Boston', 'MA', '02101', 'James Jackson', '733-555-1002', 'A+', '2024-01-10 19:00:00'),
('PAT011', 'Kevin', 'White', '1987-10-16', 'Male', '492-555-1101', 'kwhite@email.com', '852 Poplar St', 'Atlanta', 'GA', '30301', 'Linda White', '555-1102', 'B+', '2024-01-11 20:00:00'),
('PAT012', 'Michelle', 'Harris', '1979-02-28', 'Female', '111-555-1201', 'mharris@email.com', '963 Hickory Ave', 'Dallas', 'TX', '75201', 'Paul Harris', '717-555-1202', 'AB+', '2024-01-12 21:00:00'),
('PAT013', 'Daniel', 'Martin', '1983-12-11', 'Male', '482-555-1301', 'dmartin@email.com', '159 Walnut Dr', 'Nashville', 'TN', '37201', 'Nancy Martin', '249-555-1302', 'O-', '2024-01-13 22:00:00'),
('PAT014', 'Rachel', 'Thompson', '1995-05-29', 'Female', '188-555-1401', 'rthompson@email.com', '357 Cherry Ln', 'Las Vegas', 'NV', '89101', 'Steve Thompson', '550-555-1402', 'A-', '2024-01-14 23:00:00'),
('PAT015', 'Matthew', 'Garcia', '1974-09-02', 'Male', '363-555-1501', 'mgarcia@email.com', '486 Dogwood Ct', 'San Diego', 'CA', '92101', 'Maria Garcia', '332-555-1502', 'B-', '2024-01-15 08:00:00'),
('PAT016', 'Jessica', 'Rodriguez', '1989-07-19', 'Female', '592-555-1601', 'jrodriguez@email.com', '729 Magnolia St', 'Tampa', 'FL', '33601', 'Luis Rodriguez', '915-555-1602', 'AB-', '2024-01-16 09:00:00'),
('PAT017', 'Andrew', 'Lewis', '1976-03-06', 'Male', '202-555-1701', 'alewis@email.com', '618 Sycamore Ave', 'Minneapolis', 'MN', '55401', 'Beth Lewis', '310-555-1702', 'O+', '2024-01-17 10:00:00'),
('PAT018', 'Nicole', 'Lee', '1992-11-23', 'Female', '918-555-1801', 'nlee@email.com', '507 Redwood Dr', 'Portland', 'OR', '97202', 'Kevin Lee', '215-555-1802', 'A+', '2024-01-18 11:00:00'),
('PAT019', 'Joshua', 'Walker', '1981-08-08', 'Male', '301-555-1901', 'jwalker@email.com', '394 Fir St', 'Salt Lake City', 'UT', '84101', 'Amy Walker', '730-555-1902', 'B+', '2024-01-19 12:00:00'),
('PAT020', 'Stephanie', 'Hall', '1986-04-17', 'Female', '395-555-2001', 'shall@email.com', '283 Palm Ave', 'Sacramento', 'CA', '95814', 'Greg Hall', '645-555-2002', 'AB+', '2024-01-20 13:00:00');

CREATE TABLE IF NOT EXISTS providers_test (
    ProviderID STRING NOT NULL,
    FirstName STRING NOT NULL,
    LastName STRING NOT NULL,
    Specialty STRING NOT NULL,
    LicenseNumber STRING NOT NULL,
    PhoneNumber STRING,
    Email STRING,
    Department STRING,
    HireDate DATE,
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_providers PRIMARY KEY (ProviderID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Healthcare providers including doctors, nurses, and specialists';
INSERT INTO providers_test VALUES
('PRV001', 'Dr. William', 'Chen', 'Cardiology', 'LIC001234', '112-555-9001', 'w.chen@hospital.com', 'Cardiology', '2020-01-15', TRUE, '2024-01-01 10:00:00'),
('PRV002', 'Dr. Maria', 'Rodriguez', 'Internal Medicine', 'LIC002345', '392-555-9002', 'm.rodriguez@hospital.com', 'Internal Medicine', '2019-03-22', TRUE, '2024-01-02 11:00:00'),
('PRV003', 'Dr. James', 'Thompson', 'Emergency Medicine', 'LIC003456', '630-555-9003', 'j.thompson@hospital.com', 'Emergency', '2021-06-10', TRUE, '2024-01-03 12:00:00'),
('PRV004', 'Dr. Sarah', 'Kim', 'Pediatrics', 'LIC004567', '333-555-9004', 's.kim@hospital.com', 'Pediatrics', '2018-09-08', TRUE, '2024-01-04 13:00:00'),
('PRV005', 'Dr. Robert', 'Johnson', 'Orthopedics', 'LIC005678', '499-555-9005', 'r.johnson@hospital.com', 'Orthopedics', '2017-11-12', TRUE, '2024-01-05 14:00:00'),
('PRV006', 'Dr. Lisa', 'Davis', 'Dermatology', 'LIC006789', '310-555-9006', 'l.davis@hospital.com', 'Dermatology', '2022-02-28', TRUE, '2024-01-06 15:00:00'),
('PRV007', 'Dr. Michael', 'Wilson', 'Neurology', 'LIC007890', '222-555-9007', 'm.wilson@hospital.com', 'Neurology', '2019-07-14', TRUE, '2024-01-07 16:00:00'),
('PRV008', 'Dr. Jennifer', 'Brown', 'Oncology', 'LIC008901', '998-555-9008', 'j.brown@hospital.com', 'Oncology', '2020-05-03', TRUE, '2024-01-08 17:00:00'),
('PRV009', 'Dr. David', 'Miller', 'Psychiatry', 'LIC009012', '464-555-9009', 'd.miller@hospital.com', 'Psychiatry', '2021-10-17', TRUE, '2024-01-09 18:00:00'),
('PRV010', 'Dr. Amanda', 'Garcia', 'Gynecology', 'LIC010123', '332-555-9010', 'a.garcia@hospital.com', 'Gynecology', '2018-12-05', TRUE, '2024-01-10 19:00:00'),
('PRV011', 'Dr. Christopher', 'Martinez', 'Radiology', 'LIC011234', '892-555-9011', 'c.martinez@hospital.com', 'Radiology', '2019-04-21', TRUE, '2024-01-11 20:00:00'),
('PRV012', 'Dr. Emily', 'Anderson', 'Anesthesiology', 'LIC012345', '283-555-9012', 'e.anderson@hospital.com', 'Anesthesiology', '2020-08-30', TRUE, '2024-01-12 21:00:00'),
('PRV013', 'Dr. Kevin', 'Taylor', 'Pulmonology', 'LIC013456', '176-555-9013', 'k.taylor@hospital.com', 'Pulmonology', '2017-01-18', TRUE, '2024-01-13 22:00:00'),
('PRV014', 'Dr. Rachel', 'Thomas', 'Endocrinology', 'LIC014567', '520-555-9014', 'r.thomas@hospital.com', 'Endocrinology', '2022-03-12', TRUE, '2024-01-14 23:00:00'),
('PRV015', 'Dr. Matthew', 'Jackson', 'Gastroenterology', 'LIC015678', '348-555-9015', 'm.jackson@hospital.com', 'Gastroenterology', '2018-06-27', TRUE, '2024-01-15 08:00:00'),
('PRV016', 'Dr. Jessica', 'White', 'Nephrology', 'LIC016789', '762-555-9016', 'j.white@hospital.com', 'Nephrology', '2021-09-14', TRUE, '2024-01-16 09:00:00'),
('PRV017', 'Dr. Andrew', 'Harris', 'Urology', 'LIC017890', '198-555-9017', 'a.harris@hospital.com', 'Urology', '2019-12-08', TRUE, '2024-01-17 10:00:00'),
('PRV018', 'Dr. Nicole', 'Martin', 'Rheumatology', 'LIC018901', '377-555-9018', 'n.martin@hospital.com', 'Rheumatology', '2020-11-23', TRUE, '2024-01-18 11:00:00'),
('PRV019', 'Dr. Joshua', 'Lee', 'Infectious Disease', 'LIC019012', '409-555-9019', 'j.lee@hospital.com', 'Internal Medicine', '2018-04-06', TRUE, '2024-01-19 12:00:00'),
('PRV020', 'Dr. Stephanie', 'Walker', 'Family Medicine', 'LIC020123', '187-555-9020', 's.walker@hospital.com', 'Family Medicine', '2022-07-19', TRUE, '2024-01-20 13:00:00');

CREATE TABLE IF NOT EXISTS insurance_test (
    InsuranceID STRING NOT NULL,
    PatientID STRING NOT NULL,
    InsuranceCompany STRING NOT NULL,
    PolicyNumber STRING NOT NULL,
    GroupNumber STRING,
    PlanType STRING NOT NULL,
    CoverageStartDate DATE NOT NULL,
    CoverageEndDate DATE,
    Deductible DECIMAL(10,2),
    CoPayAmount DECIMAL(10,2),
    IsActive BOOLEAN DEFAULT TRUE,
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_insurance PRIMARY KEY (InsuranceID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Patient insurance coverage information and policy details';
INSERT INTO insurance_test VALUES
('INS001', 'PAT001', 'Blue Cross Blue Shield', 'BCBS001234567', 'GRP001', 'PPO', '2024-01-01', '2024-12-31', 1500.00, 25.00, TRUE, '2024-01-01 10:00:00'),
('INS002', 'PAT002', 'Aetna', 'AET002345678', 'GRP002', 'HMO', '2024-01-01', '2024-12-31', 2000.00, 30.00, TRUE, '2024-01-02 11:00:00'),
('INS003', 'PAT003', 'Cigna', 'CIG003456789', 'GRP003', 'PPO', '2024-01-01', '2024-12-31', 1000.00, 20.00, TRUE, '2024-01-03 12:00:00'),
('INS004', 'PAT004', 'UnitedHealth', 'UHC004567890', 'GRP004', 'EPO', '2024-01-01', '2024-12-31', 2500.00, 35.00, TRUE, '2024-01-04 13:00:00'),
('INS005', 'PAT005', 'Kaiser Permanente', 'KP005678901', 'GRP005', 'HMO', '2024-01-01', '2024-12-31', 1200.00, 15.00, TRUE, '2024-01-05 14:00:00'),
('INS006', 'PAT006', 'Humana', 'HUM006789012', 'GRP006', 'PPO', '2024-01-01', '2024-12-31', 1800.00, 25.00, TRUE, '2024-01-06 15:00:00'),
('INS007', 'PAT007', 'Blue Cross Blue Shield', 'BCBS007890123', 'GRP007', 'HMO', '2024-01-01', '2024-12-31', 1600.00, 20.00, TRUE, '2024-01-07 16:00:00'),
('INS008', 'PAT008', 'Aetna', 'AET008901234', 'GRP008', 'PPO', '2024-01-01', '2024-12-31', 2200.00, 30.00, TRUE, '2024-01-08 17:00:00'),
('INS009', 'PAT009', 'Cigna', 'CIG009012345', 'GRP009', 'EPO', '2024-01-01', '2024-12-31', 1400.00, 25.00, TRUE, '2024-01-09 18:00:00'),
('INS010', 'PAT010', 'UnitedHealth', 'UHC010123456', 'GRP010', 'PPO', '2024-01-01', '2024-12-31', 1900.00, 35.00, TRUE, '2024-01-10 19:00:00'),
('INS011', 'PAT011', 'Kaiser Permanente', 'KP011234567', 'GRP011', 'HMO', '2024-01-01', '2024-12-31', 1300.00, 15.00, TRUE, '2024-01-11 20:00:00'),
('INS012', 'PAT012', 'Humana', 'HUM012345678', 'GRP012', 'PPO', '2024-01-01', '2024-12-31', 2100.00, 25.00, TRUE, '2024-01-12 21:00:00'),
('INS013', 'PAT013', 'Blue Cross Blue Shield', 'BCBS013456789', 'GRP013', 'HMO', '2024-01-01', '2024-12-31', 1700.00, 20.00, TRUE, '2024-01-13 22:00:00'),
('INS014', 'PAT014', 'Aetna', 'AET014567890', 'GRP014', 'EPO', '2024-01-01', '2024-12-31', 2300.00, 30.00, TRUE, '2024-01-14 23:00:00'),
('INS015', 'PAT015', 'Cigna', 'CIG015678901', 'GRP015', 'PPO', '2024-01-01', '2024-12-31', 1500.00, 25.00, TRUE, '2024-01-15 08:00:00'),
('INS016', 'PAT016', 'UnitedHealth', 'UHC016789012', 'GRP016', 'HMO', '2024-01-01', '2024-12-31', 2000.00, 35.00, TRUE, '2024-01-16 09:00:00'),
('INS017', 'PAT017', 'Kaiser Permanente', 'KP017890123', 'GRP017', 'PPO', '2024-01-01', '2024-12-31', 1100.00, 15.00, TRUE, '2024-01-17 10:00:00'),
('INS018', 'PAT018', 'Humana', 'HUM018901234', 'GRP018', 'EPO', '2024-01-01', '2024-12-31', 2400.00, 25.00, TRUE, '2024-01-18 11:00:00'),
('INS019', 'PAT019', 'Blue Cross Blue Shield', 'BCBS019012345', 'GRP019', 'HMO', '2024-01-01', '2024-12-31', 1800.00, 20.00, TRUE, '2024-01-19 12:00:00'),
('INS020', 'PAT020', 'Aetna', 'AET020123456', 'GRP020', 'PPO', '2024-01-01', '2024-12-31', 2600.00, 30.00, TRUE, '2024-01-20 13:00:00');


CREATE TABLE IF NOT EXISTS visits_test (
    VisitID STRING NOT NULL,
    PatientID STRING NOT NULL,
    ProviderID STRING NOT NULL,
    VisitDate DATE NOT NULL,
    VisitTime TIMESTAMP NOT NULL,
    VisitType STRING NOT NULL,
    ChiefComplaint STRING,
    Diagnosis STRING,
    TreatmentPlan STRING,
    VisitStatus STRING NOT NULL,
    Duration INT, -- in minutes
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_visits PRIMARY KEY (VisitID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Patient visits, appointments, and medical encounters';
INSERT INTO visits_test VALUES
('VIS001', 'PAT001', 'PRV001', '2024-02-15', '2024-02-15 09:00:00', 'Routine Checkup', 'Annual physical exam', 'Hypertension', 'Continue current medication, follow-up in 3 months', 'Completed', 45, '2024-02-15 09:00:00'),
('VIS002', 'PAT002', 'PRV002', '2024-02-16', '2024-02-16 10:30:00', 'Follow-up', 'Diabetes management', 'Type 2 Diabetes', 'Adjust insulin dosage, dietary counseling', 'Completed', 30, '2024-02-16 10:30:00'),
('VIS003', 'PAT003', 'PRV003', '2024-02-17', '2024-02-17 14:15:00', 'Emergency', 'Chest pain', 'Acute myocardial infarction', 'Emergency cardiac intervention', 'Completed', 120, '2024-02-17 14:15:00'),
('VIS004', 'PAT004', 'PRV004', '2024-02-18', '2024-02-18 11:00:00', 'Well-child Visit', 'Routine pediatric checkup', 'Normal development', 'Immunizations up to date, next visit in 6 months', 'Completed', 25, '2024-02-18 11:00:00'),
('VIS005', 'PAT005', 'PRV005', '2024-02-19', '2024-02-19 15:45:00', 'Consultation', 'Knee pain', 'Osteoarthritis', 'Physical therapy, pain management', 'Completed', 40, '2024-02-19 15:45:00'),
('VIS006', 'PAT006', 'PRV006', '2024-02-20', '2024-02-20 13:20:00', 'Routine Checkup', 'Skin lesion evaluation', 'Benign mole', 'Monitor for changes, annual skin check', 'Completed', 20, '2024-02-20 13:20:00'),
('VIS007', 'PAT007', 'PRV007', '2024-02-21', '2024-02-21 16:00:00', 'Consultation', 'Headaches', 'Migraine', 'Prescribed medication, lifestyle modifications', 'Completed', 35, '2024-02-21 16:00:00'),
('VIS008', 'PAT008', 'PRV008', '2024-02-22', '2024-02-22 10:15:00', 'Follow-up', 'Cancer treatment monitoring', 'Breast cancer remission', 'Continue surveillance, next scan in 3 months', 'Completed', 50, '2024-02-22 10:15:00'),
('VIS009', 'PAT009', 'PRV009', '2024-02-23', '2024-02-23 12:30:00', 'Initial Consultation', 'Depression screening', 'Major depressive disorder', 'Start antidepressant therapy, counseling referral', 'Completed', 60, '2024-02-23 12:30:00'),
('VIS010', 'PAT010', 'PRV010', '2024-02-24', '2024-02-24 14:45:00', 'Annual Exam', 'Gynecological exam', 'Normal findings', 'Continue routine screening, next visit in 1 year', 'Completed', 30, '2024-02-24 14:45:00'),
('VIS011', 'PAT011', 'PRV011', '2024-02-25', '2024-02-25 08:30:00', 'Imaging', 'Abdominal pain', 'Gallstones', 'Schedule surgery consultation', 'Completed', 15, '2024-02-25 08:30:00'),
('VIS012', 'PAT012', 'PRV012', '2024-02-26', '2024-02-26 07:00:00', 'Pre-operative', 'Pre-surgery evaluation', 'Cleared for surgery', 'Anesthesia plan reviewed', 'Completed', 20, '2024-02-26 07:00:00'),
('VIS013', 'PAT013', 'PRV013', '2024-02-27', '2024-02-27 11:15:00', 'Consultation', 'Shortness of breath', 'Asthma', 'Inhaler therapy, avoid triggers', 'Completed', 35, '2024-02-27 11:15:00'),
('VIS014', 'PAT014', 'PRV014', '2024-02-28', '2024-02-28 15:30:00', 'Follow-up', 'Thyroid function', 'Hypothyroidism', 'Increase levothyroxine dose', 'Completed', 25, '2024-02-28 15:30:00'),
('VIS015', 'PAT015', 'PRV015', '2024-03-01', '2024-03-01 09:45:00', 'Consultation', 'Stomach pain', 'Gastritis', 'Proton pump inhibitor therapy', 'Completed', 30, '2024-03-01 09:45:00'),
('VIS016', 'PAT016', 'PRV016', '2024-03-02', '2024-03-02 13:00:00', 'Routine Checkup', 'Kidney function monitoring', 'Chronic kidney disease stage 3', 'Continue current treatment', 'Completed', 40, '2024-03-02 13:00:00'),
('VIS017', 'PAT017', 'PRV017', '2024-03-03', '2024-03-03 16:15:00', 'Consultation', 'Urinary symptoms', 'Benign prostatic hyperplasia', 'Medication therapy', 'Completed', 25, '2024-03-03 16:15:00'),
('VIS018', 'PAT018', 'PRV018', '2024-03-04', '2024-03-04 10:00:00', 'Follow-up', 'Joint pain', 'Rheumatoid arthritis', 'Continue DMARD therapy', 'Completed', 35, '2024-03-04 10:00:00'),
('VIS019', 'PAT019', 'PRV019', '2024-03-05', '2024-03-05 14:30:00', 'Consultation', 'Fever and fatigue', 'Viral syndrome', 'Supportive care, rest', 'Completed', 20, '2024-03-05 14:30:00'),
('VIS020', 'PAT020', 'PRV020', '2024-03-06', '2024-03-06 11:45:00', 'Annual Physical', 'Routine health maintenance', 'Healthy', 'Continue current lifestyle', 'Completed', 45, '2024-03-06 11:45:00'),
('VIS021', 'PAT001', 'PRV002', '2024-03-15', '2024-03-15 10:00:00', 'Follow-up', 'Blood pressure check', 'Controlled hypertension', 'Continue medication', 'Completed', 15, '2024-03-15 10:00:00'),
('VIS022', 'PAT003', 'PRV001', '2024-03-20', '2024-03-20 14:30:00', 'Cardiac Follow-up', 'Post-MI care', 'Recovering well', 'Cardiac rehabilitation', 'Completed', 30, '2024-03-20 14:30:00');


CREATE TABLE IF NOT EXISTS lab_results_test (
    LabResultID STRING NOT NULL,
    VisitID STRING NOT NULL,
    PatientID STRING NOT NULL,
    TestName STRING NOT NULL,
    TestCode STRING,
    ResultValue STRING NOT NULL,
    ReferenceRange STRING,
    Units STRING,
    AbnormalFlag STRING,
    TestDate DATE NOT NULL,
    ResultDate DATE NOT NULL,
    LabTechnician STRING,
    Status STRING DEFAULT 'Final',
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_lab_results PRIMARY KEY (LabResultID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Laboratory test results and diagnostic data';
INSERT INTO lab_results_test VALUES
('LAB001', 'VIS001', 'PAT001', 'Total Cholesterol', 'CHOL', '220', '150-200', 'mg/dL', 'High', '2024-02-15', '2024-02-16', 'Tech001', 'Final', '2024-02-16 08:00:00'),
('LAB002', 'VIS001', 'PAT001', 'HDL Cholesterol', 'HDL', '45', '>40', 'mg/dL', 'Normal', '2024-02-15', '2024-02-16', 'Tech001', 'Final', '2024-02-16 08:00:00'),
('LAB003', 'VIS001', 'PAT001', 'LDL Cholesterol', 'LDL', '145', '<100', 'mg/dL', 'High', '2024-02-15', '2024-02-16', 'Tech001', 'Final', '2024-02-16 08:00:00'),
('LAB004', 'VIS002', 'PAT002', 'Hemoglobin A1c', 'HBA1C', '8.2', '4.0-6.0', '%', 'High', '2024-02-16', '2024-02-17', 'Tech002', 'Final', '2024-02-17 09:00:00'),
('LAB005', 'VIS002', 'PAT002', 'Fasting Glucose', 'GLUC', '180', '70-99', 'mg/dL', 'High', '2024-02-16', '2024-02-17', 'Tech002', 'Final', '2024-02-17 09:00:00'),
('LAB006', 'VIS003', 'PAT003', 'Troponin I', 'TROP', '12.5', '<0.04', 'ng/mL', 'High', '2024-02-17', '2024-02-17', 'Tech003', 'Final', '2024-02-17 16:00:00'),
('LAB007', 'VIS003', 'PAT003', 'CK-MB', 'CKMB', '45', '0-6.3', 'ng/mL', 'High', '2024-02-17', '2024-02-17', 'Tech003', 'Final', '2024-02-17 16:00:00'),
('LAB008', 'VIS005', 'PAT005', 'C-Reactive Protein', 'CRP', '8.5', '<3.0', 'mg/L', 'High', '2024-02-19', '2024-02-20', 'Tech004', 'Final', '2024-02-20 10:00:00'),
('LAB009', 'VIS005', 'PAT005', 'ESR', 'ESR', '65', '0-22', 'mm/hr', 'High', '2024-02-19', '2024-02-20', 'Tech004', 'Final', '2024-02-20 10:00:00'),
('LAB010', 'VIS008', 'PAT008', 'CA 15-3', 'CA153', '18', '<31.3', 'U/mL', 'Normal', '2024-02-22', '2024-02-23', 'Tech005', 'Final', '2024-02-23 11:00:00');


CREATE TABLE IF NOT EXISTS prescriptions_test (
    PrescriptionID STRING NOT NULL,
    VisitID STRING NOT NULL,
    PatientID STRING NOT NULL,
    ProviderID STRING NOT NULL,
    MedicationName STRING NOT NULL,
    GenericName STRING,
    Dosage STRING NOT NULL,
    Frequency STRING NOT NULL,
    Quantity INT NOT NULL,
    Refills INT DEFAULT 0,
    PrescriptionDate DATE NOT NULL,
    Instructions STRING,
    Status STRING DEFAULT 'Active',
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_prescriptions PRIMARY KEY (PrescriptionID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Medication prescriptions and pharmaceutical orders';
INSERT INTO prescriptions_test VALUES
('RX001', 'VIS001', 'PAT001', 'PRV001', 'Lisinopril', 'Lisinopril', '10mg', 'Once daily', 30, 3, '2024-02-15', 'Take with or without food', 'Active', '2024-02-15 09:30:00'),
('RX002', 'VIS001', 'PAT001', 'PRV001', 'Atorvastatin', 'Atorvastatin', '20mg', 'Once daily at bedtime', 30, 3, '2024-02-15', 'Take at bedtime', 'Active', '2024-02-15 09:30:00'),
('RX003', 'VIS002', 'PAT002', 'PRV002', 'Metformin', 'Metformin', '500mg', 'Twice daily', 60, 5, '2024-02-16', 'Take with meals', 'Active', '2024-02-16 10:45:00'),
('RX004', 'VIS002', 'PAT002', 'PRV002', 'Insulin Glargine', 'Insulin Glargine', '20 units', 'Once daily at bedtime', 1, 2, '2024-02-16', 'Inject subcutaneously', 'Active', '2024-02-16 10:45:00'),
('RX005', 'VIS003', 'PAT003', 'PRV003', 'Aspirin', 'Aspirin', '81mg', 'Once daily', 30, 3, '2024-02-17', 'Take with food', 'Active', '2024-02-17 15:00:00');

CREATE TABLE IF NOT EXISTS billing_test (
    BillID STRING NOT NULL,
    PatientID STRING NOT NULL,
    VisitID STRING NOT NULL,
    ServiceDate DATE NOT NULL,
    ServiceCode STRING NOT NULL,
    ServiceDescription STRING NOT NULL,
    ChargeAmount DECIMAL(10,2) NOT NULL,
    InsurancePaid DECIMAL(10,2) DEFAULT 0.00,
    PatientPaid DECIMAL(10,2) DEFAULT 0.00,
    BalanceDue DECIMAL(10,2) NOT NULL,
    BillingStatus STRING DEFAULT 'Pending',
    BillingDate DATE NOT NULL,
    PaymentDueDate DATE,
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT pk_billing PRIMARY KEY (BillID)
) USING DELTA
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported')
COMMENT 'Billing information, charges, and payment tracking';
INSERT INTO billing_test VALUES
('BILL001', 'PAT001', 'VIS001', '2024-02-15', '99213', 'Office visit, established patient, level 3', 250.00, 200.00, 25.00, 25.00, 'Partial Payment', '2024-02-16', '2024-03-16', '2024-02-16 10:00:00'),
('BILL002', 'PAT002', 'VIS002', '2024-02-16', '99214', 'Office visit, established patient, level 4', 350.00, 280.00, 30.00, 40.00, 'Partial Payment', '2024-02-17', '2024-03-17', '2024-02-17 11:00:00'),
('BILL003', 'PAT003', 'VIS003', '2024-02-17', '99281', 'Emergency department visit, level 1', 1500.00, 1200.00, 0.00, 300.00, 'Pending', '2024-02-18', '2024-03-18', '2024-02-18 12:00:00'),
('BILL004', 'PAT004', 'VIS004', '2024-02-18', '99382', 'Preventive medicine, new patient, 1-4 years', 200.00, 160.00, 15.00, 25.00, 'Partial Payment', '2024-02-19', '2024-03-19', '2024-02-19 13:00:00'),
('BILL005', 'PAT005', 'VIS005', '2024-02-19', '99243', 'Office consultation, level 3', 400.00, 320.00, 35.00, 45.00, 'Partial Payment', '2024-02-20', '2024-03-20', '2024-02-20 14:00:00');

"""

TAG_APPLICATIONS_SQL = """
ALTER TABLE {CATALOG}.{SCHEMA}.lab_results_test SET TAGS ('hipaa_compliance_healthcare' = 'Required');
ALTER TABLE {CATALOG}.{SCHEMA}.lab_results_test ALTER COLUMN ResultValue SET TAGS ('phi_level_healthcare' = 'High', 'shift_hours_healthcare' = 'Standard_Business');
ALTER TABLE {CATALOG}.{SCHEMA}.lab_results_test ALTER COLUMN TestName SET TAGS ('phi_level_healthcare' = 'Medium', 'shift_hours_healthcare' = 'Standard_Business');
ALTER TABLE {CATALOG}.{SCHEMA}.lab_results_test ALTER COLUMN PatientID SET TAGS ('pii_type_healthcare' = 'patient_id', 'phi_level_healthcare' = 'High');


ALTER TABLE {CATALOG}.{SCHEMA}.billing_test SET TAGS ('hipaa_compliance_healthcare' = 'Not_Required');
ALTER TABLE {CATALOG}.{SCHEMA}.billing_test ALTER COLUMN ChargeAmount SET TAGS ('data_sensitivity_healthcare' = 'Sensitive');


ALTER TABLE {CATALOG}.{SCHEMA}.patients_test SET TAGS ('hipaa_compliance_healthcare' = 'Required');
ALTER TABLE {CATALOG}.{SCHEMA}.patients_test ALTER COLUMN FirstName SET TAGS ('pii_type_healthcare' = 'patient_name');
ALTER TABLE {CATALOG}.{SCHEMA}.patients_test ALTER COLUMN LastName SET TAGS ('pii_type_healthcare' = 'patient_name');
ALTER TABLE {CATALOG}.{SCHEMA}.patients_test ALTER COLUMN PhoneNumber SET TAGS ('pii_type_healthcare' = 'phone','data_sensitivity_healthcare' = 'Sensitive');
ALTER TABLE {CATALOG}.{SCHEMA}.patients_test ALTER COLUMN Email SET TAGS ('pii_type_healthcare' = 'email','data_sensitivity_healthcare' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.patients_test ALTER COLUMN DateOfBirth SET TAGS ('pii_type_healthcare' = 'dob', 'phi_level_healthcare' = 'High');
ALTER TABLE {CATALOG}.{SCHEMA}.patients_test ALTER COLUMN PatientID SET TAGS ('pii_type_healthcare' = 'patient_id', 'phi_level_healthcare' = 'High');


ALTER TABLE {CATALOG}.{SCHEMA}.insurance_test SET TAGS ('hipaa_compliance_healthcare' = 'Not_Required');
ALTER TABLE {CATALOG}.{SCHEMA}.insurance_test ALTER COLUMN PolicyNumber SET TAGS ('data_sensitivity_healthcare' = 'Sensitive', 'phi_level_healthcare' = 'Medium');
ALTER TABLE {CATALOG}.{SCHEMA}.insurance_test ALTER COLUMN GroupNumber SET TAGS ('data_sensitivity_healthcare' = 'Sensitive','phi_level_healthcare' = 'Medium');
ALTER TABLE {CATALOG}.{SCHEMA}.insurance_test ALTER COLUMN PatientID SET TAGS ('pii_type_healthcare' = 'patient_id', 'phi_level_healthcare' = 'High');

"""

TEST_TABLES = ["insurance_test", "patients_test", "billing_test", "visits_test", "lab_results_test", "prescriptions_test", "providers_test"]



