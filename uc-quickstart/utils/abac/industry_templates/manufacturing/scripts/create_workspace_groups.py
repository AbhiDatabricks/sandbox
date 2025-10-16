#!/usr/bin/env python3
"""Create manufacturing workspace groups"""
from databricks.sdk import WorkspaceClient
import os

os.environ.setdefault('DATABRICKS_CONFIG_PROFILE', 'AZURE1')
w = WorkspaceClient()

manufacturing_groups = [
    "Plant_Operator",
    "Quality_Engineer", 
    "Maintenance_Tech",
    "Supply_Chain_Manager",
    "Supplier_Auditor",
    "RnD_Scientist",
    "Site_Lead"
]

print("Creating manufacturing workspace groups...")
for group_name in manufacturing_groups:
    try:
        # Try to get existing group
        try:
            existing = w.groups.get(id=group_name)
            print(f"✅ Already exists: {group_name}")
            continue
        except:
            pass
        
        # Create workspace group using SCIM-like approach
        group = w.groups.create(display_name=group_name, members=[])
        print(f"✅ Created: {group_name}")
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg.lower():
            print(f"✅ Already exists: {group_name}")
        else:
            print(f"❌ Failed: {group_name} - {error_msg[:100]}")

print("\n✅ Workspace groups ready for ABAC policies!")

