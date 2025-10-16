-- =============================================
-- HEALTHCARE ABAC POLICIES - Using Built-in Groups
-- =============================================
-- This version uses workspace built-in groups (users, admins) instead of custom groups
--
-- Group Mapping:
-- - `users` group = Regular healthcare staff (analysts, technicians, clerks)
-- - `admins` group = Senior staff, managers (full data access)

USE CATALOG apscat;
USE SCHEMA healthcare;

-- Verify functions exist
SHOW FUNCTIONS IN apscat.healthcare LIKE 'mask*';
SHOW FUNCTIONS IN apscat.healthcare LIKE 'filter*';

SELECT "Ready to create healthcare ABAC policies with built-in groups" AS status;

-- =============================================
-- POLICY 1: Patient ID Masking for Cross-Table Analytics
-- =============================================
CREATE OR REPLACE POLICY healthcare_patient_id_masking
ON SCHEMA apscat.healthcare
COMMENT 'Deterministic masking of PatientID for analytics while preserving join capability'
COLUMN MASK apscat.healthcare.mask_referential
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('job_role', 'Healthcare_Analyst') AND hasTagValue('data_purpose', 'Population_Analytics') AS patient_id_cols
ON COLUMN patient_id_cols;

-- =============================================
-- POLICY 2: Business Hours Access for Lab Data
-- =============================================
CREATE OR REPLACE POLICY healthcare_business_hours_filter
ON SCHEMA apscat.healthcare
COMMENT 'Time-based access restriction for lab results outside business hours'
ROW FILTER apscat.healthcare.filter_business_hours
TO `users`
FOR TABLES
WHEN hasTagValue('shift_hours', 'Standard_Business');

-- =============================================
-- POLICY 3: Partial Name Masking for Privacy
-- =============================================
CREATE OR REPLACE POLICY healthcare_name_masking
ON SCHEMA apscat.healthcare
COMMENT 'Partial name masking for regular staff to protect patient privacy'
COLUMN MASK apscat.healthcare.mask_name_partial
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('phi_level', 'Full_PHI') AS name_cols
ON COLUMN name_cols;

-- =============================================
-- POLICY 4: Email Masking
-- =============================================
CREATE OR REPLACE POLICY healthcare_email_masking
ON SCHEMA apscat.healthcare
COMMENT 'Mask email addresses for regular users'
COLUMN MASK apscat.healthcare.mask_email
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('phi_level', 'Full_PHI') AS email_cols
ON COLUMN email_cols;

-- =============================================
-- POLICY 5: Phone Number Masking
-- =============================================
CREATE OR REPLACE POLICY healthcare_phone_masking
ON SCHEMA apscat.healthcare
COMMENT 'Mask phone numbers for regular users'
COLUMN MASK apscat.healthcare.mask_phone
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('phi_level', 'Full_PHI') AS phone_cols
ON COLUMN phone_cols;

-- =============================================
-- POLICY 6: Insurance Number Masking (Last 4)
-- =============================================
CREATE OR REPLACE POLICY healthcare_insurance_masking
ON SCHEMA apscat.healthcare
COMMENT 'Show only last 4 digits of insurance numbers for basic verification'
COLUMN MASK apscat.healthcare.mask_insurance_last4
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('verification_level', 'Basic') OR hasTagValue('verification_level', 'Standard') AS insurance_cols
ON COLUMN insurance_cols;

-- =============================================
-- POLICY 7: Age Group Masking for Research
-- =============================================
CREATE OR REPLACE POLICY healthcare_age_group_masking
ON SCHEMA apscat.healthcare
COMMENT 'Convert date of birth to age groups for HIPAA-compliant research'
COLUMN MASK apscat.healthcare.mask_dob_age_group
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('research_approval', 'Demographics_Study') AS dob_cols
ON COLUMN dob_cols;

-- Verify policies created
SHOW POLICIES ON SCHEMA apscat.healthcare;

SELECT "✅ Healthcare ABAC policies created successfully with built-in groups!" AS status;

-- =============================================
-- POLICY SUMMARY
-- =============================================
-- Column Masking Policies (6):
-- 1. Patient ID - Deterministic masking for joins
-- 2. Names - Partial masking (J*** S***)
-- 3. Emails - Local part masked (****@domain.com)
-- 4. Phones - Partial masking (XXX-XXX-1234)
-- 5. Insurance - Last 4 digits only
-- 6. DOB - Age groups (18-25, 26-35, etc.)
--
-- Row Filter Policies (1):
-- 7. Business hours - Time-based access control
--
-- Access Model:
-- - `users` group: See masked/filtered data
-- - `admins` group: See full unmasked data
--
-- This demonstrates role-based ABAC without requiring custom group creation!

