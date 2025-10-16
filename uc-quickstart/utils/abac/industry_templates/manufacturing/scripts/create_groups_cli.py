#!/usr/bin/env python3
"""Create manufacturing account groups via Databricks SDK"""
from databricks.sdk import WorkspaceClient
import os

os.environ.setdefault('DATABRICKS_CONFIG_PROFILE', 'AZURE1')
w = WorkspaceClient()

manufacturing_groups = {
    "Plant_Operator": {"display_name": "Plant Operator", "description": "Operate production assets and view site telemetry"},
    "Quality_Engineer": {"display_name": "Quality Engineer", "description": "Investigate defects and non-conformances"},
    "Maintenance_Tech": {"display_name": "Maintenance Tech", "description": "Perform maintenance during defined windows"},
    "Supply_Chain_Manager": {"display_name": "Supply Chain Manager", "description": "Manage suppliers and BOM"},
    "Supplier_Auditor": {"display_name": "Supplier Auditor", "description": "Temporary supplier audit access"},
    "RnD_Scientist": {"display_name": "R&D Scientist", "description": "Access design specs and CAD"},
    "Site_Lead": {"display_name": "Site Lead", "description": "Site leadership with broad access"}
}

print("Creating manufacturing account groups...")
for group_name, meta in manufacturing_groups.items():
    try:
        # Check if exists
        existing = [g for g in w.groups.list() if g.display_name == group_name]
        if existing:
            print(f"✅ Already exists: {group_name} (id: {existing[0].id})")
        else:
            # Create group
            group = w.groups.create(display_name=group_name)
            print(f"✅ Created: {group_name} (id: {group.id})")
    except Exception as e:
        print(f"❌ Failed: {group_name} - {str(e)[:100]}")

print("\nDone!")

