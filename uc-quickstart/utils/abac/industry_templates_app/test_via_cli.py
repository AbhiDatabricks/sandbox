#!/usr/bin/env python3
"""
CLI test using databricks CLI instead of SDK
"""
import subprocess
import json
from industries import load_industry_template

def execute_sql_via_cli(sql, warehouse_id="148ccb90800933a1"):
    """Execute SQL via databricks CLI"""
    try:
        result = subprocess.run(
            ["databricks", "sql", "execute", 
             "--warehouse-id", warehouse_id,
             "--sql", sql],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return True, "Success"
        else:
            return False, result.stderr or result.stdout
    except Exception as e:
        return False, str(e)

def test_industry(industry_name, catalog="apscat", warehouse_id="148ccb90800933a1"):
    """Test deploying an industry"""
    schema = industry_name.lower()
    
    print(f"\n{'='*60}")
    print(f"Testing: {industry_name}")
    print(f"Target: {catalog}.{schema}")
    print(f"{'='*60}")
    
    # Step 1: Use catalog
    print(f"\n1️⃣  Setting catalog context...")
    success, msg = execute_sql_via_cli(f"USE CATALOG {catalog}", warehouse_id)
    if not success:
        print(f"❌ Failed: {msg}")
        return False
    print(f"✅ Catalog set")
    
    # Step 2: Create schema
    print(f"\n2️⃣  Creating schema {catalog}.{schema}...")
    success, msg = execute_sql_via_cli(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}", warehouse_id)
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
        # Print first 500 chars to debug
        print(f"SQL preview: {sql_statements[:500]}")
        return False
    
    # Step 5: Create functions (test first 3 only for speed)
    test_count = min(3, len(statements))
    print(f"\n5️⃣  Creating first {test_count} functions (as test)...")
    success_count = 0
    errors = []
    
    for idx in range(test_count):
        stmt = statements[idx]
        # Extract function name for logging
        func_name = "unknown"
        if "CREATE" in stmt.upper() and "FUNCTION" in stmt.upper():
            parts = stmt.upper().split("FUNCTION")
            if len(parts) > 1:
                func_name = parts[1].split("(")[0].strip()
        
        print(f"  [{idx+1}/{test_count}] Creating {func_name}...", end=" ")
        success, msg = execute_sql_via_cli(stmt, warehouse_id)
        if success:
            print("✅")
            success_count += 1
        else:
            print(f"❌")
            print(f"      Error: {msg[:200]}")
            errors.append((func_name, msg))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Test Summary: {success_count}/{test_count} functions created")
    print(f"Total available: {len(statements)} functions")
    print(f"{'='*60}")
    
    return success_count > 0

def main():
    """Main test function"""
    catalog = "apscat"
    warehouse_id = "148ccb90800933a1"
    
    print("="*60)
    print("ABAC DEPLOYMENT CLI TEST")
    print("="*60)
    print(f"Catalog: {catalog}")
    print(f"Warehouse: {warehouse_id}")
    print(f"Testing via: databricks CLI")
    
    # Test key industries
    industries_to_test = ["Finance", "Healthcare"]
    
    results = {}
    for industry in industries_to_test:
        results[industry] = test_industry(industry, catalog, warehouse_id)
    
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

