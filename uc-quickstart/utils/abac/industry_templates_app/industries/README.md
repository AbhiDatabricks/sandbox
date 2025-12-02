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

# Required: Step 3 - ABAC policies
ABAC_POLICIES_SQL = """
CREATE POLICY IF NOT EXISTS xxx ON SCHEMA {SCHEMA}
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

- **Finance** (`finance_template.py`) - Banking, credit cards, transactions

## Coming Soon

- Healthcare
- Retail
- Manufacturing
- Government
- Telco
- Insurance

## Notes

- **Tag keys should be industry-specific**: Use suffix like `_finance`, `_healthcare` to avoid conflicts
- **Use placeholders**: `{CATALOG}` and `{SCHEMA}` are replaced at runtime
- **Test tables use _test suffix**: Keeps test data separate from production
- **Fully qualified names**: All functions/policies use `catalog.schema.name` format

