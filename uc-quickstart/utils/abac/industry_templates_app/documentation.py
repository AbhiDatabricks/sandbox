"""
Documentation content for the ABAC Industry Templates App
"""

DOCUMENTATION_MD = """
# 📚 ABAC Industry Templates - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Step-by-Step Guide](#step-by-step-guide)
4. [Industry Templates](#industry-templates)
5. [Authorization Modes](#authorization-modes)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## 🎯 Overview

### What is ABAC?

**Attribute-Based Access Control (ABAC)** is a flexible authorization model in Databricks Unity Catalog that allows you to:
- **Mask sensitive data** based on user attributes (groups, roles)
- **Filter rows** to show only authorized data
- **Apply policies dynamically** without changing table schemas
- **Meet compliance requirements** (HIPAA, PCI-DSS, GDPR, etc.)

### How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   User       │────▶│  ABAC Policy │────▶│  Masked Data │
│ (with tags)  │     │   (checks    │     │   (secure)   │
│              │     │    tags)     │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Example:**  
- User in `finance_analysts` group sees full credit card numbers
- User in `customer_service` group sees masked `****-1234`
- Users outside both groups see `****-****`

---

## 🚀 Getting Started

### Prerequisites

Before using this app, ensure you have:

✅ **Unity Catalog enabled** in your Databricks workspace  
✅ **SQL Warehouse** configured (app uses this for execution)  
✅ **Target catalog and schema** (or permission to create new schema)  
✅ **Permissions** to create/manage resources in the target catalog/schema:
   - Functions in the target schema (Step 1)
   - ABAC policies on the schema (Step 3, requires `MANAGE` on schema)
   - Tables in the target schema (optional Step 4)
✅ **Permissions** to grant the above privileges to the app service principal:
  - grant use catalog on catalog CATALOG to `SP-ID`;
  - grant use schema on schema CATALOG.SCHEMA to `SP-ID`;
  - grant create function on schema CATALOG.SCHEMA to `SP-ID`;
  - grant create table on schema CATALOG.SCHEMA to `SP-ID`;


### Required Permissions by Step

| Step | Permission Required | Who Grants It | SQL Command |
|------|---------------------|---------------|-------------|
| **Step 1: Functions** | `CREATE FUNCTION` on schema | Catalog Owner or Metastore Admin | `GRANT CREATE FUNCTION ON SCHEMA catalog.schema TO \`app-SP\`;` |
| **Step 2: Tag Policies** | **Account Admin** for the App's Service Principal | Account Admin (via Account Console) | Go to Account Console → Users → Find App SP → Add "Account Admin" role |
| **Step 3: ABAC Policies** | `MANAGE` on schema | Catalog Owner or Metastore Admin | `GRANT MANAGE ON SCHEMA catalog.schema TO \`app-SP\`;` |
| **Step 4: Test Data** | `CREATE TABLE` on schema | Catalog Owner | `GRANT CREATE TABLE ON SCHEMA catalog.schema TO \`app-SP\`;` |
| **Step 5: Tag Data** | `APPLY TAG` on tables | Catalog Owner | `GRANT APPLY TAG ON TABLE catalog.schema.* TO \`app-SP\`;` |

### ⚠️ Important: Step 2 Requires Account Admin

**Step 2 (Create Tag Policies)** requires the App's Service Principal to have **Account Admin** role. This is because tag policies are created at the **account level**, not the workspace level.

**To grant Account Admin to the App's Service Principal:**

1. Go to **Account Console** (accounts.cloud.databricks.com or accounts.azuredatabricks.net)
2. Navigate to **User management** → **Service principals**
3. Find the service principal named `app-XXXX <your-app-name>` (e.g., `app-39ck4z abacindustry`)
4. Click on the service principal → **Roles** tab
5. Add the **Account Admin** role

**Without this permission, Step 2 will fail** with: `"Provided OAuth token does not have required scopes"`

### Finding the App's Service Principal

When a Databricks App is created, it automatically gets a service principal. You can find it by:

1. **From the App page:** Go to your App → Settings → The SP name is shown as "Service Principal"
2. **From CLI:** `databricks apps get <app-name>` - look for `service_principal_name`
3. **Pattern:** Usually named `app-XXXXX <app-name>`

### Quick Start (5 Minutes)

1. **Select Configuration**
   - Catalog: Choose existing or type new
   - Schema: Choose existing or type new (will be created)
   - Industry: Pick from 6 industries

2. **Run Required Steps** (in order)
   - ① Create Functions → Deploys masking UDFs
   - ② Create Tag Policies → Defines governed tags  
   - ③ Create ABAC Policies → Applies policies

3. **Test (Optional)**
   - ④ Create Test Data → Sample tables with `_test` suffix
   - ⑤ Tag Test Data → Apply tags to columns
   - ⑥ Test Policies → Run queries to verify

---

## 📋 Step-by-Step Guide

### Step 1: Create Functions

**What it does:**  
Deploys User-Defined Functions (UDFs) for data masking and filtering.

**Examples:**
- `mask_credit_card('4111222233334444')` → `****-****-****-4444`
- `mask_email('john@company.com')` → `****@company.com`
- `mask_ssn_last4('123-45-6789')` → `***-**-6789`

**Industry Function Counts:**
- Finance: 15 functions
- Healthcare: 9 functions
- Manufacturing: 13 functions
- Retail: 11 functions
- Telco: 8 functions
- Government: 8 functions

**Time:** ~30-60 seconds

---

### Step 2: Create Tag Policies

**What it does:**  
Creates account-level tag definitions with allowed values.

**Important:** This step **requires Service Principal** (admin OAuth scopes). The "Use User Authorization" checkbox is ignored for this step.

**Example Tags (Finance):**
```sql
pii_type_finance:
  - email, ssn, credit_card, phone, etc.

pci_compliance_finance:
  - Required, Not_Required

data_classification_finance:
  - Public, Internal, Confidential, Restricted
```

**Each industry gets 4 tag policies** with industry-specific suffix (e.g., `_finance`, `_healthcare`)

**Time:** ~10-20 seconds

---

### Step 3: Create ABAC Policies

**What it does:**  
Creates column mask and row filter policies that use the functions and tags.

**Example Policy:**
```sql
CREATE POLICY IF NOT EXISTS mask_ssn_policy  
  ON SCHEMA finance  
  COLUMN MASK mask_ssn_last4  
  USING hasTagValue('pii_type_finance', 'ssn')  
  FOR EXCEPT ('account users');
```

**This means:**
- Any column tagged with `pii_type_finance = 'ssn'`
- Will be masked using `mask_ssn_last4()` function
- For all users except those in `account users` group

**Policy Counts:**
- Finance: 14 policies
- Healthcare: 8 policies
- Manufacturing: 10 policies
- Retail/Telco/Government: Included in templates

**Time:** ~20-40 seconds

---

### Step 4: Create Test Data (Optional)

**What it does:**  
Creates sample tables with `_test` suffix for testing policies.

**Test Tables (Finance):**
- `customers_test` - Customer PII data
- `accounts_test` - Account information
- `credit_cards_test` - Card numbers
- `transactions_test` - Transaction records

**Important:** Test tables are separate from production. They help verify masking works before applying to real data.

**Time:** ~30-60 seconds

---

### Step 5: Tag Test Data (Optional)

**What it does:**  
Applies tags to columns in test tables.

**Example:**
```sql
ALTER TABLE customers_test  
  ALTER COLUMN ssn  
  SET TAGS ('pii_type_finance' = 'ssn', 'pci_compliance_finance' = 'Required');
```

Now the `ssn` column will trigger the `mask_ssn_policy` created in Step 3!

**Time:** ~20-40 seconds

---

### Step 6: Test Policies (Optional)

**What it does:**  
Runs sample SELECT queries to verify masking is applied.

**Example Test:**
```sql
SELECT customer_id, ssn, email, credit_card  
FROM customers_test  
LIMIT 5;
```

**Expected Results:**
- SSN: `***-**-6789` (last 4 visible)
- Email: `****@company.com` (domain visible)
- Credit Card: `****-****-****-4444` (last 4 visible)

**Time:** ~10-20 seconds

---

## 🏭 Industry Templates

### Default ⭐ (SUPER-SET - Recommended Starting Point)
**Use Cases:** Comprehensive generic template - works for ANY industry. Contains the maximum coverage of all masking, filtering, and policy types.

**Column Masking Functions (20):**
- `mask_ssn` - SSN (last 4 digits)
- `mask_email` - Email (domain visible)
- `mask_phone` - Phone (last 4 digits)
- `mask_credit_card` - Credit card (PCI-DSS compliant)
- `mask_account_number` - Account number (last 4)
- `mask_routing_number` - Routing number (last 2)
- `mask_name` - Name (first initial + ***)
- `mask_name_hash` - Name (SHA-256 hash)
- `mask_address` - Address (city/state only)
- `mask_dob` - Date of birth (year only)
- `mask_dob_age_range` - DOB to age bucket
- `mask_ip_address` - IP (subnet only)
- `mask_amount_bucket` - Amount ranges ($0-$100, $100-$1K, etc.)
- `mask_salary_bucket` - Salary ranges (Entry, Junior, Mid, Senior, etc.)
- `mask_string_hash` - SHA-256 anonymization
- `mask_string_partial` - First/last chars visible
- `mask_id_deterministic` - Deterministic ID hash (preserves joins)
- `mask_timestamp_round` - Round to 15-min intervals
- `mask_gps_precision` - GPS to 2 decimal places (~1km)
- `mask_serial_last4` - Serial number (last 4)

**Row Filter Functions (8):**
- `filter_business_hours` - 9AM-5PM access
- `filter_extended_hours` - 7AM-9PM access
- `filter_maintenance_window` - 10PM-6AM access
- `filter_high_value` - >$10K transactions
- `filter_flagged_only` - Flagged records only
- `filter_active_only` - Active status only
- `filter_deny_all` - Block all access
- `filter_allow_all` - Allow all access

**Tag Policies (8):**
- `pii_type` - 19 PII types (ssn, email, phone, name, dob, credit_card, medical_record, etc.)
- `data_classification` - 5 levels (Public, Internal, Confidential, Restricted, Top_Secret)
- `compliance_requirement` - 10 frameworks (PCI_DSS, HIPAA, GDPR, CCPA, SOX, GLBA, etc.)
- `sensitivity_level` - 4 levels (Low, Medium, High, Critical)
- `data_purpose` - 10 purposes (Operations, Analytics, Audit, HR, Marketing, etc.)
- `access_restriction` - 7 types (Business_Hours, Region_Locked, Flagged_Only, etc.)
- `retention_policy` - 7 periods (30_Days, 90_Days, 1_Year, 7_Years, etc.)
- `geographic_scope` - 4 scopes (Country_Only, Region_Only, Cross_Border_Approved, Global)

**ABAC Policies (15):**
- 12 column mask policies (SSN, email, phone, name, credit_card, account, IP, DOB, amount, salary, device_id, timestamp)
- 3 row filter policies (business hours, extended hours, maintenance window)

**Test Data (5 tables):**
- `users_test` - Customer PII (8 rows)
- `transactions_test` - Financial transactions with fraud flags (10 rows)
- `employees_test` - HR/Employee records with salary (10 rows)
- `assets_test` - Inventory/Equipment with GPS (8 rows)
- `audit_log_test` - System access logs (10 rows)

---

### Finance ✅ Complete
**Use Cases:** Banking, credit cards, payment processing

**Functions:**
- Credit card masking (PCI-DSS compliant)
- SSN protection (last 4 digits)
- Account/routing number masking
- Transaction amount bucketing
- Fraud detection filters

**Tags:**
- `pii_type_finance` - PII field types
- `pci_compliance_finance` - PCI requirements
- `data_classification_finance` - Data sensitivity
- `fraud_detection_finance` - Fraud flags

**ABAC Policies:** 14 policies (9 column masks + 4 row filters + 1 combined)

---

### Insurance ✅ Complete
**Use Cases:** Insurance policies, claims processing, underwriting

**Functions:**
- SSN masking (last 4 digits)
- Policy number masking (last 4 digits)
- Claim amount bucketing
- Policyholder ID hashing (deterministic for joins)
- Email/phone masking
- Business hours filter
- High value claims filter

**Tags:**
- `pii_type_insurance` - PII field types (ssn, email, phone, policy_number, amount, id)
- `data_classification_insurance` - Data classification (Confidential, Internal, Public)

**ABAC Policies:** 6 policies (SSN, policy number, email, phone, policyholder ID, high-value claims filter)

---

### Healthcare ✅ Complete
**Use Cases:** Hospitals, medical records, HIPAA compliance

**Functions:**
- Patient name/ID masking
- Medical record number protection
- Diagnosis/treatment masking
- Provider information protection
- Email/phone masking

**Tags:**
- `pii_type_healthcare` - Healthcare PII types
- `phi_level_healthcare` - PHI sensitivity
- `hipaa_compliance_healthcare` - HIPAA requirements
- `data_sensitivity_healthcare` - Data classification

**ABAC Policies:** 8 policies (column masks for PHI data)

---

### Manufacturing ✅ Complete
**Use Cases:** Product design, supply chain, trade secrets

**Functions:**
- Employee ID/SSN masking
- Product design protection
- Supplier information masking
- Production data filtering
- Quality control data protection

**Tags:**
- `pii_type_manufacturing` - Employee PII
- `ip_classification_manufacturing` - IP/trade secrets
- `compliance_type_manufacturing` - Export control, ISO
- `data_sensitivity_manufacturing` - Sensitivity levels

**ABAC Policies:** 10 policies (protecting IP and employee data)

---

### Retail ✅ Complete
**Use Cases:** E-commerce, customer data, loyalty programs

**Functions:** 11 masking functions  
**Tags:** 4 tag policies  
**ABAC Policies:** Included in templates

---

### Telco ✅ Complete
**Use Cases:** Subscriber data, call records, GDPR compliance

**Functions:** 8 masking functions  
**Tags:** 4 tag policies  
**ABAC Policies:** Included in templates

---

### Government ✅ Complete
**Use Cases:** Security clearances, classified data, CUI

**Functions:** 8 masking functions  
**Tags:** 4 tag policies  
**ABAC Policies:** Included in templates

---

## 🔐 Authorization Modes

### Service Principal (Default)

**When to use:**
- Deploying to shared catalog/schema
- App admin managing policies
- Automated deployments

**How it works:**
- Uses app's service principal identity
- Has permissions granted to the app
- Independent of your user permissions

**Checkbox:** ☐ Use User Authorization (unchecked)

---

### User Authorization

**When to use:**
- Testing YOUR specific permissions
- Deploying to your personal schema
- Seeing masking based on YOUR group membership

**How it works:**
- Extracts `X-Forwarded-Access-Token` from request
- All operations run as YOUR identity
- Uses YOUR Unity Catalog permissions

**Checkbox:** ☑ Use User Authorization (checked)

**Progress shows:** `Auth: User (your.email@databricks.com)`

**Note:** Step 2 (Tag Policies) ALWAYS uses Service Principal due to required OAuth scopes.

---

## 🔧 Troubleshooting

### Common Issues

#### "PERMISSION_DENIED: User does not have USE CATALOG"

**Problem:** You don't have permissions on the catalog.

**Solution:**
```sql
-- Admin must grant:
GRANT USE CATALOG ON CATALOG your_catalog TO `your.email@databricks.com`;
GRANT USE SCHEMA ON SCHEMA your_catalog.your_schema TO `your.email@databricks.com`;
GRANT CREATE FUNCTION ON SCHEMA your_catalog.your_schema TO `your.email@databricks.com`;
```

---

#### "ALREADY_EXISTS: Tag policy already exists"

**Problem:** Tag policies with same names exist (they're account-level).

**Solution:** This is informational - the app continues. Each industry uses unique suffixes (`_finance`, `_healthcare`) to avoid conflicts.

---

#### "Provided OAuth token does not have required scopes"

**Problem:** User authorization doesn't have admin scopes for tag policies.

**Solution:** Uncheck "Use User Authorization" for Step 2, or always use Service Principal.

---

#### "SQL execution error: warehouse_id required"

**Problem:** SQL warehouse not configured.

**Solution:** The app should auto-select a warehouse. Check that at least one SQL warehouse exists and is running.

---

#### "Function created in wrong catalog/schema"

**Problem:** `USE CATALOG` context not persisting between statements.

**Solution:** App now uses fully qualified names (`CATALOG.SCHEMA.FUNCTION_NAME`). Update to latest version.

---

## ✅ Best Practices

### 1. Start with Finance or Healthcare
These industries have complete ABAC policies and are fully tested.

### 2. Use Test Data First
Always run Steps 4-6 (optional testing) before applying to production tables.

### 3. Tag Your Real Tables
After testing, apply tags to your production tables:
```sql
ALTER TABLE my_production_table  
  ALTER COLUMN ssn  
  SET TAGS ('pii_type_finance' = 'ssn');
```

### 4. Create User Groups
ABAC works best with groups:
```sql
-- Example: Create finance analysts group
CREATE GROUP finance_analysts;
ALTER GROUP finance_analysts ADD USER `analyst@company.com`;

-- Update policy to use your group:
CREATE POLICY mask_ssn_policy  
  ...  
  FOR EXCEPT ('finance_analysts');
```

### 5. Test with Different Users
Log in as different users (or use different groups) to verify masking works correctly.

### 6. Document Your Policies
Keep track of which columns are tagged and what policies apply.

### 7. Monitor Performance
ABAC policies are evaluated on every query. For large tables:
- Use row filters sparingly
- Combine filters when possible
- Consider materialized views for heavy masking

### 8. Regular Audits
Periodically review:
- Which policies are active (`SHOW POLICIES IN SCHEMA`)
- Which columns are tagged
- Which groups have exceptions

---

## 📚 Additional Resources

### Databricks Documentation
- [Unity Catalog ABAC Overview](https://docs.databricks.com/data-governance/unity-catalog/abac/)
- [Column Masks](https://docs.databricks.com/security/privacy/column-masks.html)
- [Row Filters](https://docs.databricks.com/security/privacy/row-filters.html)

### GitHub Repository
- [Source Code](https://github.com/AbhiDatabricks/sandbox)
- [Issue Tracker](https://github.com/AbhiDatabricks/sandbox/issues)

### Support
For questions or issues, contact your Databricks account team or file an issue on GitHub.

---

**Version:** 1.1  
**Last Updated:** December 2025  
**Supported Industries:** Default, Finance, Insurance, Healthcare, Manufacturing, Retail, Telco, Government

---

# 🛡️ Insurance Industry - Complete Reference

## 📋 Functions (Step 1)

### Masking Functions

#### 1. mask_ssn_last4
```sql
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Mask SSN showing last 4 digits (XXX-XX-1234)'
RETURN CASE 
  WHEN ssn IS NULL THEN ssn 
  ELSE CONCAT('XXX-XX-', RIGHT(REPLACE(ssn, '-', ''), 4)) 
END;

-- Example: '123-45-6789' → 'XXX-XX-6789'
```

#### 2. mask_policy_number_last4
```sql
CREATE OR REPLACE FUNCTION mask_policy_number_last4(policy STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Mask policy number showing last 4 digits'
RETURN CASE 
  WHEN policy IS NULL THEN policy 
  ELSE CONCAT('****', RIGHT(policy, 4)) 
END;

-- Example: '172123456' → '****3456'
```

#### 3. mask_claim_amount_bucket
```sql
CREATE OR REPLACE FUNCTION mask_claim_amount_bucket(amt DECIMAL(12,2))
RETURNS STRING
COMMENT 'ABAC utility: Bucket claim amounts into ranges' 
RETURN CASE 
  WHEN amt IS NULL THEN 'Unknown' 
  WHEN amt < 1000 THEN '$0-$1K'
  WHEN amt < 5000 THEN '$1K-$5K' 
  WHEN amt < 10000 THEN '$5K-$10K' 
  ELSE '$10K+' 
END;

-- Example: 8500.00 → '$5K-$10K'
```

#### 4. mask_policyholder_id_hash
```sql
CREATE OR REPLACE FUNCTION mask_policyholder_id_hash(id STRING) 
RETURNS STRING
COMMENT 'ABAC utility: Deterministic policy holder ID masking for joins'
RETURN CONCAT('PH_', SUBSTRING(SHA2(id, 256), 1, 12));

-- Example: 'PH-1001' → 'PH_a1b2c3d4e5f6'
-- Note: Same input always produces same output (for joins)
```

#### 5. mask_email
```sql
CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask email local part'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN email NOT LIKE '%@%' THEN '****'
  ELSE CONCAT('****@', SPLIT(email, '@')[1])
END;

-- Example: 'john@email.com' → '****@email.com'
```

#### 6. mask_phone
```sql
CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'ABAC utility: Mask phone number showing last 4 digits'
RETURN CASE 
  WHEN phone IS NULL OR phone = '' THEN phone
  WHEN LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '')) < 4 THEN 'XXXX'
  ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4))
END;

-- Example: '246-555-0101' → 'XXXX0101'
```

### Row Filter Functions

#### 7. filter_business_hours
```sql
CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'ABAC utility: Allow access only during business hours'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 14 AND 22; -- adjusted for UTC

-- Use Case: Limit claim access to business hours only
```

#### 8. filter_high_value_claims
```sql
CREATE OR REPLACE FUNCTION filter_high_value_claims(amount DECIMAL(12,2))
RETURNS BOOLEAN
COMMENT 'ABAC utility: Filter out high-value claims'
RETURN amount > 5000;

-- Use Case: Managers see only high-value claims requiring approval
```

---

## 🏷️ Tag Policies (Step 2)

### pii_type_insurance
```
Tag Key: pii_type_insurance
Description: PII field types for insurance industry
Allowed Values:
  - ssn
  - email
  - phone
  - policy_number
  - amount
  - id
```

### data_classification_insurance
```
Tag Key: data_classification_insurance
Description: Data classification level for insurance industry
Allowed Values:
  - Confidential
  - Internal
  - Public
```

---

## 🔐 ABAC Policies (Step 3)

### Column Mask Policies

#### 1. ssn_mask
```sql
CREATE OR REPLACE POLICY ssn_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','ssn') AS ssn
ON COLUMN ssn;
```
**Effect:** Any column tagged `pii_type_insurance = 'ssn'` shows `XXX-XX-XXXX`

#### 2. policy_no_mask
```sql
CREATE OR REPLACE POLICY policy_no_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_policy_number_last4 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','policy_number') AS policy
ON COLUMN policy;
```
**Effect:** Any column tagged `pii_type_insurance = 'policy_number'` shows `****XXXX`

#### 3. email_mask
```sql
CREATE OR REPLACE POLICY email_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','email') AS email
ON COLUMN email;
```
**Effect:** Any column tagged `pii_type_insurance = 'email'` shows `****@domain.com`

#### 4. phone_mask
```sql
CREATE OR REPLACE POLICY phone_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','phone') AS phone
ON COLUMN phone;
```
**Effect:** Any column tagged `pii_type_insurance = 'phone'` shows `XXXXNNNN`

#### 5. policyholder_mask
```sql
CREATE OR REPLACE POLICY policyholder_mask ON SCHEMA {CATALOG}.{SCHEMA}
COLUMN MASK {CATALOG}.{SCHEMA}.mask_policyholder_id_hash 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','id') AS policyholder_id
ON COLUMN policyholder_id;
```
**Effect:** Any column tagged `pii_type_insurance = 'id'` shows `PH_XXXXXXXXXXXX` (hashed, deterministic)

### Row Filter Policies

#### 6. claims_filter
```sql
CREATE OR REPLACE POLICY claims_filter ON SCHEMA {CATALOG}.{SCHEMA}
ROW FILTER {CATALOG}.{SCHEMA}.filter_high_value_claims 
TO `account users`
FOR TABLES
MATCH COLUMNS
  hasTagValue('pii_type_insurance','amount') AS amount
USING COLUMNS (amount);
```
**Effect:** Only rows where `amount > 5000` are visible

---

## 📊 Test Tables (Step 4)

### policyholders_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| policyholder_id | STRING | pii_type_insurance = 'id' |
| first_name | STRING | - |
| last_name | STRING | - |
| ssn | STRING | pii_type_insurance = 'ssn', data_classification = 'Confidential' |
| email | STRING | pii_type_insurance = 'email' |
| phone | STRING | pii_type_insurance = 'phone' |

### policies_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| policy_id | STRING | - |
| policyholder_id | STRING | pii_type_insurance = 'id' |
| policy_number | STRING | pii_type_insurance = 'policy_number', data_classification_insurance = 'Confidential' |
| policy_type | STRING | - |
| premium | DECIMAL | - |
| coverage_amount | STRING | - |

### claims_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| claim_id | STRING | - |
| policy_id | STRING | - |
| claim_amount | STRING | pii_type_insurance = 'amount' |
| claim_date | DATE | - |
| status | STRING | - |

### premiums_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| payment_id | STRING | - |
| policy_id | STRING | - |
| amount | STRING | pii_type_insurance = 'amount' |
| payment_date | DATE | - |

---

## ✅ Compliance Mapping (Insurance)

| Regulation | How ABAC Helps |
|------------|----------------|
| **HIPAA** | PHI data in health insurance masked, SSN protected |
| **GLBA** | Customer financial data protected, policy details masked |
| **State Privacy Laws** | PII columns identified and masked per state requirements |
| **NAIC Model Laws** | Insurance-specific data governance compliance |

---

# 💰 Finance Industry - Complete Reference

## 📋 Functions (Step 1)

### Masking Functions

#### 1. mask_credit_card
```sql
CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'Masks credit card number showing only last 4 digits'
RETURN CONCAT('****-****-****-', SUBSTRING(card_number, -4, 4));

-- Example: '4532-1234-5678-9010' → '****-****-****-9010'
```

#### 2. mask_ssn_last4
```sql
CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING)
RETURNS STRING
COMMENT 'Masks SSN showing only last 4 digits'
RETURN CONCAT('***-**-', SUBSTRING(ssn, -4, 4));

-- Example: '123-45-6789' → '***-**-6789'
```

#### 3. mask_email
```sql
CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'Masks email local part, shows domain'
RETURN CONCAT('***@', SPLIT(email, '@')[1]);

-- Example: 'john.smith@company.com' → '***@company.com'
```

#### 4. mask_phone
```sql
CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'Masks phone number showing only last 4 digits'
RETURN CONCAT('***-***-', SUBSTRING(phone, -4, 4));

-- Example: '234-555-0101' → '***-***-0101'
```

#### 5. mask_account_last4
```sql
CREATE OR REPLACE FUNCTION mask_account_last4(account_number STRING)
RETURNS STRING
COMMENT 'Masks account number showing only last 4 digits'
RETURN CONCAT('********', SUBSTRING(account_number, -4, 4));

-- Example: '1001234567' → '********4567'
```

#### 6. mask_routing_number
```sql
CREATE OR REPLACE FUNCTION mask_routing_number(routing_number STRING)
RETURNS STRING
COMMENT 'Masks routing number showing only last 2 digits'
RETURN CONCAT('*******', SUBSTRING(routing_number, -2, 2));

-- Example: '021000021' → '*******21'
```

#### 7. mask_ip_address
```sql
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'Masks IP address to subnet level'
RETURN CONCAT(SPLIT(ip, '\\.')[0], '.', SPLIT(ip, '\\.')[1], '.', '***', '.', '***');

-- Example: '192.168.1.100' → '192.168.***.***'
```

#### 8. mask_income_bracket
```sql
CREATE OR REPLACE FUNCTION mask_income_bracket(income DECIMAL(18,2))
RETURNS DECIMAL(18,2)
COMMENT 'Masks income by returning 0 for privacy'
RETURN CAST(0 AS DECIMAL(18,2));

-- Example: 75000.00 → 0.00
```

### Row Filter Functions

#### 9. filter_fraud_flagged_only
```sql
CREATE OR REPLACE FUNCTION filter_fraud_flagged_only(fraud_flag BOOLEAN)
RETURNS BOOLEAN
COMMENT 'Row filter to show only fraud-flagged transactions'
RETURN fraud_flag = TRUE;

-- Use Case: Compliance team sees only suspicious transactions
```

#### 10. filter_high_value_transactions
```sql
CREATE OR REPLACE FUNCTION filter_high_value_transactions(amount DECIMAL(18,2))
RETURNS BOOLEAN
COMMENT 'Row filter for transactions over $5000'
RETURN amount > 5000;

-- Use Case: Managers see only high-value transactions requiring approval
```

---

## 🏷️ Tag Policies (Step 2)

Tag policies are defined at the **account level** and define what tags can be applied.

### pii_type_finance
```
Tag Key: pii_type_finance
Description: PII field types for finance industry
Allowed Values:
  - ssn
  - email
  - location
  - phone
  - income
  - account
  - routing_number
  - ip_address
  - credit_card
  - transaction_amount
  - transaction_id
  - id
```

### pci_compliance_finance
```
Tag Key: pci_compliance_finance
Description: PCI-DSS compliance requirement for finance
Allowed Values:
  - Required
  - Not_Required
```

### data_classification_finance
```
Tag Key: data_classification_finance
Description: Data classification level for finance
Allowed Values:
  - Confidential
  - Internal
  - Public
```

### fraud_detection_finance
```
Tag Key: fraud_detection_finance
Description: Fraud detection flag for finance
Allowed Values:
  - true
  - false
```

---

## 🔐 ABAC Policies (Step 3)

ABAC policies apply masking functions based on column tags.

### Column Mask Policies

#### 1. ssn_mask
```sql
CREATE OR REPLACE POLICY ssn_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask SSN columns tagged with pii_type_finance=ssn'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn_last4
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'ssn') AS ssn_col
ON COLUMN ssn_col;
```
**Effect:** Any column tagged `pii_type_finance = 'ssn'` shows `***-**-XXXX`

#### 2. email_mask
```sql
CREATE OR REPLACE POLICY email_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask email columns tagged with pii_type_finance=email'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'email') AS email_col
ON COLUMN email_col;
```
**Effect:** Any column tagged `pii_type_finance = 'email'` shows `***@domain.com`

#### 3. phone_mask
```sql
CREATE OR REPLACE POLICY phone_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask phone columns tagged with pii_type_finance=phone'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'phone') AS phone_col
ON COLUMN phone_col;
```
**Effect:** Any column tagged `pii_type_finance = 'phone'` shows `***-***-XXXX`

#### 4. card_mask
```sql
CREATE OR REPLACE POLICY card_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask credit card columns tagged with pii_type_finance=credit_card'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_credit_card
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'credit_card') AS card_col
ON COLUMN card_col;
```
**Effect:** Any column tagged `pii_type_finance = 'credit_card'` shows `****-****-****-XXXX`

#### 5. account_mask
```sql
CREATE OR REPLACE POLICY account_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask account columns tagged with pii_type_finance=account'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_account_last4
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'account') AS account_col
ON COLUMN account_col;
```
**Effect:** Any column tagged `pii_type_finance = 'account'` shows `********XXXX`

#### 6. income_mask
```sql
CREATE OR REPLACE POLICY income_mask
ON SCHEMA {CATALOG}.{SCHEMA}
COMMENT 'Mask income columns tagged with pii_type_finance=income'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_income_bracket
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type_finance', 'income') AS income_col
ON COLUMN income_col;
```
**Effect:** Any column tagged `pii_type_finance = 'income'` shows `0.00`

---

## 📊 Test Tables (Step 4)

### customers_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| customer_id | STRING | pii_type_finance = 'id' |
| first_name | STRING | - |
| last_name | STRING | - |
| ssn | STRING | pii_type_finance = 'ssn', pci_compliance_finance = 'Required' |
| email | STRING | pii_type_finance = 'email' |
| phone | STRING | pii_type_finance = 'phone' |
| annual_income | DECIMAL | pii_type_finance = 'income', data_classification_finance = 'Confidential' |

### accounts_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| account_id | STRING | - |
| customer_id | STRING | pii_type_finance = 'id' |
| account_number | STRING | pii_type_finance = 'account', data_classification_finance = 'Confidential' |
| routing_number | STRING | pii_type_finance = 'routing_number' |
| balance | DECIMAL | - |

### credit_cards_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| card_id | STRING | - |
| customer_id | STRING | pii_type_finance = 'id' |
| card_number | STRING | pii_type_finance = 'credit_card', pci_compliance_finance = 'Required' |
| credit_limit | DECIMAL | - |

### transactions_test
| Column | Type | Tags Applied |
|--------|------|--------------|
| transaction_id | STRING | pii_type_finance = 'transaction_id' |
| customer_id | STRING | pii_type_finance = 'id' |
| amount | DECIMAL | pii_type_finance = 'transaction_amount' |
| ip_address | STRING | pii_type_finance = 'ip_address' |
| fraud_flag | BOOLEAN | fraud_detection_finance = 'true' |

---

## ✅ Compliance Mapping

| Regulation | How ABAC Helps |
|------------|----------------|
| **PCI-DSS** | Credit card & account numbers masked, tagged with `pci_compliance_finance = 'Required'` |
| **GLBA** | Customer financial data protected, income/account details masked |
| **SOX** | Audit trail via ABAC policies, role-based access to financial data |
| **GDPR** | Email/phone masking, right to be forgotten supported by tags |
| **CCPA** | PII columns identified and masked for California residents |

---

## 🔗 Quick Links

- [ABAC Overview](https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/)
- [Create ABAC Policies](https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/policies)
- [Governed Tags](https://docs.databricks.com/aws/en/data-governance/unity-catalog/tags.html)
- [UDFs in Unity Catalog](https://docs.databricks.com/sql/language-manual/sql-ref-functions-udf.html)
"""

