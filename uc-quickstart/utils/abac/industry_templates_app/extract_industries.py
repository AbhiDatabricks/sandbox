#!/usr/bin/env python3
"""
Extract industry templates from notebooks/SQL files and create modular template files
"""
import os
from pathlib import Path
import re

# Industry configurations
INDUSTRIES = {
    "government": {
        "sql_dir": "../../industry_templates/government/sql",
        "functions_file": "0.1government_abac_functions.sql",
        "schema_file": "0.2government_database_schema.sql",
        "extended_file": "0.3government_extended_tables.sql",
        "test_file": "6.TestGovernmentData_Simple.sql",
    },
    "healthcare": {
        "sql_dir": "../../industry_templates/healthcare/sql",
        "functions_file": "0.1healthcare_abac_functions_updated.sql",
        "schema_file": "0.2healthcare_database_schema_updated.sql",
        "tags_file": "3.ApplyHealthcareSetTags.sql",
        "abac_file": "4.2.CreateHealthcareABACPolicies_BuiltInGroups.sql",
        "test_file": "6.TestHealthcareData_Simple.sql",
    },
    "insurance": {
        "sql_dir": "../../industry_templates/insurance",
        "notebook_based": True,  # Extract from notebooks
    },
    "manufacturing": {
        "sql_dir": "../../industry_templates/manufacturing/sql",
        "functions_file": "0.1manufacturing_abac_functions.sql",
        "schema_file": "0.2manufacturing_database_schema.sql",
        "extended_file": "0.3manufacturing_extended_schema.sql",
        "tags_file": "0.4apply_tags.sql",
        "abac_file": "4.2.CreateManufacturingABACPolicies_BuiltInGroups.sql",
        "test_file": "7.TestManufacturingData_Simple.sql",
    },
    "retail": {
        "sql_dir": "../../industry_templates/retail/sql",
        "functions_file": "0.1retail_abac_functions.sql",
        "schema_file": "0.2retail_database_schema.sql",
        "extended_file": "0.3retail_extended_tables.sql",
        "test_file": "6.TestRetailData_Simple.sql",
    },
    "telco": {
        "sql_dir": "../../industry_templates/telco/sql",
        "functions_file": "0.1telco_abac_functions.sql",
        "schema_file": "0.2telco_database_schema.sql",
        "extended_file": "0.3telco_extended_tables.sql",
        "test_file": "6.TestTelcoData_Simple.sql",
    },
}

def read_sql_file(base_path, relative_path):
    """Read SQL file and return content"""
    file_path = Path(base_path) / relative_path
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def extract_tag_definitions_from_python(script_path):
    """Extract tag definitions from Python tag policy creation script"""
    if not os.path.exists(script_path):
        return []
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse tag definitions (simple pattern matching)
    tags = []
    # This is a placeholder - actual extraction would need to parse the Python file
    return tags

def create_template_file(industry_name, config):
    """Create a Python template file for an industry"""
    print(f"\n{'='*60}")
    print(f"Processing: {industry_name.upper()}")
    print(f"{'='*60}")
    
    base_path = Path(__file__).parent
    sql_dir = base_path / config["sql_dir"]
    
    # Read SQL files
    functions_sql = ""
    schema_sql = ""
    extended_sql = ""
    tags_sql = ""
    abac_sql = ""
    test_sql = ""
    
    if config.get("functions_file"):
        functions_sql = read_sql_file(sql_dir, config["functions_file"]) or ""
        print(f"✓ Functions: {len(functions_sql)} chars")
    
    if config.get("schema_file"):
        schema_sql = read_sql_file(sql_dir, config["schema_file"]) or ""
        print(f"✓ Schema: {len(schema_sql)} chars")
    
    if config.get("extended_file"):
        extended_sql = read_sql_file(sql_dir, config["extended_file"]) or ""
        print(f"✓ Extended: {len(extended_sql)} chars")
    
    if config.get("tags_file"):
        tags_sql = read_sql_file(sql_dir, config["tags_file"]) or ""
        print(f"✓ Tags: {len(tags_sql)} chars")
    
    if config.get("abac_file"):
        abac_sql = read_sql_file(sql_dir, config["abac_file"]) or ""
        print(f"✓ ABAC: {len(abac_sql)} chars")
    
    if config.get("test_file"):
        test_sql = read_sql_file(sql_dir, config["test_file"]) or ""
        print(f"✓ Test: {len(test_sql)} chars")
    
    # Combine schema and extended for test tables
    test_tables_sql = schema_sql
    if extended_sql:
        test_tables_sql += "\n\n" + extended_sql
    
    # Extract table names for TEST_TABLES list
    table_pattern = r'CREATE TABLE (?:IF NOT EXISTS )?(\w+)'
    tables = re.findall(table_pattern, test_tables_sql, re.IGNORECASE)
    test_tables = [f"{t}_test" for t in tables if t.lower() not in ['if', 'not', 'exists']]
    
    # Generate Python template
    template_content = f'''"""
{industry_name.capitalize()} Industry ABAC Template

This module contains all SQL definitions for the {industry_name} industry ABAC setup.
"""

INDUSTRY_NAME = "{industry_name.capitalize()}"
INDUSTRY_DESCRIPTION = "{industry_name.capitalize()} industry ABAC policies and masking functions"

# Step 1: Masking/Filtering Functions
FUNCTIONS_SQL = """
{functions_sql.strip()}
"""

# Step 2: Tag Policy Definitions
# Format: (tag_key, description, [allowed_values])
TAG_DEFINITIONS = [
    ("pii_type_{industry_name}", "PII data types for {industry_name}", [
        "email", "phone", "ssn", "name", "address", "dob", "id"
    ]),
    ("data_classification_{industry_name}", "Data classification levels", [
        "Public", "Internal", "Confidential", "Restricted"
    ]),
    ("compliance_required_{industry_name}", "Compliance requirements", [
        "Required", "Not_Required"
    ]),
]

# Step 3: ABAC Policies
ABAC_POLICIES_SQL = """
{abac_sql.strip() if abac_sql else "-- ABAC policies to be defined"}
"""

# Step 4: Test Tables SQL (Optional)
TEST_TABLES_SQL = """
{test_tables_sql.strip()}
"""

# Step 5: Tag Applications SQL (Optional)
TAG_APPLICATIONS_SQL = """
{tags_sql.strip() if tags_sql else "-- Tag applications to be defined"}
"""

# List of test tables created
TEST_TABLES = {test_tables[:10]}  # Limited to first 10
'''
    
    # Write template file
    output_file = base_path / "industries" / f"{industry_name}_template.py"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ Created: {output_file}")
    print(f"   Tables: {len(test_tables)}")
    
    return output_file

def main():
    """Main extraction function"""
    print("="*60)
    print("EXTRACTING INDUSTRY TEMPLATES")
    print("="*60)
    
    created_files = []
    
    for industry, config in INDUSTRIES.items():
        if config.get("notebook_based"):
            print(f"\n⚠️  {industry.upper()}: Skipping (notebook-based, needs manual extraction)")
            continue
        
        try:
            output_file = create_template_file(industry, config)
            created_files.append(output_file)
        except Exception as e:
            print(f"❌ Error processing {industry}: {e}")
    
    print("\n" + "="*60)
    print(f"✅ EXTRACTION COMPLETE: {len(created_files)} industries")
    print("="*60)
    print("\nCreated files:")
    for f in created_files:
        print(f"  - {f.name}")
    
    print("\nNext steps:")
    print("1. Review generated template files")
    print("2. Update TAG_DEFINITIONS for each industry")
    print("3. Add missing ABAC_POLICIES_SQL where needed")
    print("4. Test in the app UI")

if __name__ == "__main__":
    main()

