#!/usr/bin/env python3
"""Execute SQL files using Databricks SQL warehouse with config file"""
import os
import sys
import yaml
from pathlib import Path
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def execute_sql_file(w, warehouse_id, catalog, schema, sql_file):
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
    
    success_count = 0
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
            # Use catalog and schema parameters
            result = w.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=statement,
                catalog=catalog,
                schema=schema,
                wait_timeout="50s"
            )
            
            if result.status.state == StatementState.SUCCEEDED:
                print(f"✅ Success")
                success_count += 1
                if result.result and result.result.data_array:
                    print(f"   Rows: {len(result.result.data_array)}")
            else:
                print(f"⚠️  Status: {result.status.state}")
                if result.status.error:
                    print(f"   Error: {result.status.error.message[:200]}")
                    
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error: {error_msg[:200]}")
            if "already exists" in error_msg.lower():
                print("   (Ignoring 'already exists' error)")
                success_count += 1
    
    print(f"\n✅ Completed: {sql_file} ({success_count}/{len(statements)} successful)")
    return success_count

def main():
    # Load configuration
    script_dir = Path(__file__).parent
    config_path = script_dir / "config.yaml"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    config = load_config(config_path)
    
    # Set profile from config
    profile = config['databricks_profile']
    warehouse_id = config['warehouse_id']
    catalog = config['catalog']
    schema = config['schema']
    
    os.environ['DATABRICKS_CONFIG_PROFILE'] = profile
    
    print(f"{'='*60}")
    print(f"Manufacturing ABAC Demo Deployment")
    print(f"{'='*60}")
    print(f"Profile: {profile}")
    print(f"Warehouse: {warehouse_id}")
    print(f"Catalog: {catalog}")
    print(f"Schema: {schema}")
    print(f"{'='*60}")
    
    w = WorkspaceClient(profile=profile)
    print(f"✅ Connected to workspace")
    
    # Create schema if it doesn't exist
    print(f"\n{'='*60}")
    print(f"Checking/Creating schema: {catalog}.{schema}")
    print(f"{'='*60}")
    try:
        result = w.statement_execution.execute_statement(
            warehouse_id=warehouse_id,
            statement=f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}",
            catalog=catalog,
            wait_timeout="30s"
        )
        if result.status.state == StatementState.SUCCEEDED:
            print(f"✅ Schema {catalog}.{schema} ready")
        else:
            print(f"⚠️  Schema creation status: {result.status.state}")
    except Exception as e:
        print(f"⚠️  Schema check: {str(e)[:200]}")
    
    # Execute SQL files in order
    total_success = 0
    total_statements = 0
    
    for sql_file in config['sql_files']:
        sql_path = script_dir / sql_file
        if sql_path.exists():
            count = execute_sql_file(w, warehouse_id, catalog, schema, sql_path)
            total_success += count
        else:
            print(f"⚠️  File not found: {sql_path}")
    
    print("\n" + "="*60)
    print(f"✅ Deployment Complete")
    print(f"Total successful statements: {total_success}")
    print("="*60)

if __name__ == "__main__":
    main()

