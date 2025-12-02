import gradio as gr
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import os

# Initialize Databricks client
# Auth credentials are automatically injected by Databricks Apps
w = WorkspaceClient()

# Get SQL warehouse ID from environment (injected from app.yaml resource)
WAREHOUSE_ID = os.getenv("WAREHOUSE_ID")

# Finance SQL functions definition
FINANCE_FUNCTIONS_SQL = """
-- Create Finance ABAC Functions

CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'Masks credit card number showing only last 4 digits'
RETURN CONCAT('****-****-****-', SUBSTRING(card_number, -4, 4));

CREATE OR REPLACE FUNCTION mask_ssn_last4(ssn STRING)
RETURNS STRING
COMMENT 'Masks SSN showing only last 4 digits'
RETURN CONCAT('***-**-', SUBSTRING(ssn, -4, 4));

CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'Masks email local part, shows domain'
RETURN CONCAT('***@', SPLIT(email, '@')[1]);

CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'Masks phone number showing only last 4 digits'
RETURN CONCAT('***-***-', SUBSTRING(phone, -4, 4));

CREATE OR REPLACE FUNCTION mask_account_last4(account_number STRING)
RETURNS STRING
COMMENT 'Masks account number showing only last 4 digits'
RETURN CONCAT('********', SUBSTRING(account_number, -4, 4));

CREATE OR REPLACE FUNCTION mask_routing_number(routing_number STRING)
RETURNS STRING
COMMENT 'Masks routing number showing only last 2 digits'
RETURN CONCAT('*******', SUBSTRING(routing_number, -2, 2));

CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'Masks IP address to subnet level'
RETURN CONCAT(
    SPLIT(ip, '\\.')[0], '.',
    SPLIT(ip, '\\.')[1], '.',
    '***', '.',
    '***'
);

CREATE OR REPLACE FUNCTION mask_transaction_hash(transaction_id STRING)
RETURNS STRING
COMMENT 'Returns deterministic hash of transaction ID'
RETURN CONCAT('TXN_', SHA2(transaction_id, 256));

CREATE OR REPLACE FUNCTION mask_customer_id_deterministic(customer_id STRING)
RETURNS STRING
COMMENT 'Returns deterministic hash for customer ID (preserves joins)'
RETURN CONCAT('CUST_', SUBSTRING(SHA2(customer_id, 256), 1, 12));

CREATE OR REPLACE FUNCTION mask_amount_bucket(amount DECIMAL(18,2))
RETURNS STRING
COMMENT 'Buckets transaction amounts into ranges'
RETURN CASE
    WHEN amount < 100 THEN '$0-$100'
    WHEN amount < 500 THEN '$100-$500'
    WHEN amount < 1000 THEN '$500-$1K'
    WHEN amount < 5000 THEN '$1K-$5K'
    WHEN amount < 10000 THEN '$5K-$10K'
    ELSE '$10K+'
END;

CREATE OR REPLACE FUNCTION mask_income_bracket(income DECIMAL(18,2))
RETURNS STRING
COMMENT 'Buckets annual income into ranges'
RETURN CASE
    WHEN income < 30000 THEN 'Under $30K'
    WHEN income < 50000 THEN '$30K-$50K'
    WHEN income < 75000 THEN '$50K-$75K'
    WHEN income < 100000 THEN '$75K-$100K'
    WHEN income < 150000 THEN '$100K-$150K'
    ELSE 'Over $150K'
END;

CREATE OR REPLACE FUNCTION filter_fraud_flagged_only(fraud_flag BOOLEAN)
RETURNS BOOLEAN
COMMENT 'Row filter to show only fraud-flagged transactions'
RETURN fraud_flag = TRUE;

CREATE OR REPLACE FUNCTION filter_high_value_transactions(amount DECIMAL(18,2))
RETURNS BOOLEAN
COMMENT 'Row filter for transactions over $5000'
RETURN amount > 5000;

CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'Row filter for business hours (9 AM - 5 PM)'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

CREATE OR REPLACE FUNCTION filter_by_region(state STRING)
RETURNS BOOLEAN
COMMENT 'Row filter for specific region (CA only example)'
RETURN state = 'CA';
"""

def execute_sql(sql_query):
    """Execute SQL using SQL warehouse"""
    try:
        result = w.statement_execution.execute_statement(
            statement=sql_query,
            warehouse_id=WAREHOUSE_ID,
            wait_timeout="30s"
        )
        
        if result.status.state == StatementState.SUCCEEDED:
            if result.result and result.result.data_array:
                return result.result.data_array
            return []
        else:
            raise Exception(f"Query failed: {result.status.state}")
    except Exception as e:
        raise Exception(f"SQL execution error: {str(e)}")

def get_catalogs():
    """Get list of catalogs from Unity Catalog"""
    try:
        data = execute_sql("SHOW CATALOGS")
        # data_array returns list of lists, first row is headers
        if len(data) > 1:
            catalogs = [row[0] for row in data[1:]]  # Skip header row
            return catalogs
        return []
    except Exception as e:
        return [f"Error: {str(e)}"]

def get_schemas(catalog):
    """Get list of schemas in selected catalog"""
    if not catalog or catalog.startswith("Error"):
        return []
    try:
        data = execute_sql(f"SHOW SCHEMAS IN {catalog}")
        # data_array returns list of lists, first row is headers
        if len(data) > 1:
            schemas = [row[0] for row in data[1:]]  # Skip header row
            return schemas
        return []
    except Exception as e:
        return [f"Error: {str(e)}"]

def deploy_functions(catalog, schema, industry, progress=gr.Progress()):
    """Deploy functions to selected catalog and schema"""
    try:
        if not catalog or not schema or not industry:
            return "❌ Error: Please select catalog, schema, and industry"
        
        progress(0, desc="Setting catalog and schema...")
        execute_sql(f"USE CATALOG {catalog}")
        execute_sql(f"USE SCHEMA {schema}")
        
        progress(0.2, desc="Reading function definitions...")
        if industry == "Finance":
            sql_statements = FINANCE_FUNCTIONS_SQL
        else:
            return f"❌ Error: {industry} not implemented yet"
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_statements.split(';') if s.strip() and not s.strip().startswith('--')]
        total = len(statements)
        
        progress(0.3, desc=f"Creating {total} functions...")
        
        success_count = 0
        errors = []
        
        for idx, stmt in enumerate(statements):
            try:
                if stmt.strip():
                    execute_sql(stmt)
                    success_count += 1
                    progress((0.3 + (0.6 * (idx + 1) / total)), 
                           desc=f"Created function {idx + 1}/{total}")
            except Exception as e:
                errors.append(f"Statement {idx + 1}: {str(e)[:100]}")
        
        progress(1.0, desc="Complete!")
        
        result = f"""
✅ **Deployment Complete!**

📊 **Target**: `{catalog}.{schema}`
🏭 **Industry**: {industry}
✨ **Functions Created**: {success_count}/{total}

### Functions Deployed:
- mask_credit_card
- mask_ssn_last4
- mask_email
- mask_phone
- mask_account_last4
- mask_routing_number
- mask_ip_address
- mask_transaction_hash
- mask_customer_id_deterministic
- mask_amount_bucket
- mask_income_bracket
- filter_fraud_flagged_only
- filter_high_value_transactions
- filter_business_hours
- filter_by_region

### Next Steps:
1. Create tables in your schema
2. Apply tags to columns
3. Create ABAC policies using these functions
"""
        
        if errors:
            result += f"\n\n⚠️ **Warnings**: {len(errors)} errors occurred\n"
            for err in errors[:3]:  # Show first 3 errors
                result += f"- {err}\n"
        
        return result
        
    except Exception as e:
        return f"❌ **Deployment Failed**\n\nError: {str(e)}"

# Gradio UI
with gr.Blocks(title="ABAC Industry Templates Deployer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🏭 ABAC Industry Templates Deployer
    
    Deploy Attribute-Based Access Control (ABAC) masking and filtering functions to your Unity Catalog.
    
    ### How to Use:
    1. **Select Catalog**: Choose the target catalog from your workspace
    2. **Select Schema**: Choose or create a schema for the functions
    3. **Select Industry**: Choose the industry template (Finance available)
    4. **Deploy**: Click to create all masking/filtering functions
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Step 1: Select Catalog & Schema")
            catalog_dropdown = gr.Dropdown(
                choices=get_catalogs(),
                label="Catalog",
                info="Select the catalog where functions will be created",
                interactive=True
            )
            
            schema_dropdown = gr.Dropdown(
                label="Schema",
                info="Select the schema for the functions",
                interactive=True
            )
            
            refresh_btn = gr.Button("🔄 Refresh Catalogs", size="sm")
            
        with gr.Column():
            gr.Markdown("### Step 2: Select Industry Template")
            industry_dropdown = gr.Dropdown(
                choices=["Finance"],
                value="Finance",
                label="Industry",
                info="Choose the industry template to deploy",
                interactive=True
            )
            
            gr.Markdown("""
            **Finance Template Includes:**
            - Credit card masking
            - SSN protection
            - Email/phone masking
            - Account number protection
            - Transaction amount bucketing
            - Income bracketing
            - Fraud detection filters
            - Business hours filters
            """)
    
    gr.Markdown("### Step 3: Deploy Functions")
    
    deploy_btn = gr.Button("🚀 Deploy Functions", variant="primary", size="lg")
    
    output = gr.Markdown(label="Deployment Status")
    
    # Event handlers
    def update_schemas(catalog):
        schemas = get_schemas(catalog)
        return gr.Dropdown(choices=schemas, value=None)
    
    catalog_dropdown.change(
        fn=update_schemas,
        inputs=[catalog_dropdown],
        outputs=[schema_dropdown]
    )
    
    refresh_btn.click(
        fn=lambda: gr.Dropdown(choices=get_catalogs(), value=None),
        outputs=[catalog_dropdown]
    )
    
    deploy_btn.click(
        fn=deploy_functions,
        inputs=[catalog_dropdown, schema_dropdown, industry_dropdown],
        outputs=[output]
    )
    
    gr.Markdown("""
    ---
    ### 📚 Additional Resources
    - [Unity Catalog ABAC Documentation](https://docs.databricks.com/data-governance/unity-catalog/abac/)
    - [Masking Functions Guide](https://docs.databricks.com/data-governance/unity-catalog/filters-and-masks)
    - [GitHub Repository](https://github.com/AbhiDatabricks/sandbox)
    """)

if __name__ == "__main__":
    demo.launch()

