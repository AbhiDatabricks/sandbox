# Manufacturing ABAC Demo

## 🎯 Overview
A comprehensive Attribute-Based Access Control (ABAC) demonstration for manufacturing industry data governance using Databricks Unity Catalog.

## 📊 Contents

### 📊 Data (6 Tables, 153 Rows)
| Table | Rows | Description |
|-------|------|-------------|
| `assets` | 3 | Manufacturing asset master data |
| `maintenance_events` | 50 | Maintenance activities with PII |
| `product_specs` | 25 | Product specifications (sensitive IP) |
| `shipments` | 25 | Supplier shipments with costs |
| `employee_contacts` | 25 | Employee PII data |
| `performance_metrics` | 25 | Asset performance data |

### 🔐 Masking Functions (17)
**Column Masks:**
- `mask_email(email)` - Email masking (user@domain.com → ****@domain.com)
- `mask_phone(phone)` - Phone masking (555-1234 → XXXX1234)
- `mask_spec_text(text)` - Spec redaction (Full text → REDACTED_SPEC)
- `mask_cad_reference(uri)` - CAD URI hashing (s3://path → sha256:...)
- `mask_timestamp_15min(ts)` - Timestamp rounding (to 15-min intervals)
- `mask_string_hash(str)` - String hashing (SHA-256)
- `mask_serial_last4(serial)` - Serial masking (last 4 only)
- `mask_gps_precision(lat,lon)` - GPS coordinate rounding
- `mask_cost_bucket(amount)` - Cost bucketing ($0-$100, $100-$500, etc.)
- `mask_string_partial(str)` - Partial string masking
- `mask_id_referential(id)` - Deterministic ID masking
- `mask_decimal_referential(num)` - Deterministic number masking

**Row Filters:**
- `business_hours_filter()` - Restrict to business hours
- `maintenance_hours_filter()` - Maintenance window access
- `sensitive_asset_filter()` - Asset-level filtering
- `quality_nc_only()` - Non-conformance filtering
- `no_rows()` - Complete denial

### 🏷️ Tags Applied
| Tag Key | Values | Applied To |
|---------|--------|------------|
| `ip_sensitivity` | Internal, Trade_Secret, Public | emails, phones, specs, CAD |
| `asset_criticality` | High, Medium, Low | asset_id, timestamps |
| `data_purpose` | Production, Quality, Maintenance | - |

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
catalog: "apscat"
schema: "manufacturing"
```

### Deploy
```bash
cd uc-quickstart/utils/abac/manufacturing
python3 execute_sql_configurable.py
```

## 🎭 Masking Examples

### Email Masking
```sql
SELECT 
  technician_email AS original,
  apscat.manufacturing.mask_email(technician_email) AS masked
FROM maintenance_events;
```
**Result:** `mike.a@plantA.com` → `****@plantA.com`

### Phone Masking
```sql
SELECT 
  phone AS original,
  apscat.manufacturing.mask_phone(phone) AS masked
FROM employee_contacts;
```
**Result:** `555-1001` → `XXXX1001`

### Spec Text Redaction
```sql
SELECT 
  spec_text AS original,
  apscat.manufacturing.mask_spec_text(spec_text) AS redacted
FROM product_specs;
```
**Result:** `Proprietary aluminum alloy...` → `REDACTED_SPEC`

### CAD URI Hashing
```sql
SELECT 
  cad_file_uri AS original,
  apscat.manufacturing.mask_cad_reference(cad_file_uri) AS hashed
FROM product_specs;
```
**Result:** `s3://cad/widget-alpha.dwg` → `ed89234abc3ea4df...`

### Timestamp Rounding
```sql
SELECT 
  start_time AS original,
  apscat.manufacturing.mask_timestamp_15min(start_time) AS rounded
FROM maintenance_events;
```
**Result:** `2024-03-01 08:03:27` → `2024-03-01 08:00:00`

## 🧪 Testing

### Run Verification Tests
```bash
# Via Python SDK
python3 -c "
from databricks.sdk import WorkspaceClient
import os
os.environ['DATABRICKS_CONFIG_PROFILE'] = 'DEFAULT'
w = WorkspaceClient()

result = w.statement_execution.execute_statement(
    warehouse_id='862f1d757f0424f7',
    statement='SELECT COUNT(*) FROM apscat.manufacturing.maintenance_events',
    catalog='apscat',
    schema='manufacturing'
)
print(result.result.data_array[0][0])
"
```

### Test Queries
See `7.TestManufacturingData_Simple.sql` for comprehensive test queries.

## 📋 ABAC Policies (Optional)

### Note on Groups
ABAC policies require workspace groups (`users`, `admins`) to be created by a workspace administrator. 

Without policies, masking functions can be called manually in queries:
```sql
SELECT mask_email(email) FROM employee_contacts;
```

With policies (requires admin), masking is automatic:
```sql
-- As regular user: emails are automatically masked
SELECT email FROM employee_contacts;

-- As admin: emails are visible
SELECT email FROM employee_contacts;
```

### Policy Example
```sql
CREATE OR REPLACE POLICY mfg_email_masking
ON SCHEMA apscat.manufacturing
COMMENT 'Mask emails for regular users'
COLUMN MASK apscat.manufacturing.mask_email
TO `users`
FOR TABLES
MATCH COLUMNS hasTagValue('ip_sensitivity','Internal') AS email_cols
ON COLUMN email_cols;
```

## 📁 File Structure
```
manufacturing/
├── config.yaml                              # Deployment configuration
├── execute_sql_configurable.py              # Config-driven deployment script
├── 0.1manufacturing_abac_functions.sql      # Masking/filter functions
├── 0.2manufacturing_database_schema.sql     # Base tables (assets, etc.)
├── 0.3manufacturing_extended_schema.sql     # Additional 5 tables
├── 0.4apply_tags.sql                        # Apply tags to columns
├── 4.2.CreateManufacturingABACPolicies_BuiltInGroups.sql  # ABAC policies (optional)
├── 7.TestManufacturingData_Simple.sql       # Verification tests
└── README.md                                # This file
```

## 🎓 Key Concepts

### 1. Attribute-Based Access Control (ABAC)
- **Tags**: Metadata labels on columns (e.g., `ip_sensitivity=Internal`)
- **Policies**: Rules that bind masking functions to tagged columns for specific groups
- **Dynamic**: No code changes needed; just update tags or group membership

### 2. Masking Functions
- **Column Masks**: Transform data (e.g., hash, redact, partial mask)
- **Row Filters**: Hide entire rows based on conditions
- **Deterministic**: Same input always produces same output (for joins)

### 3. Unity Catalog Tags
- **Tag Policies**: Define allowed tag values
- **Column Tags**: Applied via `ALTER TABLE ... ALTER COLUMN ... SET TAGS`
- **Policy Binding**: Policies match columns using `hasTagValue('tag_key', 'tag_value')`

## 🔧 Troubleshooting

### Issue: Tables not created
**Solution:** Remove `DEFAULT CURRENT_TIMESTAMP()` from CREATE TABLE statements (compatibility issue)

### Issue: Tags not applying
**Solution:** Ensure tag policies exist first:
```sql
CREATE TAG POLICY IF NOT EXISTS ip_sensitivity 
ALLOWED VALUES ['Internal', 'Trade_Secret', 'Public'];
```

### Issue: Policies failing
**Solution:** 
1. Check if groups exist: `SHOW GROUPS`
2. Verify admin permissions to create policies
3. Test functions manually without policies first

### Issue: Warehouse not found
**Solution:** Update `config.yaml` with your warehouse ID:
```bash
databricks warehouses list --profile DEFAULT
```

## 📊 Test Results

```
✅ 6 tables created with 153 total rows
✅ 17 masking/filter functions deployed
✅ 7 tags applied to sensitive columns
✅ Email: mike.a@plantA.com → ****@plantA.com
✅ Phone: 555-1001 → XXXX1001
✅ Spec: Full text → REDACTED_SPEC
✅ CAD: s3://cad/... → sha256:...
✅ Timestamp: 08:03:27 → 08:00:00
```

## 🚦 Next Steps

1. **Add More Tables**: Extend schema with `quality_inspections`, `work_orders`, etc.
2. **Create Groups**: Have admin create `users` and `admins` workspace groups
3. **Apply Policies**: Bind masking functions via ABAC policies
4. **Test Access**: Verify masking works for different user groups
5. **Production**: Adapt to your actual manufacturing data model

## 📚 References
- [Unity Catalog ABAC Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/attribute-based-access-control.html)
- [Column Masking](https://docs.databricks.com/en/data-governance/unity-catalog/column-masks.html)
- [Row Filters](https://docs.databricks.com/en/data-governance/unity-catalog/row-filters.html)

---
**Status**: ✅ Fully deployed and tested (2024)
