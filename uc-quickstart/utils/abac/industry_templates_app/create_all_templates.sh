#!/bin/bash

# Create industry templates by reading SQL files directly

BASE_DIR="/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates"
OUT_DIR="/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates_app/industries"

echo "Creating industry template files..."

# Healthcare
echo "Processing Healthcare..."
python3 << 'HEALTHCARE_EOF'
import sys
sys.path.insert(0, '/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates_app/industries')

# Read SQL files
with open('/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates/healthcare/sql/0.1healthcare_abac_functions_updated.sql', 'r') as f:
    functions_sql = f.read()

with open('/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates/healthcare/sql/0.2healthcare_database_schema_updated.sql', 'r') as f:
    schema_sql = f.read()

with open('/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates/healthcare/sql/3.ApplyHealthcareSetTags.sql', 'r') as f:
    tags_sql = f.read()

with open('/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates/healthcare/sql/4.2.CreateHealthcareABACPolicies_BuiltInGroups.sql', 'r') as f:
    abac_sql = f.read()

# Create template
template = f'''"""
Healthcare Industry ABAC Template

This module contains all SQL definitions for the healthcare industry ABAC setup.
"""

INDUSTRY_NAME = "Healthcare"
INDUSTRY_DESCRIPTION = "Healthcare/medical data protection with HIPAA compliance"

# Step 1: Masking/Filtering Functions
FUNCTIONS_SQL = """
{functions_sql.strip()}
"""

# Step 2: Tag Policy Definitions
TAG_DEFINITIONS = [
    ("pii_type_healthcare", "Healthcare PII data types", [
        "patient_name", "patient_id", "ssn", "dob", "email", "phone", 
        "address", "medical_record_number", "diagnosis", "treatment"
    ]),
    ("phi_level_healthcare", "Protected Health Information level", [
        "High", "Medium", "Low", "Public"
    ]),
    ("hipaa_compliance_healthcare", "HIPAA compliance requirement", [
        "Required", "Not_Required"
    ]),
    ("data_sensitivity_healthcare", "Data sensitivity classification", [
        "Highly_Sensitive", "Sensitive", "Internal", "Public"
    ]),
]

# Step 3: ABAC Policies
ABAC_POLICIES_SQL = """
{abac_sql.strip()}
"""

# Step 4: Test Tables SQL
TEST_TABLES_SQL = """
{schema_sql.strip()}
"""

# Step 5: Tag Applications SQL
TAG_APPLICATIONS_SQL = """
{tags_sql.strip()}
"""

# List of test tables
TEST_TABLES = ["patients_test", "medical_records_test", "prescriptions_test", 
               "lab_results_test", "providers_test", "appointments_test"]
'''

# Write template file
with open('/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates_app/industries/healthcare_template.py', 'w') as f:
    f.write(template)

print("✅ Healthcare template created")
HEALTHCARE_EOF

echo "Done!"

