## Insurance ABAC Demo

A comprehensive ABAC (Attribute-Based Access Control) demonstration for the insurance industry.

### 📊 Overview

**Database Schema (4 tables, 62 rows)**
- `policyholders` (20 rows) - Policy holder master data with PII (SSN, email, phone)
- `policies` (20 rows) - Insurance Policies (auto, home, life)
- `claims` (9 rows) - Insurance Claims
- `Premiums` (13 rows) - Insurance Premiums

**Masking Functions (6 total)**
- `mask_policy_number_last4` - Policy number masking
- `mask_ssn_last4` - SSN masking (XXX-XX-1234)
- `mask_email` - Email privacy
- `mask_phone` - Phone masking
- `mask_claim_amount_bucket` - Claim amount ranges
- `mask_policyholder_id_hash` - Policy holder ID hashing

**Deployment Options**
- Interactive Notebooks (4 .ipynb files)
- Configuration file (`config.yaml`)

### 🎭 Masking Examples:

```
Policy No.:   434234567 → ****4567
SSN:          123-45-6789 → XXX-XX-6789
Email:        john.smith@email.com → ****@email.com
Phone:        283-555-0101 → XXXX0101
Amount:       $8500.00 → $5K-$10K (bucket)
PH ID:        PH-1001 → PH_1cec78... (deterministic for joins)
```

### 🔒 Compliance Features:

**Privacy Protection:**
- SSN masking
- Email/phone obfuscation
- Claim amount bracketing (not exact figures)
- Policy number partial masking

### 📊 Data Statistics:
```
Total Records: 120
- 20 Policy holders
- 20 Insurance policies (auto/home/life)
- 9 Filed claims (3 types: approved, pending, denied)
- 13 Premiums across different policies
```

### 🚀 Quick Start:

**Using Notebooks**
1. Import the 4 `.ipynb` files to Databricks
2. Edit `config.yaml` to set your catalog name
3. Run notebooks 1 → 2 → 3 → 4


### 📁 File Structure:
```
finance/
├── config.yaml                          # Configuration (edit this!)
├── 1_Create_Functions.ipynb             # Notebook: Create masking + filtering functions
├── 2_Create_Tables.ipynb                # Notebook: Create schema & tables
├── 3_Setup_Tagging.ipynb                # Notebook: Define governed tags
├── 4_Test_ABAC_Policies.ipynb           # Notebook: Test functions through ABAC policies
├── 5_Cleanup.ipynb                      # Notebook: Cleanup test tables, tag policies, and abac policies
├── README.md                            # This file
```

### 🔧 Configuration:

Edit `config.yaml` to set your Unity Catalog and schema:
```yaml
catalog: "your_catalog_name"  # Change this
schema: "insurance"
```

All notebooks will automatically use these settings.

### 📚 References:
- [Unity Catalog ABAC Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/)
- [Databricks Financial Services Solutions - Insurance](https://www.databricks.com/solutions/industries/financial-services#insurance)

---

**Note**: This is a demonstration environment. For production configuration, consult with security and compliance teams.

