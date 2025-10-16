#!/usr/bin/env python3
"""Execute SQL files using Databricks SQL warehouse"""
import os
import sys
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

def execute_sql_file(w, warehouse_id, sql_file):
    """Execute SQL file statements"""
    print(f"\n{'='*60}")
    print(f"Executing: {sql_file}")
    print(f"{'='*60}")
    
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Split by semicolon and filter out comments/empty
    statements = []
    for stmt in sql_content.split(';'):
        stmt = stmt.strip()
        # Remove comment lines
        lines = [l for l in stmt.split('\n') if not l.strip().startswith('--')]
        stmt = '\n'.join(lines).strip()
        if stmt and not stmt.startswith('--'):
            statements.append(stmt)
    
    print(f"Found {len(statements)} statements to execute")
    
    for idx, statement in enumerate(statements, 1):
        # Skip MAGIC comments or USE CATALOG/SCHEMA (we'll handle context separately)
        if 'MAGIC' in statement:
            continue
        if statement.strip().upper().startswith('USE CATALOG') or statement.strip().upper().startswith('USE SCHEMA'):
            print(f"\n[{idx}/{len(statements)}] Skipping context statement: {statement[:50]}...")
            continue
            
        print(f"\n[{idx}/{len(statements)}] Executing statement...")
        print(f"Preview: {statement[:100]}...")
        
        try:
            # Use catalog and schema parameters instead of prepending USE statements
            result = w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=statement,
                catalog="users",
                schema="abhishekpratap_singh",
                wait_timeout="50s"
            )
            
            if result.status.state == StatementState.SUCCEEDED:
                print(f"✅ Success")
                if result.result and result.result.data_array:
                    print(f"   Rows: {len(result.result.data_array)}")
            else:
                print(f"⚠️  Status: {result.status.state}")
                if result.status.error:
                    print(f"   Error: {result.status.error.message}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if "already exists" in str(e).lower():
                print("   (Ignoring 'already exists' error)")
            else:
                print(f"   Continuing...")
    
    print(f"\n✅ Completed: {sql_file}")

def main():
    profile = os.getenv("DATABRICKS_CONFIG_PROFILE", "AZURE1")
    warehouse_id = "071969b1ec9a91ca"
    
    w = WorkspaceClient(profile=profile)
    print(f"Connected to workspace (profile: {profile})")
    print(f"Using warehouse: {warehouse_id}")
    
    # Execute in order
    base_path = "uc-quickstart/utils/abac/manufacturing"
    sql_files = [
        f"{base_path}/0.1manufacturing_abac_functions.sql",
        f"{base_path}/0.2manufacturing_database_schema.sql",
        f"{base_path}/4.1.CreateManufacturingABACPolicies.sql",
    ]
    
    for sql_file in sql_files:
        if os.path.exists(sql_file):
            execute_sql_file(w, warehouse_id, sql_file)
        else:
            print(f"⚠️  File not found: {sql_file}")
    
    print("\n" + "="*60)
    print("✅ All SQL files executed")
    print("="*60)

if __name__ == "__main__":
    main()

