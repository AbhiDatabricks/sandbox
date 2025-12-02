#!/usr/bin/env python3
"""
Generate industry template files from SQL sources
"""
from pathlib import Path

BASE_DIR = Path("/Users/abhishekpratap.singh/APSProjects/sandbox-1/uc-quickstart/utils/abac/industry_templates")
OUT_DIR = Path(__file__).parent / "industries"

def read_sql(path):
    """Read SQL file safely"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"  ⚠️  Could not read {path}: {e}")
        return ""

def create_healthcare():
    """Create Healthcare template"""
    print("\n📋 Healthcare")
    sql_dir = BASE_DIR / "healthcare" / "sql"
    
    functions = read_sql(sql_dir / "0.1healthcare_abac_functions_updated.sql")
    schema = read_sql(sql_dir / "0.2healthcare_database_schema_updated.sql")
    tags = read_sql(sql_dir / "3.ApplyHealthcareSetTags.sql")
    abac = read_sql(sql_dir / "4.2.CreateHealthcareABACPolicies_BuiltInGroups.sql")
    
    template = f'''"""
Healthcare Industry ABAC Template
"""

INDUSTRY_NAME = "Healthcare"
INDUSTRY_DESCRIPTION = "Healthcare/medical data protection with HIPAA compliance"

FUNCTIONS_SQL = """
{functions}
"""

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

ABAC_POLICIES_SQL = """
{abac}
"""

TEST_TABLES_SQL = """
{schema}
"""

TAG_APPLICATIONS_SQL = """
{tags}
"""

TEST_TABLES = ["patients_test", "medical_records_test", "prescriptions_test", 
               "lab_results_test", "providers_test", "appointments_test"]
'''
    
    output = OUT_DIR / "healthcare_template.py"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"  ✅ Created {output.name}")

def create_manufacturing():
    """Create Manufacturing template"""
    print("\n📋 Manufacturing")
    sql_dir = BASE_DIR / "manufacturing" / "sql"
    
    functions = read_sql(sql_dir / "0.1manufacturing_abac_functions.sql")
    schema = read_sql(sql_dir / "0.2manufacturing_database_schema.sql")
    extended = read_sql(sql_dir / "0.3manufacturing_extended_schema.sql")
    tags = read_sql(sql_dir / "0.4apply_tags.sql")
    abac = read_sql(sql_dir / "4.2.CreateManufacturingABACPolicies_BuiltInGroups.sql")
    
    test_tables = schema + "\n\n" + extended
    
    template = f'''"""
Manufacturing Industry ABAC Template
"""

INDUSTRY_NAME = "Manufacturing"
INDUSTRY_DESCRIPTION = "Manufacturing data protection with IP and trade secret controls"

FUNCTIONS_SQL = """
{functions}
"""

TAG_DEFINITIONS = [
    ("pii_type_manufacturing", "PII data types in manufacturing", [
        "employee_id", "ssn", "email", "phone", "name", "address"
    ]),
    ("ip_classification_manufacturing", "Intellectual property classification", [
        "Trade_Secret", "Proprietary", "Confidential", "Internal", "Public"
    ]),
    ("compliance_type_manufacturing", "Manufacturing compliance requirements", [
        "Export_Control", "ISO_Certified", "FDA_Regulated", "None"
    ]),
    ("data_sensitivity_manufacturing", "Data sensitivity levels", [
        "Highly_Sensitive", "Sensitive", "Internal", "Public"
    ]),
]

ABAC_POLICIES_SQL = """
{abac}
"""

TEST_TABLES_SQL = """
{test_tables}
"""

TAG_APPLICATIONS_SQL = """
{tags}
"""

TEST_TABLES = ["products_test", "suppliers_test", "inventory_test", 
               "production_data_test", "quality_control_test", "employees_test"]
'''
    
    output = OUT_DIR / "manufacturing_template.py"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"  ✅ Created {output.name}")

def create_retail():
    """Create Retail template"""
    print("\n📋 Retail")
    sql_dir = BASE_DIR / "retail" / "sql"
    
    functions = read_sql(sql_dir / "0.1retail_abac_functions.sql")
    schema = read_sql(sql_dir / "0.2retail_database_schema.sql")
    extended = read_sql(sql_dir / "0.3retail_extended_tables.sql")
    
    test_tables = schema + "\n\n" + extended
    
    template = f'''"""
Retail Industry ABAC Template
"""

INDUSTRY_NAME = "Retail"
INDUSTRY_DESCRIPTION = "Retail customer data protection and PCI compliance"

FUNCTIONS_SQL = """
{functions}
"""

TAG_DEFINITIONS = [
    ("pii_type_retail", "Retail PII data types", [
        "customer_name", "email", "phone", "address", "credit_card", 
        "loyalty_id", "purchase_history"
    ]),
    ("pci_compliance_retail", "PCI-DSS compliance requirement", [
        "Required", "Not_Required"
    ]),
    ("customer_tier_retail", "Customer loyalty tier", [
        "Platinum", "Gold", "Silver", "Bronze", "Standard"
    ]),
    ("data_classification_retail", "Data classification levels", [
        "Confidential", "Internal", "Public"
    ]),
]

ABAC_POLICIES_SQL = """
-- ABAC policies for retail to be defined
"""

TEST_TABLES_SQL = """
{test_tables}
"""

TAG_APPLICATIONS_SQL = """
-- Tag applications for retail to be defined
"""

TEST_TABLES = ["customers_test", "orders_test", "products_test", 
               "transactions_test", "loyalty_programs_test", "stores_test"]
'''
    
    output = OUT_DIR / "retail_template.py"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"  ✅ Created {output.name}")

def create_telco():
    """Create Telco template"""
    print("\n📋 Telco")
    sql_dir = BASE_DIR / "telco" / "sql"
    
    functions = read_sql(sql_dir / "0.1telco_abac_functions.sql")
    schema = read_sql(sql_dir / "0.2telco_database_schema.sql")
    extended = read_sql(sql_dir / "0.3telco_extended_tables.sql")
    
    test_tables = schema + "\n\n" + extended
    
    template = f'''"""
Telco Industry ABAC Template
"""

INDUSTRY_NAME = "Telco"
INDUSTRY_DESCRIPTION = "Telecommunications data protection with subscriber privacy"

FUNCTIONS_SQL = """
{functions}
"""

TAG_DEFINITIONS = [
    ("pii_type_telco", "Telco PII data types", [
        "subscriber_name", "phone_number", "email", "address", 
        "imsi", "imei", "account_number", "usage_data"
    ]),
    ("data_classification_telco", "Data classification levels", [
        "Highly_Confidential", "Confidential", "Internal", "Public"
    ]),
    ("regulatory_compliance_telco", "Regulatory compliance requirements", [
        "GDPR", "CPNI", "CALEA", "None"
    ]),
    ("subscriber_type_telco", "Subscriber type classification", [
        "Enterprise", "Business", "Consumer", "Government"
    ]),
]

ABAC_POLICIES_SQL = """
-- ABAC policies for telco to be defined
"""

TEST_TABLES_SQL = """
{test_tables}
"""

TAG_APPLICATIONS_SQL = """
-- Tag applications for telco to be defined
"""

TEST_TABLES = ["subscribers_test", "accounts_test", "call_records_test", 
               "data_usage_test", "network_devices_test", "billing_test"]
'''
    
    output = OUT_DIR / "telco_template.py"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"  ✅ Created {output.name}")

def create_government():
    """Create Government template"""
    print("\n📋 Government")
    sql_dir = BASE_DIR / "government" / "sql"
    
    functions = read_sql(sql_dir / "0.1government_abac_functions.sql")
    schema = read_sql(sql_dir / "0.2government_database_schema.sql")
    extended = read_sql(sql_dir / "0.3government_extended_tables.sql")
    
    test_tables = schema + "\n\n" + extended
    
    template = f'''"""
Government Industry ABAC Template
"""

INDUSTRY_NAME = "Government"
INDUSTRY_DESCRIPTION = "Government data protection with security clearances and classifications"

FUNCTIONS_SQL = """
{functions}
"""

TAG_DEFINITIONS = [
    ("pii_type_government", "Government PII data types", [
        "ssn", "name", "dob", "address", "phone", "email", 
        "employee_id", "clearance_level"
    ]),
    ("security_classification_government", "Security classification levels", [
        "Top_Secret", "Secret", "Confidential", "Unclassified"
    ]),
    ("clearance_required_government", "Security clearance requirement", [
        "Top_Secret", "Secret", "Confidential", "Public_Trust", "None"
    ]),
    ("data_sensitivity_government", "Data sensitivity levels", [
        "CUI", "FOUO", "Sensitive", "Public"
    ]),
]

ABAC_POLICIES_SQL = """
-- ABAC policies for government to be defined
"""

TEST_TABLES_SQL = """
{test_tables}
"""

TAG_APPLICATIONS_SQL = """
-- Tag applications for government to be defined
"""

TEST_TABLES = ["citizens_test", "employees_test", "security_clearances_test", 
               "classified_documents_test", "access_logs_test", "facilities_test"]
'''
    
    output = OUT_DIR / "government_template.py"
    with open(output, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"  ✅ Created {output.name}")

def main():
    print("=" * 60)
    print("GENERATING INDUSTRY TEMPLATES")
    print("=" * 60)
    
    create_healthcare()
    create_manufacturing()
    create_retail()
    create_telco()
    create_government()
    
    print("\n" + "=" * 60)
    print("✅ ALL TEMPLATES GENERATED")
    print("=" * 60)
    print("\nAvailable industries:")
    print("  - Finance (already exists)")
    print("  - Healthcare")
    print("  - Manufacturing")
    print("  - Retail")
    print("  - Telco")
    print("  - Government")
    print("\nNote: Insurance needs manual extraction from notebooks")

if __name__ == "__main__":
    main()

