# Databricks notebook source
# MAGIC %md
# MAGIC # 🏷️ Manufacturing ABAC Tag Policies Creation

import requests, json, os
from typing import List, Dict, Any

workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL", "https://e2-demo-field-eng.cloud.databricks.com")
try:
    token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
except Exception:
    raise Exception("Token retrieval failed - run in Databricks workspace")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
base_url = f"{workspace_url}/api/2.0/tag-policies"

def create_tag_policy(tag_key: str, allowed_values: List[str], description: str) -> Dict[str, Any]:
    try:
        requests.delete(f"{base_url}/{tag_key}", headers=headers)
    except Exception:
        pass
    payload = {"tag_policy": {"key": tag_key, "values": [{"name": v} for v in allowed_values], "description": description}}
    resp = requests.post(base_url, headers=headers, data=json.dumps(payload))
    if resp.status_code == 200:
        print(f"Created tag policy: {tag_key}")
        return {"success": True}
    else:
        print(f"Failed tag policy: {tag_key} -> {resp.status_code} {resp.text}")
        return {"success": False, "error": resp.text}

manufacturing_tag_policies = {
    "job_role": {"values": [
        "Plant_Operator","Quality_Engineer","Maintenance_Tech","Supply_Chain_Manager","Supplier_Auditor","RnD_Scientist","Site_Lead"
    ], "description": "Manufacturing personas for ABAC"},
    "data_purpose": {"values": [
        "Operations","Quality","Maintenance","SupplyChain","Audit","RnD"
    ], "description": "Intended use purpose for data access"},
    "site_region": {"values": [
        "Plant_A","Plant_B","Plant_C","AMER","EMEA","APAC"
    ], "description": "Plant-level and regional residency control"},
    "shift_hours": {"values": [
        "Day","Swing","Night","Emergency_24x7"
    ], "description": "Shift-based access control"},
    "asset_criticality": {"values": [
        "High","Medium","Low"
    ], "description": "Asset criticality based access"},
    "export_control": {"values": [
        "ITAR","EAR99","Not_Controlled"
    ], "description": "Export control classification"},
    "ip_sensitivity": {"values": [
        "Trade_Secret","Internal","Public"
    ], "description": "Design/IP sensitivity classification"},
    "data_residency": {"values": [
        "Country_Only","EU_Only","Cross_Border_Approved"
    ], "description": "Geographic data residency requirements"},
    "access_expiry_date": {"values": [
        "2025-12-31","2026-03-31","2026-06-30","2026-12-31","Permanent"
    ], "description": "Temporal access control with expiry"},
    "supplier_scope": {"values": [
        "Named_Supplier_Only","All_Suppliers","Audit_Project_Only"
    ], "description": "Scope restriction for supplier data"}
}

for key, cfg in manufacturing_tag_policies.items():
    create_tag_policy(key, cfg["values"], cfg["description"])

print("Tag policies creation completed")


