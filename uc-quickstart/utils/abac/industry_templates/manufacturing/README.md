# Manufacturing ABAC Demo

## 🎯 Overview
A comprehensive Attribute-Based Access Control (ABAC) demonstration for manufacturing industry data governance using Databricks Unity Catalog.

## 📊 Contents

### 📊 Data (12 Tables)
| Table | Description |
|-------|-------------|
| `assets` | Manufacturing asset master data |
| `maintenance_events` | Maintenance activities with PII |
| `product_specs` | Product specifications (sensitive IP) |
| `shipments` | Supplier shipments with costs |
| `employee_contacts` | Employee PII data |
| `performance_metrics` | Asset performance data |
| `sensors` | Sensors mounted to assets |
| `production_runs` | Production runs by asset, site, and shift |
| `work_orders` | Maintenance work orders with scheduling |
| `quality_inspections` | Quality inspections for production runs |
| `suppliers` | Suppliers supporting plants |
| `bom` | Bill of materials linking assets to supplier parts |


### 🔐 Masking Functions (14)
**Column Masks:**
- `mask_email(email)` - Email masking (user@domain.com → ****@domain.com)
- `mask_phone(phone)` - Phone masking (123-555-1234 → XXXX1234)
- `mask_spec_text(text)` - Spec redaction (Full text → REDACTED_SPEC)
- `mask_cad_reference(uri)` - CAD URI hashing (s3://path → sha256:...)
- `mask_timestamp_15min(ts)` - Timestamp rounding (to 15-min intervals)
- `mask_string_hash(str)` - String hashing (SHA-256)
- `mask_serial_last4(serial)` - Serial masking (last 4 only)
- `mask_gps_precision(lat,lon)` - GPS coordinate rounding
- `mask_cost_bucket(amount)` - Cost bucketing ($0-$100, $100-$500, etc.)
- `mask_string_partial(str)` - Partial string masking
- `mask_decimal_referential(num)` - Deterministic number masking

**Row Filters:**
- `business_hours_filter()` - Restrict to business hours
- `maintenance_hours_filter()` - Maintenance window access
- `no_rows_filter()` - Complete denial

### 🏷️ Tags Applied
| Tag Key | Values | Applied To |
|---------|--------|------------|
| `ip_sensitivity_manufacturing` | Internal, Trade_Secret, Public |
| `sensitive_type_manufacturing` | name, gps, cost, phone, email, serial_number |
| `data_purpose_manufacturing` | Operations, Quality, Maintenance, SupplyChain, Audit, RnD |
| `shift_hours_manufacturing` | Day, Swing, Night, Emergency_24x7 |
| `asset_criticality_manufacturing` | High, Medium, Low |
| `export_control_manufacturing` | ITAR", EAR99, Not_Controlled |
| `data_residency_manufacturing` | Country_Only, EU_Only, Cross_Border_Approved |
| `supplier_scope_manufacturing` | Named_Supplier_Only, All_Suppliers, Audit_Project_Only |


## 🎭 Masking Examples

### Email Masking
```sql
SELECT 
  technician_email AS original,
  manufacturing.mask_email(technician_email) AS masked
FROM maintenance_events;
```
**Result:** `mike.a@plantA.com` → `****@plantA.com`

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



## 📁 File Structure
```
manufacturing/
├── config.yaml                          # Configuration (edit this!)
├── 1_Create_Functions.ipynb             # Notebook: Create masking + filtering functions
├── 2_Create_Tables.ipynb                # Notebook: Create schema & tables
├── 3_Setup_Tagging.ipynb                # Notebook: Define governed tags
├── 4_Test_ABAC_Policies.ipynb           # Notebook: Test functions through ABAC policies
├── 5_Cleanup.ipynb                      # Notebook: Cleanup test tables, tag policies, and ABAC policies
├── README.md                            # This file
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



## 📊 Test Results

```
✅ 12 tables created
✅ 14 masking/filter functions deployed
✅ 8 tags applied to sensitive columns
✅ Email: mike.a@plantA.com → ****@plantA.com
✅ Spec: Full text → REDACTED_SPEC
✅ CAD: s3://cad/... → sha256:...
✅ Timestamp: 08:03:27 → 08:00:00
```

## 🚦 Next Steps

1. **Add More Tables**: Extend schema with `quality_inspections`, `work_orders`, etc.
2. **Create Groups**: Have admin create `users` and `admins` workspace groups
3. **Test Access**: Verify masking works for different user groups
4. **Production**: Adapt to your actual manufacturing data model

## 📚 References
- [Unity Catalog ABAC Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/)
- [Column Masks + Row Filters](https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks)

---
