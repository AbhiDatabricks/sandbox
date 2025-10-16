# Healthcare ABAC Demo

## 🎯 Overview
A comprehensive Attribute-Based Access Control (ABAC) demonstration for healthcare/medical industry data governance using Databricks Unity Catalog, with focus on HIPAA compliance and PHI protection.

## 📊 Contents

### 📊 Data (6 Tables, 92 Rows)
| Table | Rows | Description |
|-------|------|-------------|
| `Patients` | 20 | Patient demographics with PHI |
| `Providers` | 20 | Healthcare provider information |
| `Insurance` | 20 | Insurance policies and coverage |
| `Visits` | 22 | Patient visits and encounters |
| `Prescriptions` | 5 | Medication prescriptions |
| `Billing` | 5 | Billing and payment records |

### 🔐 Masking Functions (9)
**Column Masks:**
- `mask_referential(id)` - Deterministic ID masking for cross-table joins (P-001 → REF_abc123...)
- `mask_name_partial(name)` - Partial name masking (John → J***n)
- `mask_email(email)` - Email masking (john@email.com → ****@email.com)
- `mask_phone(phone)` - Phone masking (555-1234 → XXXX1234)
- `mask_insurance_last4(policy)` - Insurance number masking (POL123456 → ****3456)
- `mask_dob_age_group(dob)` - DOB to age groups (1990-05-15 → 26-35)
- `mask_string_hash(str)` - SHA-256 hashing
- `mask_decimal_referential(num)` - Deterministic number masking
- `fast_deterministic_multiplier(num)` - Fast numeric transformation

**Row Filters (7):**
- `filter_business_hours()` - Business hours (8AM-6PM) access
- `filter_emergency_access()` - Emergency/24x7 access
- `filter_temporal_access()` - Time-limited access (expiry date)
- `filter_by_region()` - Geographic/regional filtering
- `filter_sensitive_records()` - Sensitive data access control
- `filter_hipaa_compliant()` - HIPAA compliance filtering
- `no_rows()` - Complete denial

### 🏷️ Healthcare-Specific Tags
| Tag Key | Values | Use Case |
|---------|--------|----------|
| `phi_level` | Full_PHI, Limited_Dataset, De-identified | PHI protection levels |
| `job_role` | Healthcare_Analyst, Lab_Technician, Billing_Clerk | Role-based access |
| `data_purpose` | Population_Analytics, Research, Billing | Purpose limitation |
| `shift_hours` | Standard_Business, Emergency_24x7 | Time-based access |
| `seniority` | Senior_Staff, Junior_Staff | Hierarchical access |
| `region` | North, South, East, West | Geographic control |
| `access_expiry_date` | Date values | Temporal access |
| `research_approval` | Demographics_Study, Clinical_Trial | Research ethics |
| `verification_level` | Basic, Standard, Full | Insurance verification |

## 🚀 Deployment

### Prerequisites
```bash
# Install Databricks SDK
pip install databricks-sdk pyyaml

# Configure Databricks CLI
databricks auth login --profile DEFAULT
```

### Configuration (`config.yaml`)
```yaml
databricks_profile: "DEFAULT"
warehouse_id: "862f1d757f0424f7"
catalog: "your_catalog_name"
schema: "healthcare"
```

### Deploy
```bash
cd uc-quickstart/utils/abac/healthcare
python3 execute_sql_configurable.py
```

## 🎭 Masking Examples

### Patient ID Deterministic Masking
```sql
SELECT 
  PatientID AS original,
  apscat.healthcare.mask_referential(PatientID) AS masked
FROM Patients;
```
**Result:** `P-001` → `REF_c2ef4e99b20b47609ad21816c758655...` (deterministic for joins)

### Name Partial Masking
```sql
SELECT 
  FirstName AS original,
  apscat.healthcare.mask_name_partial(FirstName) AS masked
FROM Patients;
```
**Result:** `John` → `J***n`

### Email Masking
```sql
SELECT 
  email AS original,
  apscat.healthcare.mask_email(email) AS masked
FROM Patients;
```
**Result:** `john.smith@email.com` → `****@email.com`

### Phone Masking
```sql
SELECT 
  PhoneNumber AS original,
  apscat.healthcare.mask_phone(PhoneNumber) AS masked
FROM Patients;
```
**Result:** `555-1234` → `XXXX1234`

### Insurance Last 4 Masking
```sql
SELECT 
  PolicyNumber AS original,
  apscat.healthcare.mask_insurance_last4(PolicyNumber) AS masked
FROM Insurance;
```
**Result:** `POL123456` → `****3456`

### DOB to Age Group
```sql
SELECT 
  DateOfBirth AS original,
  apscat.healthcare.mask_dob_age_group(DateOfBirth) AS age_group
FROM Patients;
```
**Result:** `1990-05-15` → `26-35`

## 🧪 Testing

### Run Verification Tests
```bash
cd uc-quickstart/utils/abac/healthcare
python3 execute_sql_configurable.py
```

### Test Queries
See `6.TestHealthcareData_Simple.sql` for comprehensive test queries covering:
- Patient ID masking for analytics
- Name/email/phone PII protection
- Insurance verification levels
- Age group demographics
- Visit/prescription statistics

## 📋 ABAC Policies (Optional)

### Note on Groups
ABAC policies require workspace groups (`users`, `admins`) or custom healthcare groups to be created by a workspace administrator.

**Custom Healthcare Groups (optional):**
- `Healthcare_Analyst` - Population health analytics
- `Lab_Technician` - Lab result access
- `Billing_Clerk` - Insurance verification
- `Junior_Staff` - Limited access
- `Senior_Staff` - Full PHI access
- `External_Auditor` - Temporary access
- `Population_Health_Researcher` - De-identified research data

Without policies, masking functions can be called manually:
```sql
SELECT mask_referential(PatientID) FROM Patients;
```

With policies (requires admin), masking is automatic:
```sql
-- As healthcare analyst: PatientID is automatically masked
SELECT PatientID FROM Patients;

-- As admin/doctor: PatientID is visible
SELECT PatientID FROM Patients;
```

### Policy Example
```sql
CREATE OR REPLACE POLICY healthcare_patient_id_masking
ON SCHEMA apscat.healthcare
COMMENT 'Deterministic masking for analytics'
COLUMN MASK apscat.healthcare.mask_referential
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('job_role', 'Healthcare_Analyst') AS patient_cols
ON COLUMN patient_cols;
```

## 📁 File Structure
```
healthcare/
├── config.yaml                                  # Deployment configuration
├── execute_sql_configurable.py                  # Config-driven deployment
├── 0.1healthcare_abac_functions_updated.sql     # 9 masking + 7 filter functions
├── 0.2healthcare_database_schema_updated.sql    # 6 healthcare tables with data
├── 3.ApplyHealthcareSetTags.sql                 # Apply tags to columns
├── 4.1.CreateHealthcareABACPolicies_Fixed.sql   # Original policies (custom groups)
├── 4.2.CreateHealthcareABACPolicies_BuiltInGroups.sql  # Built-in groups version
├── 6.TestHealthcareData_Simple.sql              # Verification tests
└── README.md                                    # This file
```

## 🎓 Healthcare-Specific Use Cases

### 1. Cross-Table Analytics (Deterministic Masking)
**Challenge:** Analysts need to join patient data across tables but shouldn't see actual patient IDs.
**Solution:** Deterministic masking produces same hash for same PatientID, enabling joins.
```sql
SELECT 
  p.PatientID AS masked_id,
  COUNT(v.VisitID) AS visit_count
FROM Patients p
JOIN Visits v ON p.PatientID = v.PatientID
GROUP BY p.PatientID;
```

### 2. Population Health Research (Age Groups)
**Challenge:** Researchers need age demographics but not exact DOBs (HIPAA requirement).
**Solution:** Convert DOB to age groups (18-25, 26-35, 36-50, 51-64, 65+).
```sql
SELECT 
  mask_dob_age_group(DateOfBirth) AS age_group,
  COUNT(*) AS patient_count
FROM Patients
GROUP BY mask_dob_age_group(DateOfBirth);
```

### 3. Insurance Verification (Last 4 Digits)
**Challenge:** Billing clerks need to verify insurance but don't need full policy numbers.
**Solution:** Show only last 4 digits for basic verification.
```sql
SELECT 
  mask_insurance_last4(PolicyNumber) AS policy_last4,
  InsuranceCompany
FROM Insurance;
```

### 4. Time-Based Access Control
**Challenge:** Lab data should only be accessible during business hours for regular staff.
**Solution:** Row filter based on current time and user role.
```sql
-- Automatically filters rows outside business hours for regular users
SELECT * FROM LabResults;
```

### 5. Temporary External Auditor Access
**Challenge:** Grant external auditors time-limited access to billing data.
**Solution:** Row filter with expiry date check.
```sql
-- Automatically filters all data after expiry date
SELECT * FROM Billing WHERE access_expiry_date > CURRENT_DATE();
```

## 🔧 Troubleshooting

### Issue: Functions not found
**Solution:** Deploy functions first:
```bash
python3 execute_sql_configurable.py
```

### Issue: Schema not found
**Solution:** Schema is auto-created, but verify catalog exists:
```sql
SHOW CATALOGS;
USE CATALOG apscat;
CREATE SCHEMA IF NOT EXISTS healthcare;
```

### Issue: Policies failing with "Unknown tag policy key"
**Solution:** Create tag policies first (admin required):
```sql
CREATE TAG POLICY IF NOT EXISTS phi_level 
ALLOWED VALUES ['Full_PHI', 'Limited_Dataset', 'De-identified'];
```

### Issue: Column name mismatches in tests
**Solution:** Check actual column names in tables:
```sql
DESCRIBE TABLE Patients;
```

## 📊 Test Results

```
✅ 6 tables with 92 total rows
✅ 16 masking/filter functions deployed
✅ Patient ID: P-001 → REF_abc123... (deterministic)
✅ Name: John → J***n
✅ Email: john@email.com → ****@email.com
✅ Phone: 555-1234 → XXXX1234
✅ Insurance: POL123456 → ****3456
✅ DOB: 1990-05-15 → 26-35 (age group)
```

## 🚦 Next Steps

1. **Apply Tags**: Use `3.ApplyHealthcareSetTags.sql` to tag columns
2. **Create Groups**: Have admin create healthcare-specific groups or use built-in `users`/`admins`
3. **Apply Policies**: Use `4.2.CreateHealthcareABACPolicies_BuiltInGroups.sql`
4. **Test Access**: Verify masking works for different user groups
5. **Production**: Adapt to your actual healthcare data model

## 📚 References
- [Unity Catalog ABAC Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/attribute-based-access-control.html)
- [HIPAA Compliance](https://www.hhs.gov/hipaa/index.html)
- [Column Masking](https://docs.databricks.com/en/data-governance/unity-catalog/column-masks.html)
- [Row Filters](https://docs.databricks.com/en/data-governance/unity-catalog/row-filters.html)

---
**Status**: ✅ Fully deployed and tested (2024)
**HIPAA Note**: This is a demonstration. For production HIPAA compliance, consult legal/compliance teams.

