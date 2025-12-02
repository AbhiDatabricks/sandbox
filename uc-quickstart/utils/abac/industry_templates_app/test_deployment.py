#!/usr/bin/env python3
"""
CLI test script to simulate app deployment
"""
from databricks.sdk import WorkspaceClient
from industries import load_industry_template, get_available_industries
import os

# Initialize client
w = WorkspaceClient()

# Get SQL warehouse ID
WAREHOUSE_ID = os.getenv("WAREHOUSE_ID")
if not WAREHOUSE_ID:
    try:
        warehouses = w.warehouses.list()
        first_warehouse = next(iter(warehouses), None)
        if first_warehouse:
            WAREHOUSE_ID = first_warehouse.id
            print(f"Using warehouse: {first_warehouse.name} ({WAREHOUSE_ID})")
    except Exception as e:
        print(f"Error finding warehouse: {e}")
        exit(1)

def execute_sql(sql, description="SQL"):
    """Execute SQL via warehouse"""
    try:
        result = w.statement_execution.execute_statement(
            statement=sql,
            warehouse_id=WAREHOUSE_ID,
            wait_timeout="50s"
        )
        if result.status.state.value == "SUCCEEDED":
            return True, "Success"
        else:
            error = result.status.error
            return False, f"{error.error_code}: {error.message}" if error else "Unknown error"
    except Exception as e:
        return False, str(e)

def test_industry(industry_name, catalog="apscat"):
    """Test deploying an industry"""
    schema = industry_name.lower()
    
    print(f"\n{'='*60}")
    print(f"Testing: {industry_name}")
    print(f"Target: {catalog}.{schema}")
    print(f"{'='*60}")
    
    # Step 1: Use catalog
    print(f"\n1️⃣  Setting catalog context...")
    success, msg = execute_sql(f"USE CATALOG {catalog}", "Use catalog")
    if not success:
        print(f"❌ Failed: {msg}")
        return False
    print(f"✅ Catalog set")
    
    # Step 2: Create schema
    print(f"\n2️⃣  Creating schema {catalog}.{schema}...")
    success, msg = execute_sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}", "Create schema")
    if not success:
        print(f"❌ Failed: {msg}")
        return False
    print(f"✅ Schema created/exists")
    
    # Step 3: Load template
    print(f"\n3️⃣  Loading {industry_name} template...")
    try:
        template = load_industry_template(industry_name)
        sql_statements = template.FUNCTIONS_SQL
        print(f"✅ Template loaded ({len(sql_statements)} chars)")
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Step 4: Replace with fully qualified names
    print(f"\n4️⃣  Preparing SQL statements...")
    sql_statements = sql_statements.replace("CREATE OR REPLACE FUNCTION ", f"CREATE OR REPLACE FUNCTION {catalog}.{schema}.")
    
    # Split by semicolon and filter
    statements = [s.strip() for s in sql_statements.split(';') 
                 if s.strip() and ('CREATE' in s.upper() and 'FUNCTION' in s.upper())]
    print(f"✅ Found {len(statements)} CREATE FUNCTION statements")
    
    if len(statements) == 0:
        print(f"❌ No statements to execute!")
        return False
    
    # Step 5: Create functions
    print(f"\n5️⃣  Creating {len(statements)} functions...")
    success_count = 0
    errors = []
    
    for idx, stmt in enumerate(statements):
        # Extract function name for logging
        func_name = "unknown"
        if "CREATE" in stmt.upper() and "FUNCTION" in stmt.upper():
            parts = stmt.upper().split("FUNCTION")
            if len(parts) > 1:
                func_name = parts[1].split("(")[0].strip()
        
        print(f"  [{idx+1}/{len(statements)}] Creating {func_name}...", end=" ")
        success, msg = execute_sql(stmt, f"Create function {func_name}")
        if success:
            print("✅")
            success_count += 1
        else:
            print(f"❌ {msg[:100]}")
            errors.append((func_name, msg))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {success_count}/{len(statements)} functions created")
    print(f"{'='*60}")
    
    if errors:
        print(f"\n❌ Errors ({len(errors)}):")
        for func, err in errors[:3]:
            print(f"  • {func}: {err[:200]}")
    
    return success_count == len(statements)

def main():
    """Main test function"""
    catalog = "apscat"
    
    print("="*60)
    print("ABAC DEPLOYMENT CLI TEST")
    print("="*60)
    print(f"Catalog: {catalog}")
    print(f"Warehouse: {WAREHOUSE_ID}")
    
    # Test key industries
    industries_to_test = ["Finance", "Healthcare"]
    
    results = {}
    for industry in industries_to_test:
        results[industry] = test_industry(industry, catalog)
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for industry, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {industry}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! App should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())

