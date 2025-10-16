-- =============================================
-- HEALTHCARE DATA VERIFICATION & TESTING
-- =============================================
-- Purpose: Verify tables, data, and demonstrate masking functions
-- NO ABAC POLICIES REQUIRED - Manual function demonstration
-- =============================================

USE CATALOG apscat;
USE SCHEMA healthcare;

-- =============================================
-- TEST 1: Table Row Counts
-- =============================================
SELECT '=== TABLE ROW COUNTS ===' AS section;

SELECT 
  'Patients' AS table_name, 
  COUNT(*) AS row_count 
FROM Patients
UNION ALL
SELECT 'Providers', COUNT(*) FROM Providers
UNION ALL
SELECT 'Insurance', COUNT(*) FROM Insurance
UNION ALL
SELECT 'Visits', COUNT(*) FROM Visits
UNION ALL
SELECT 'LabResults', COUNT(*) FROM LabResults
UNION ALL
SELECT 'Prescriptions', COUNT(*) FROM Prescriptions
UNION ALL
SELECT 'Billing', COUNT(*) FROM Billing
ORDER BY table_name;

-- =============================================
-- TEST 2: Patient ID Deterministic Masking Demo
-- =============================================
SELECT '=== PATIENT ID MASKING (Deterministic) ===' AS section;

SELECT 
  PatientID AS original_id,
  apscat.healthcare.mask_referential(PatientID) AS masked_id,
  FirstName,
  LastName
FROM Patients
LIMIT 5;

-- =============================================
-- TEST 3: Name Partial Masking Demo
-- =============================================
SELECT '=== NAME MASKING DEMO ===' AS section;

SELECT 
  PatientID,
  FirstName AS original_first,
  apscat.healthcare.mask_name_partial(FirstName) AS masked_first,
  LastName AS original_last,
  apscat.healthcare.mask_name_partial(LastName) AS masked_last
FROM Patients
LIMIT 5;

-- =============================================
-- TEST 4: Email Masking Demo
-- =============================================
SELECT '=== EMAIL MASKING DEMO ===' AS section;

SELECT 
  PatientID,
  CONCAT(FirstName, '.', LastName, '@email.com') AS sample_email,
  apscat.healthcare.mask_email(CONCAT(FirstName, '.', LastName, '@email.com')) AS masked_email
FROM Patients
LIMIT 5;

-- =============================================
-- TEST 5: Phone Masking Demo
-- =============================================
SELECT '=== PHONE MASKING DEMO ===' AS section;

SELECT 
  PatientID,
  PhoneNumber AS original_phone,
  apscat.healthcare.mask_phone(PhoneNumber) AS masked_phone
FROM Patients
LIMIT 5;

-- =============================================
-- TEST 6: Insurance Number Masking (Last 4)
-- =============================================
SELECT '=== INSURANCE MASKING DEMO ===' AS section;

SELECT 
  PatientID,
  PolicyNumber AS original_policy,
  apscat.healthcare.mask_insurance_last4(PolicyNumber) AS masked_policy_last4,
  GroupNumber AS original_group,
  apscat.healthcare.mask_insurance_last4(GroupNumber) AS masked_group_last4
FROM Insurance
LIMIT 5;

-- =============================================
-- TEST 7: Date of Birth to Age Group
-- =============================================
SELECT '=== DOB TO AGE GROUP DEMO ===' AS section;

SELECT 
  PatientID,
  DateOfBirth AS original_dob,
  apscat.healthcare.mask_dob_age_group(DateOfBirth) AS age_group
FROM Patients
LIMIT 5;

-- =============================================
-- TEST 8: Multi-Column Masking Demo
-- =============================================
SELECT '=== MULTI-COLUMN MASKING DEMO ===' AS section;

SELECT 
  PatientID,
  apscat.healthcare.mask_name_partial(FirstName) AS masked_first,
  apscat.healthcare.mask_name_partial(LastName) AS masked_last,
  apscat.healthcare.mask_dob_age_group(DateOfBirth) AS age_group,
  apscat.healthcare.mask_phone(PhoneNumber) AS masked_phone
FROM Patients
LIMIT 5;

-- =============================================
-- TEST 9: Lab Results with Masking
-- =============================================
SELECT '=== LAB RESULTS WITH MASKING ===' AS section;

SELECT 
  lr.TestID,
  apscat.healthcare.mask_referential(lr.PatientID) AS masked_patient_id,
  lr.TestType,
  lr.Result,
  lr.TestDate
FROM LabResults lr
LIMIT 5;

-- =============================================
-- TEST 10: Billing Data with Masking
-- =============================================
SELECT '=== BILLING DATA WITH MASKING ===' AS section;

SELECT 
  b.BillingID,
  apscat.healthcare.mask_referential(b.PatientID) AS masked_patient_id,
  b.TotalAmount,
  b.PaymentStatus,
  b.BillingDate
FROM Billing b
LIMIT 5;

-- =============================================
-- TEST 11: Visit Statistics
-- =============================================
SELECT '=== VISIT STATISTICS ===' AS section;

SELECT 
  VisitType,
  COUNT(*) AS visit_count,
  COUNT(DISTINCT PatientID) AS unique_patients
FROM Visits
GROUP BY VisitType
ORDER BY visit_count DESC;

-- =============================================
-- TEST 12: Prescription Summary
-- =============================================
SELECT '=== PRESCRIPTION SUMMARY ===' AS section;

SELECT 
  MedicationName,
  COUNT(*) AS prescription_count,
  COUNT(DISTINCT PatientID) AS unique_patients
FROM Prescriptions
GROUP BY MedicationName
ORDER BY prescription_count DESC
LIMIT 10;

-- =============================================
-- TEST 13: Provider Statistics
-- =============================================
SELECT '=== PROVIDER STATISTICS ===' AS section;

SELECT 
  Specialty,
  COUNT(*) AS provider_count
FROM Providers
GROUP BY Specialty
ORDER BY provider_count DESC;

-- =============================================
-- TEST 14: Insurance Coverage Summary
-- =============================================
SELECT '=== INSURANCE COVERAGE SUMMARY ===' AS section;

SELECT 
  InsuranceProvider,
  COUNT(*) AS policy_count,
  COUNT(DISTINCT PatientID) AS covered_patients
FROM Insurance
GROUP BY InsuranceProvider
ORDER BY policy_count DESC;

-- =============================================
-- TEST 15: Functions Verification
-- =============================================
SELECT '=== MASKING FUNCTIONS AVAILABLE ===' AS section;

SHOW USER FUNCTIONS IN apscat.healthcare LIKE 'mask_%';

-- =============================================
-- SUMMARY
-- =============================================
SELECT 
  '✅ HEALTHCARE DATA VERIFICATION COMPLETE' AS status,
  '7+ tables with synthetic healthcare data' AS data_summary,
  'All masking functions demonstrated successfully' AS functions_status;

