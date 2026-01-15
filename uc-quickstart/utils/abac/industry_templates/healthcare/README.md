# Healthcare ABAC Demo

## 🎯 Overview
A comprehensive Attribute-Based Access Control (ABAC) demonstration for healthcare/medical industry data governance using Databricks Unity Catalog, with focus on HIPAA compliance and PHI protection.

## 📊 Contents

### 📊 Data (6 Tables, 92 Rows)
| Table | Rows | Description |
|-------|------|-------------|
| `patients` | 20 | Patient demographics with PHI |
| `providers` | 20 | Healthcare provider information |
| `insurance` | 20 | Insurance policies and coverage |
| `visits` | 22 | Patient visits and encounters |
| `prescriptions` | 5 | Medication prescriptions |
| `billing` | 5 | Billing and payment records |

### 🔐 Masking Functions (9)
**Column Masks:**
- `mask_referential(id)` - Deterministic ID masking for cross-table joins (P-001 → REF_abc123...)
- `mask_string_partial(name)` - Partial name masking (John → J***n)
- `mask_email(email)` - Email masking (john@email.com → ****@email.com)
- `mask_phone(phone)` - Phone masking (555-1234 → XXXX1234)
- `mask_date_year_only(dob)` - DOB to age groups (1990-05-15 → 1990-01-01)
- `mask_string_hash(str)` - SHA-256 hashing
- `mask_decimal_referential(num)` - Deterministic number masking
- `fast_deterministic_multiplier(num)` - Fast numeric transformation

**Row Filters (3):**
- `filter_business_hours()` - Business hours (8AM-6PM) access
- `filter_by_region()` - Geographic/regional filtering
- `no_rows()` - Complete denial

### 🏷️ Healthcare-Specific Tags
| Tag Key | Values | Use Case |
|---------|--------|----------|
| `pii_type_healthcare` | patient_name, patient_id, ssn, dob, phone, email, address, medical_record_number, diagnosis, treatment | PII sensitivity levels |
| `phi_level_healthcare` | High, Medium, Low, Public | PHI protection levels |
| `shift_hours_healthcare` | Standard_Business, Emergency_24x7 | Time-based access |
| `data_sensitivity_healthcare` | Highly_Sensitive, Sensitive, Internal, Public | Data sensitivity classification |
| `hipaa_compliance_healthcare` | Required, Not_Required | HIPAA Compliance requirement|

## 🚀 Deployment
- Interactive Notebooks (5 .ipynb files)
- Configuration file (`config.yaml`)

### 🔧 Configuration:

Edit `config.yaml` to set your Unity Catalog and schema:
```yaml
catalog: "your_catalog_name"  # Change this
schema: "healthcare"
```

All notebooks will automatically use these settings.


### 📁 File Structure:
```
healthcare/
├── config.yaml                          # Configuration (edit this!)
├── 1_Create_Functions.ipynb             # Notebook: Create masking + filtering functions
├── 2_Create_Tables.ipynb                # Notebook: Create schema & tables
├── 3_Setup_Tagging.ipynb                # Notebook: Define governed tags
├── 4_Test_ABAC_Policies.ipynb           # Notebook: Test functions through ABAC policies
├── 5_Cleanup.ipynb                      # Notebook: Cleanup test tables, tag policies, and ABAC policies
├── README.md                            # This file
```

## 🎓 Healthcare-Specific Use Cases

### 1. Cross-Table Analytics (Deterministic Masking)
**Challenge:** Analysts need to join patient data across tables but shouldn't see actual patient IDs.
**Solution:** Deterministic masking produces same hash for same PatientID, enabling joins.
```sql
SELECT 
  p.PatientID AS masked_id,
  COUNT(v.VisitID) AS visit_count
FROM patients p
JOIN visits v ON p.PatientID = v.PatientID
GROUP BY p.PatientID;
```

### 2. Population Health Research (Age Groups)
**Challenge:** Researchers need age demographics but not exact DOBs (HIPAA requirement).
**Solution:** Convert DOB to age groups.
```sql
SELECT 
  mask_dob_age_group(DateOfBirth) AS age_group,
  COUNT(*) AS patient_count
FROM patients
GROUP BY mask_dob_age_group(DateOfBirth);
```

### 3. Time-Based Access Control
**Challenge:** Lab data should only be accessible during business hours for regular staff.
**Solution:** Row filter based on current time and user role.
```sql
-- Automatically filters rows outside business hours for regular users
SELECT * FROM lab_results;
```

## 📚 References
- [Unity Catalog ABAC Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/attribute-based-access-control.html)
- [HIPAA Compliance](https://www.hhs.gov/hipaa/index.html)
- [Column Masking](https://docs.databricks.com/en/data-governance/unity-catalog/column-masks.html)
- [Row Filters](https://docs.databricks.com/en/data-governance/unity-catalog/row-filters.html)

---
**HIPAA Note**: This is a demonstration. For production HIPAA compliance, consult legal/compliance teams.

