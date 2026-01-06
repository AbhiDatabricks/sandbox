# Industry Templates

This folder contains modular industry-specific ABAC templates. Each industry has its own file with all necessary SQL definitions.

## Structure

Each industry template file must define these variables:

```python
# industries/<industry>_template.py

# Required: Industry metadata
INDUSTRY_NAME = "Industry Name"
INDUSTRY_DESCRIPTION = "Brief description"

# Required: Step 1 - Masking/filtering functions
FUNCTIONS_SQL = """
CREATE OR REPLACE FUNCTION mask_xxx(...)
...
"""

# Required: Step 2 - Tag policy definitions
TAG_DEFINITIONS = [
    ("tag_key", "description", ["value1", "value2"]),
    ...
]

# Required: Step 3 - ABAC policies (at Catalog level)
ABAC_POLICIES_SQL = """
CREATE POLICY IF NOT EXISTS xxx ON CATALOG {CATALOG}
  COLUMN MASK {CATALOG}.{SCHEMA}.mask_xxx
  ...
"""

# Optional: Step 4 - Test data (with _test suffix)
TEST_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS xxx_test (...)
INSERT INTO xxx_test VALUES (...)
"""

# Optional: Step 5 - Tag applications for test tables
TAG_APPLICATIONS_SQL = """
ALTER TABLE xxx ALTER COLUMN yyy SET TAGS (...)
"""

# Optional: List of test tables created
TEST_TABLES = ["table1_test", "table2_test"]
```

## Adding a New Industry

To add a new industry (e.g., Healthcare):

1. **Create the template file**:
   ```
   industries/healthcare_template.py
   ```

2. **Define all required variables** (see structure above)

3. **Test locally** if possible

4. **Deploy**: The app will automatically detect and load the new industry!

## Current Industries

- **Default** (`default_template.py`) ⭐ **SUPER-SET** - Comprehensive template with maximum coverage:
  - 20 column masking functions
  - 8 row filter functions
  - 8 tag policies (generic names, no industry suffix)
  - 15 ABAC policies
  - 5 test tables (users, transactions, employees, assets, audit_log)
- **Finance** (`finance_template.py`) - Banking, credit cards, transactions
- **Insurance** (`insurance_template.py`) - Policies, claims, underwriting
- **Healthcare** (`healthcare_template.py`) - Medical records, HIPAA compliance
- **Manufacturing** (`manufacturing_template.py`) - Supply chain, IP protection
- **Retail** (`retail_template.py`) - E-commerce, customer data
- **Telco** (`telco_template.py`) - Subscriber data, call records
- **Government** (`government_template.py`) - Security clearances, CUI

## Notes

- **Default uses generic tag names**: No industry suffix (e.g., `pii_type` not `pii_type_finance`)
- **Industry templates use industry-specific suffix**: e.g., `pii_type_finance`, `pii_type_healthcare`
- **Use placeholders**: `{CATALOG}` and `{SCHEMA}` are replaced at runtime
- **Test tables use _test suffix**: Keeps test data separate from production
- **Fully qualified names**: All functions/policies use `catalog.schema.name` format

