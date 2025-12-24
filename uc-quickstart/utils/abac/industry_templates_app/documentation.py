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
✅ **Permissions** to create:
   - Functions in target catalog/schema
   - Tag policies (account-level admin for Step 2)
   - ABAC policies on schemas
   - Tables in target catalog/schema \n
✅ **SQL Warehouse** configured (app uses this for execution)  
✅ **Target catalog and schema** (or permission to create new schema) \n
✅ **Permissions** to grant the above priveleges to the app service principal
  - grant use catalog on catalog CATALOG to `SP-ID`;
  - grant use schema on schema CATALOG.SCHEMA to `SP-ID`;
  - grant create function on schema CATALOG.SCHEMA to `SP-ID`;
  - grant create table on schema CATALOG.SCHEMA to `SP-ID`;


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
- Retail/Telco/Government: In development

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

### Retail ⚙️ Partial
**Use Cases:** E-commerce, customer data, loyalty programs

**Functions:** 11 masking functions  
**Tags:** 4 tag policies  
**ABAC Policies:** In development

---

### Telco ⚙️ Partial
**Use Cases:** Subscriber data, call records, GDPR compliance

**Functions:** 8 masking functions  
**Tags:** 4 tag policies  
**ABAC Policies:** In development

---

### Government ⚙️ Partial
**Use Cases:** Security clearances, classified data, CUI

**Functions:** 8 masking functions  
**Tags:** 4 tag policies  
**ABAC Policies:** In development

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

**Version:** 1.0  
**Last Updated:** December 2025  
**Supported Industries:** Finance, Healthcare, Manufacturing, Retail, Telco, Government

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

