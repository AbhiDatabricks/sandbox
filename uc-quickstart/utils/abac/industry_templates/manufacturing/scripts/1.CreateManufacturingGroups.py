# Databricks notebook source
# MAGIC %md
# MAGIC # 👥 Manufacturing ABAC Account Groups Setup
# MAGIC
# MAGIC This script creates account-level user groups for manufacturing personas using Databricks Account SCIM API.

import requests
import json

try:
    token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
except Exception as e:
    raise Exception("Token retrieval failed - run in Databricks workspace")

workspace_url = "https://e2-demo-field-eng.cloud.databricks.com"
account_domain = workspace_url
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
account_scim_url = f"{account_domain}/api/2.0/account/scim/v2/Groups"

manufacturing_groups = {
    "Plant_Operator": {"display_name": "Plant Operator", "description": "Operate production assets and view site telemetry"},
    "Quality_Engineer": {"display_name": "Quality Engineer", "description": "Investigate defects and non-conformances"},
    "Maintenance_Tech": {"display_name": "Maintenance Tech", "description": "Perform maintenance during defined windows"},
    "Supply_Chain_Manager": {"display_name": "Supply Chain Manager", "description": "Manage suppliers and BOM"},
    "Supplier_Auditor": {"display_name": "Supplier Auditor", "description": "Temporary supplier audit access"},
    "RnD_Scientist": {"display_name": "R&D Scientist", "description": "Access design specs and CAD"},
    "Site_Lead": {"display_name": "Site Lead", "description": "Site leadership with broad access"}
}

def create_account_group(group_name: str, display_name: str, description: str):
    try:
        list_response = requests.get(account_scim_url, headers=headers)
        if list_response.status_code == 200:
            for group in list_response.json().get('Resources', []):
                if group.get('displayName') == group_name:
                    print(f"Already exists: {group_name} ({group.get('id')})")
                    return {"success": True, "action": "skipped", "group_id": group.get('id')}
    except Exception:
        pass

    payload = {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "displayName": group_name
    }
    resp = requests.post(account_scim_url, headers=headers, data=json.dumps(payload))
    if resp.status_code == 201:
        gid = resp.json().get('id')
        print(f"Created: {group_name} ({gid})")
        return {"success": True, "action": "created", "group_id": gid}
    else:
        print(f"Failed: {group_name} -> {resp.status_code} {resp.text}")
        return {"success": False, "action": "failed", "error": resp.text}

results = {}
for group_name, meta in manufacturing_groups.items():
    results[group_name] = create_account_group(group_name, meta["display_name"], meta["description"])

print("Summary:")
print(json.dumps(results, indent=2))


