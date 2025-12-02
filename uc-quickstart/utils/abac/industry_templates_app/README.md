# ABAC Industry Templates Deployer - Databricks App

A Databricks App that provides a simple UI to deploy ABAC (Attribute-Based Access Control) masking and filtering functions to your Unity Catalog.

## Features

- 🎯 **Select Catalog & Schema**: Choose where to deploy functions via dropdown
- 🏭 **Industry Templates**: Start with Finance template (more coming soon)
- 🚀 **One-Click Deployment**: Deploy 15+ masking/filtering functions instantly
- ✅ **Real-time Progress**: Track deployment status with progress indicators

## What Gets Deployed (Finance Template)

### Masking Functions (11):
- `mask_credit_card` - PCI-DSS compliant credit card masking
- `mask_ssn_last4` - SSN protection (last 4 digits)
- `mask_email` - Email masking (hides local part)
- `mask_phone` - Phone number masking (last 4 digits)
- `mask_account_last4` - Account number protection
- `mask_routing_number` - Routing number masking
- `mask_ip_address` - IP address subnet masking
- `mask_transaction_hash` - Transaction ID hashing
- `mask_customer_id_deterministic` - Deterministic customer ID hashing
- `mask_amount_bucket` - Transaction amount bucketing
- `mask_income_bracket` - Income range bucketing

### Filter Functions (4):
- `filter_fraud_flagged_only` - Show only fraudulent transactions
- `filter_high_value_transactions` - Filter transactions > $5K
- `filter_business_hours` - Business hours (9 AM - 5 PM) filter
- `filter_by_region` - Regional access filter (CA example)

## How to Deploy

### Prerequisites

1. Databricks workspace with Apps enabled
2. Unity Catalog configured
3. **SQL Warehouse** - App will use a SQL warehouse resource (configured at deployment)
4. Permissions to create functions in target catalog/schema

### Deployment Steps

1. **Create the App in Databricks**:
   - Go to your Databricks workspace
   - Click **+ New** → **App** in the sidebar
   - Under "Create from code", choose **Manual**
   - Name it: `abac-industry-deployer`

2. **Upload App Files**:
   ```bash
   # Navigate to this directory
   cd uc-quickstart/utils/abac/industry_templates_app
   
   # Deploy to Databricks
   databricks apps deploy abac-industry-deployer \
     --source-code-path /Workspace/Users/<your-email>/apps/abac-deployer
   ```

3. **Configure SQL Warehouse Resource**:
   - During app creation, Databricks will prompt you to select a SQL warehouse
   - Choose an existing warehouse or let Databricks provision one
   - The app will automatically use this warehouse (via the `sql_warehouse` resource in `app.yaml`)
   - No need to hard-code warehouse IDs! 🎉

4. **Alternative: Use Databricks CLI**:
   ```bash
   # Create workspace directory
   databricks workspace mkdirs /Workspace/Users/<your-email>/apps/abac-deployer
   
   # Upload files
   databricks workspace import-dir . \
     /Workspace/Users/<your-email>/apps/abac-deployer
   
   # Create and start app
   databricks apps create abac-industry-deployer \
     --source-code-path /Workspace/Users/<your-email>/apps/abac-deployer
   ```

## Usage

1. **Open the App**: Navigate to the app URL in your workspace
2. **Select Catalog**: Choose your target catalog from the dropdown
3. **Select Schema**: Choose the schema (or create a new one first)
4. **Select Industry**: Choose "Finance" template
5. **Deploy**: Click "🚀 Deploy Functions" button
6. **Verify**: Check deployment status and function list

## After Deployment

Once functions are deployed, you can:

1. **Create Tables**: Set up your data tables in the same schema
2. **Apply Tags**: Use Unity Catalog tags on sensitive columns
3. **Create ABAC Policies**: Use these functions in your ABAC policies

Example:
```sql
-- Create policy using deployed function
CREATE POLICY mask_ssn ON SCHEMA finance
  COLUMN MASK mask_ssn_last4
  TO `account users`
  FOR TABLES
  MATCH COLUMNS
    hasTagValue('pii_type_finance', 'ssn') AS ssn
  ON COLUMN ssn;
```

## App Structure

```
industry_templates_app/
├── app.py          # Main Gradio application
├── app.yaml        # Databricks App configuration
└── README.md       # This file
```

## Requirements

- `gradio` - For the web UI
- `databricks-sdk` - For SQL warehouse execution
- SQL Warehouse - For running queries (more scalable than Spark session)

## Architecture

This app follows the **Databricks Apps resource pattern**:

### SQL Warehouse as a Resource
Instead of hard-coding warehouse IDs, the app declares a SQL warehouse as a **resource**:
```yaml
resources:
  - key: sql_warehouse
    type: sql-warehouse
    permission: CAN_USE

env:
  - name: WAREHOUSE_ID
    valueFrom: sql_warehouse  # Auto-inject warehouse ID
```

At runtime, Databricks automatically injects:
- `WAREHOUSE_ID` - The actual warehouse ID
- `DATABRICKS_HOST` - Workspace URL
- `DATABRICKS_CLIENT_ID` - OAuth credentials
- `DATABRICKS_CLIENT_SECRET` - OAuth credentials

The app code just reads `WAREHOUSE_ID` from the environment and never knows the actual ID!

### Benefits over Spark Session
- **Performance**: SQL warehouses are optimized for SQL workloads
- **Resource Management**: Dedicated compute separate from app runtime
- **Scalability**: Auto-scaling capabilities
- **Concurrency**: Better handling of concurrent requests
- **Flexibility**: Swap warehouses without code changes

### References
- [Databricks App Templates](https://github.com/databricks/app-templates)
- [Add SQL Warehouse Resource](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/sql-warehouse)
- [Add Resources to Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/resources)

## Troubleshooting

### App won't start
- Check that `app.yaml` is in the same directory as `app.py`
- Verify the source code path in workspace
- Ensure a SQL warehouse resource is configured for the app

### SQL Warehouse errors
- Check that a warehouse is selected/provisioned for the app
- The warehouse will auto-start if stopped (serverless is fastest)
- Verify you have `CAN USE` permission on the warehouse
- Check `WAREHOUSE_ID` environment variable is being injected (it's automatic)

### Functions fail to create
- Ensure you have `CREATE FUNCTION` permission on the schema
- Verify the catalog and schema exist
- Check that you're not deploying to a system schema
- Verify SQL warehouse has permissions to the catalog/schema

### Can't see catalogs/schemas
- Ensure you have `USE CATALOG` and `USE SCHEMA` permissions
- Check Unity Catalog is enabled in your workspace
- Verify the SQL warehouse can query system tables

## Future Enhancements

- [ ] Add more industry templates (Healthcare, Retail, Manufacturing)
- [ ] Support for table creation
- [ ] Tag application UI
- [ ] ABAC policy creation wizard
- [ ] Deployment history tracking
- [ ] Function testing interface

## Resources

- [Databricks Apps Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [Unity Catalog ABAC](https://docs.databricks.com/data-governance/unity-catalog/abac/)
- [Repository](https://github.com/AbhiDatabricks/sandbox)

