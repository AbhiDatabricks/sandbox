import gradio as gr
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import os
import requests
from industries import get_available_industries, load_industry_template
from documentation import DOCUMENTATION_MD

# Initialize Databricks client
try:
    w = WorkspaceClient()
    print(f"WorkspaceClient initialized, host: {w.config.host}")
except Exception as e:
    print(f"Error initializing WorkspaceClient: {e}")
    w = None

# Hardcode warehouse ID for Azure workspace (most reliable)
WAREHOUSE_ID = os.getenv("WAREHOUSE_ID") or "b0620c9f66bdeda3"
print(f"Using WAREHOUSE_ID: {WAREHOUSE_ID}")


def execute_sql(sql_query, description="SQL query", user_token=None):
    """Execute SQL using SQL warehouse

    Args:
        sql_query: SQL statement to execute
        description: Description for error messages
        user_token: Optional user access token for user authorization
    """
    try:
        # If user_token provided, use it for user authorization
        # Otherwise, use service principal (default WorkspaceClient)
        if user_token:
            # Use REST API with user token for user authorization
            workspace_url = w.config.host
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "statement": sql_query,
                "warehouse_id": WAREHOUSE_ID,
                "wait_timeout": "50s"
            }
            response = requests.post(
                f"{workspace_url}/api/2.0/sql/statements",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()

            if result.get("status", {}).get("state") == "SUCCEEDED":
                data_array = result.get("result", {}).get("data_array", [])
                return data_array
            else:
                error_info = result.get("status", {}).get("error", {})
                error_msg = f"State: {result.get('status', {}).get('state')}\n"
                error_msg += f"Error Code: {error_info.get('error_code', 'N/A')}\n"
                error_msg += f"Message: {error_info.get('message', 'Unknown error')}"
                raise Exception(error_msg)
        else:
            # Use service principal via WorkspaceClient (default)
            result = w.statement_execution.execute_statement(
                statement=sql_query,
                warehouse_id=WAREHOUSE_ID,
                wait_timeout="50s"
            )

            if result.status.state == StatementState.SUCCEEDED:
                if result.result and result.result.data_array:
                    return result.result.data_array
                return []
            else:
                error_msg = f"State: {result.status.state}"
                if result.status.error:
                    error_msg += f"\nError Code: {result.status.error.error_code if hasattr(result.status.error, 'error_code') else 'N/A'}"
                    error_msg += f"\nMessage: {result.status.error.message}"
                raise Exception(error_msg)
    except Exception as e:
        raise Exception(f"{description}\n{str(e)}")

def get_catalogs():
    """Get list of catalogs from Unity Catalog"""
    try:
        # Try SDK first (faster and more reliable)
        catalogs_list = list(w.catalogs.list())
        catalogs = [c.name for c in catalogs_list if c.name and not c.name.startswith('__')]
        print(f"Found catalogs via SDK: {catalogs}")
        if catalogs:
            return catalogs
    except Exception as e:
        print(f"SDK catalog list failed: {e}, trying SQL...")

    # Fallback to SQL
    try:
        data = execute_sql("SHOW CATALOGS")
        if data:
            catalogs = [row[0] for row in data if row and row[0] and not row[0].startswith('__')]
            print(f"Found catalogs via SQL: {catalogs}")
            return catalogs
        return []
    except Exception as e:
        print(f"Error getting catalogs: {e}")
        return [f"Error: {str(e)}"]

def get_schemas(catalog):
    """Get list of schemas in selected catalog"""
    if not catalog or catalog.startswith("Error"):
        return []
    try:
        data = execute_sql(f"SHOW SCHEMAS IN {catalog}")
        # data_array doesn't include header row
        if data:
            schemas = [row[0] for row in data if row and row[0]]
            return schemas
        return []
    except Exception as e:
        return [f"Error: {str(e)}"]

def check_test_tables_exist(catalog, schema):
    """Check if _test tables exist"""
    try:
        data = execute_sql(f"SHOW TABLES IN {catalog}.{schema}")
        if len(data) > 1:
            tables = [row[1] for row in data[1:]]  # Second column is table name
            test_tables = [t for t in tables if t.endswith('_test')]
            return len(test_tables) > 0, test_tables
        return False, []
    except:
        return False, []

def create_tag_policy(tag_key, description, values, use_user_token=False, user_token=None):
    """Create a tag policy via REST API using WorkspaceClient's built-in auth"""
    payload = {
        "tag_key": tag_key,
        "description": description,
        "values": [{"name": v} for v in values]
    }

    try:
        workspace_url = w.config.host.rstrip('/')

        # Build headers - use user token if provided, else use service principal
        if use_user_token and user_token:
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            }
        else:
            # Use WorkspaceClient's built-in auth via api_client
            # Make the request through the SDK's api_client which handles auth
            try:
                result = w.api_client.do(
                    "POST",
                    "/api/2.1/tag-policies",
                    body=payload
                )
                return True, f"✅ Created: {tag_key}"
            except Exception as api_err:
                err_str = str(api_err)
                if "ALREADY_EXISTS" in err_str or "already exists" in err_str.lower():
                    return True, f"ℹ️  Already exists: {tag_key}"
                return False, f"❌ Failed: {tag_key} - {err_str[:100]}"

        # Only use requests if we have a user token
        response = requests.post(
            f"{workspace_url}/api/2.1/tag-policies",
            headers=headers,
            json=payload
        )

        # Handle empty responses
        if response.status_code == 200:
            return True, f"✅ Created: {tag_key}"

        # Try to parse JSON response for errors
        try:
            result = response.json()
            if response.status_code == 409 or result.get('error_code') == 'ALREADY_EXISTS':
                return True, f"ℹ️  Already exists: {tag_key}"
            else:
                return False, f"❌ Failed: {tag_key} - {result.get('message', response.text[:100])}"
        except:
            if response.status_code == 409:
                return True, f"ℹ️  Already exists: {tag_key}"
            return False, f"❌ Failed: {tag_key} - HTTP {response.status_code}: {response.text[:100]}"

    except Exception as e:
        return False, f"❌ Error: {tag_key} - {str(e)}"

# Step 1: Deploy Functions
def deploy_functions(catalog, schema, industry, use_user_auth, request: gr.Request, progress=gr.Progress()):
    """Deploy functions to selected catalog and schema"""
    try:
        # Validate inputs
        if not catalog or not schema or not industry:
            return f"❌ **Error**: Missing required fields\n\n- Catalog: {'✅' if catalog else '❌ Not selected'}\n- Schema: {'✅' if schema else '❌ Not selected'}\n- Industry: {'✅' if industry else '❌ Not selected'}\n\nPlease fill in all fields and try again."

        # Show what was selected for debugging
        progress(0.0, desc=f"Selected: {catalog}.{schema} ({industry})")

        # Extract user token if using user authorization
        user_token = None
        auth_mode = "Service Principal"
        if use_user_auth:
            user_token = request.headers.get("X-Forwarded-Access-Token")
            if user_token:
                auth_mode = f"User ({request.headers.get('X-Forwarded-Email', 'Unknown')})"
            else:
                return "❌ **Error**: User authorization selected but no access token found"

        progress(0.05, desc=f"Auth: {auth_mode} | Checking catalog access...")
        try:
            # Verify catalog exists and we have access
            execute_sql(f"USE CATALOG {catalog}", "Use catalog", user_token)
        except Exception as e:
            return f"❌ **Error**: Cannot access catalog `{catalog}`\n\n{str(e)}\n\n**Solution:**\n```sql\nGRANT USE CATALOG ON CATALOG {catalog} TO `your_user_or_sp`;\n```"

        progress(0.1, desc=f"Creating schema {catalog}.{schema}...")
        try:
            # Create schema using fully qualified name (works regardless of context)
            execute_sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}", "Create schema", user_token)
            # Verify schema was created/exists
            execute_sql(f"DESCRIBE SCHEMA {catalog}.{schema}", "Verify schema", user_token)
        except Exception as e:
            return f"❌ **Error**: Could not create schema `{catalog}.{schema}`\n\n{str(e)}\n\n**Possible causes:**\n- Missing CREATE SCHEMA permission\n- Schema name contains invalid characters\n- Catalog doesn't exist\n\n**Solution:**\n```sql\nGRANT CREATE SCHEMA ON CATALOG {catalog} TO `your_user_or_sp`;\nGRANT USE SCHEMA ON SCHEMA {catalog}.{schema} TO `your_user_or_sp`;\n```"

        progress(0.2, desc="Loading industry template...")
        try:
            template = load_industry_template(industry)
            sql_statements = template.FUNCTIONS_SQL
        except ValueError as e:
            return f"❌ Error: {str(e)}"

        # Replace with fully qualified names
        sql_statements = sql_statements.replace("CREATE OR REPLACE FUNCTION ", f"CREATE OR REPLACE FUNCTION {catalog}.{schema}.")

        # Split by semicolon and keep only parts that contain CREATE FUNCTION
        statements = [s.strip() for s in sql_statements.split(';')
                     if s.strip() and ('CREATE' in s.upper() and 'FUNCTION' in s.upper())]
        total = len(statements)

        progress(0.3, desc=f"Creating {total} functions...")

        success_count = 0
        errors = []

        for idx, stmt in enumerate(statements):
            try:
                if stmt.strip():
                    func_name = "unknown"
                    if "CREATE" in stmt.upper() and "FUNCTION" in stmt.upper():
                        parts = stmt.upper().split("FUNCTION")
                        if len(parts) > 1:
                            func_name = parts[1].split("(")[0].strip()

                    execute_sql(stmt, f"CREATE FUNCTION {func_name}", user_token)
                    success_count += 1
                    progress((0.3 + (0.6 * (idx + 1) / total)),
                           desc=f"Created {idx + 1}/{total}")
            except Exception as e:
                errors.append(f"Function {idx + 1} ({func_name}):\n{str(e)[:300]}")

        progress(1.0, desc="Complete!")

        if success_count == total:
            return f"✅ **Step 1 Complete!**\n\n📊 **Created {success_count} functions** in `{catalog}.{schema}`\n\n**Next:** Create tag policies (Step 2)"
        elif success_count > 0:
            result = f"⚠️ **Partial Success**\n\n✅ Created: {success_count}/{total}\n❌ Failed: {len(errors)}\n\n"
            for err in errors[:2]:
                result += f"\n{err}\n"
            return result
        else:
            result = f"❌ **All functions failed**\n\n"
            for err in errors[:3]:
                result += f"\n{err}\n" + "-"*50 + "\n"
            return result

    except Exception as e:
        return f"❌ **Deployment Failed**\n\n{str(e)}"

# Step 2: Create Tag Policies
def deploy_tag_policies(catalog, schema, industry, use_user_auth, request: gr.Request, progress=gr.Progress()):
    """Create tag policies for the industry"""
    try:
        if not catalog or not schema or not industry:
            return "❌ Error: Please select catalog, schema, and industry"

        # Extract user token if using user authorization
        user_token = None
        auth_mode = "Service Principal"
        if use_user_auth:
            user_token = request.headers.get("X-Forwarded-Access-Token")
            if user_token:
                auth_mode = f"User ({request.headers.get('X-Forwarded-Email', 'Unknown')})"
            else:
                return "❌ **Error**: User authorization selected but no access token found"

        progress(0.05, desc=f"Auth: {auth_mode} | Loading template...")
        try:
            template = load_industry_template(industry)
        except ValueError as e:
            return f"❌ Error: {str(e)}"

        progress(0.2, desc="Creating tag policies...")

        results = []
        success_count = 0

        for idx, (tag_key, desc, values) in enumerate(template.TAG_DEFINITIONS):
            success, msg = create_tag_policy(tag_key, desc, values, use_user_auth, user_token)
            results.append(msg)
            if success:
                success_count += 1
            progress(0.2 + (0.7 * (idx + 1) / len(template.TAG_DEFINITIONS)),
                   desc=f"Created {idx + 1}/{len(template.TAG_DEFINITIONS)}")

        progress(1.0, desc="Complete!")

        output = f"✅ **Step 2 Complete!**\n\n📊 **Created {success_count}/{len(template.TAG_DEFINITIONS)} tag policies**\n\n"
        for r in results:
            output += f"{r}\n"

        output += f"\n**Next:** Create ABAC policies (Step 3)"
        return output

    except Exception as e:
        return f"❌ **Tag Policy Creation Failed**\n\n{str(e)}"

# Step 3: Create ABAC Policies
def deploy_abac_policies(catalog, schema, industry, use_user_auth, request: gr.Request, progress=gr.Progress()):
    """Create ABAC policies"""
    try:
        if not catalog or not schema or not industry:
            return "❌ Error: Please select catalog, schema, and industry"

        # Extract user token if using user authorization
        user_token = None
        auth_mode = "Service Principal"
        if use_user_auth:
            user_token = request.headers.get("X-Forwarded-Access-Token")
            if user_token:
                auth_mode = f"User ({request.headers.get('X-Forwarded-Email', 'Unknown')})"
            else:
                return "❌ **Error**: User authorization selected but no access token found"

        progress(0.05, desc=f"Auth: {auth_mode} | Loading template...")
        try:
            template = load_industry_template(industry)
        except ValueError as e:
            return f"❌ Error: {str(e)}"

        progress(0.1, desc="Reading ABAC policy definitions...")

        # Replace placeholders
        policies_sql = template.ABAC_POLICIES_SQL.replace("{CATALOG}", catalog).replace("{SCHEMA}", schema)

        # Split by semicolon and keep only parts that contain CREATE POLICY
        statements = [s.strip() for s in policies_sql.split(';')
                     if s.strip() and ('CREATE' in s.upper() or 'DROP' in s.upper())]
        total = len(statements)

        progress(0.2, desc=f"Creating {total} ABAC policies...")

        success_count = 0
        errors = []

        for idx, stmt in enumerate(statements):
            try:
                if stmt.strip():
                    execute_sql(stmt, f"CREATE POLICY {idx+1}", user_token)
                    success_count += 1
                    progress(0.2 + (0.7 * (idx + 1) / total), desc=f"Created {idx + 1}/{total}")
            except Exception as e:
                errors.append(f"Policy {idx + 1}: {str(e)[:200]}")

        progress(1.0, desc="Complete!")

        if success_count == total:
            return f"✅ **Step 3 Complete!**\n\n📊 **Created {success_count} ABAC policies** in `{catalog}.{schema}`\n\n**Optional:** Create test data to try it out (Step 4)"
        else:
            result = f"⚠️ **Partial Success**\n\n✅ Created: {success_count}/{total}\n❌ Failed: {len(errors)}\n\n"
            for err in errors[:3]:
                result += f"{err}\n"
            return result

    except Exception as e:
        return f"❌ **ABAC Policy Creation Failed**\n\n{str(e)}"

# Step 4: Create Test Data (Optional)
def create_test_data(catalog, schema, industry, use_user_auth, request: gr.Request, progress=gr.Progress()):
    """Create test tables with sample data"""
    try:
        if not catalog or not schema or not industry:
            return "❌ Error: Please select catalog, schema, and industry"

        # Extract user token if using user authorization
        user_token = None
        auth_mode = "Service Principal"
        if use_user_auth:
            user_token = request.headers.get("X-Forwarded-Access-Token")
            if user_token:
                auth_mode = f"User ({request.headers.get('X-Forwarded-Email', 'Unknown')})"
            else:
                return "❌ **Error**: User authorization selected but no access token found"

        progress(0.05, desc=f"Auth: {auth_mode} | Loading template...")
        try:
            template = load_industry_template(industry)
        except ValueError as e:
            return f"❌ Error: {str(e)}"

        progress(0.1, desc="Reading table definitions...")

        # Replace with fully qualified names and add _test suffix
        tables_sql = template.TEST_TABLES_SQL.replace("CREATE TABLE IF NOT EXISTS ", f"CREATE TABLE IF NOT EXISTS {catalog}.{schema}.")
        tables_sql = tables_sql.replace("INSERT INTO ", f"INSERT INTO {catalog}.{schema}.")

        # Split by semicolon and keep only parts that contain SQL commands
        statements = [s.strip() for s in tables_sql.split(';')
                     if s.strip() and ('CREATE' in s.upper() or 'INSERT' in s.upper())]
        total = len(statements)

        progress(0.2, desc=f"Creating test tables...")

        success_count = 0
        errors = []

        for idx, stmt in enumerate(statements):
            try:
                if stmt.strip():
                    execute_sql(stmt, f"Table operation {idx+1}", user_token)
                    success_count += 1
                    progress(0.2 + (0.7 * (idx + 1) / total), desc=f"Executed {idx + 1}/{total}")
            except Exception as e:
                errors.append(f"Statement {idx + 1}: {str(e)[:200]}")

        progress(1.0, desc="Complete!")

        if success_count > 0:
            tables_list = "\n".join([f"- {t}" for t in template.TEST_TABLES])
            return f"✅ **Test Data Created!**\n\n📊 **Executed {success_count}/{total} statements**\n\nTables created:\n{tables_list}\n\n**Next:** Tag the test data (Step 5)"
        else:
            result = f"❌ **Test Data Creation Failed**\n\n"
            for err in errors[:3]:
                result += f"{err}\n"
            return result

    except Exception as e:
        return f"❌ **Test Data Creation Failed**\n\n{str(e)}"

# Step 5: Tag Test Data (Optional, conditional)
def tag_test_data(catalog, schema, industry, use_user_auth, request: gr.Request, progress=gr.Progress()):
    """Apply tags to test table columns"""
    try:
        if not catalog or not schema or not industry:
            return "❌ Error: Please select catalog, schema, and industry"

        # Extract user token if using user authorization
        user_token = None
        auth_mode = "Service Principal"
        if use_user_auth:
            user_token = request.headers.get("X-Forwarded-Access-Token")
            if user_token:
                auth_mode = f"User ({request.headers.get('X-Forwarded-Email', 'Unknown')})"
            else:
                return "❌ **Error**: User authorization selected but no access token found"

        # Check if test tables exist
        exists, test_tables = check_test_tables_exist(catalog, schema)
        if not exists:
            return "⚠️ **No test tables found!**\n\nCreate test data first (Step 4)"

        progress(0.05, desc=f"Auth: {auth_mode} | Loading template...")
        try:
            template = load_industry_template(industry)
        except ValueError as e:
            return f"❌ Error: {str(e)}"

        progress(0.1, desc="Applying tags to test tables...")

        # Replace placeholders with actual catalog and schema
        tagging_sql = template.TAG_APPLICATIONS_SQL
        tagging_sql = tagging_sql.replace("{CATALOG}", catalog)
        tagging_sql = tagging_sql.replace("{SCHEMA}", schema)

        # Split by semicolon and keep only parts that contain ALTER
        statements = [s.strip() for s in tagging_sql.split(';')
                     if s.strip() and 'ALTER' in s.upper()]
        total = len(statements)

        progress(0.2, desc=f"Tagging columns...")

        success_count = 0
        errors = []

        for idx, stmt in enumerate(statements):
            try:
                if stmt.strip():
                    execute_sql(stmt, f"Tag column {idx+1}", user_token)
                    success_count += 1
                    progress(0.2 + (0.7 * (idx + 1) / total), desc=f"Tagged {idx + 1}/{total}")
            except Exception as e:
                errors.append(f"Tag {idx + 1}: {str(e)[:150]}")

        progress(1.0, desc="Complete!")

        if success_count > 0:
            return f"✅ **Tags Applied!**\n\n🏷️ **Tagged {success_count} columns** across test tables\n\n**Next:** Test the policies (Step 6)"
        else:
            result = f"❌ **Tagging Failed**\n\n"
            for err in errors[:3]:
                result += f"{err}\n"
            return result

    except Exception as e:
        return f"❌ **Tagging Failed**\n\n{str(e)}"

# Step 6: Test Policies (Optional, conditional)
def test_policies(catalog, schema, industry, use_user_auth, request: gr.Request, progress=gr.Progress()):
    """Run test queries to demonstrate ABAC policies"""
    try:
        if not catalog or not schema or not industry:
            return "❌ Error: Please select catalog, schema, and industry"

        # Extract user token if using user authorization
        user_token = None
        auth_mode = "Service Principal"
        if use_user_auth:
            user_token = request.headers.get("X-Forwarded-Access-Token")
            if user_token:
                auth_mode = f"User ({request.headers.get('X-Forwarded-Email', 'Unknown')})"
            else:
                return "❌ **Error**: User authorization selected but no access token found"

        # Check if test tables exist
        exists, test_tables = check_test_tables_exist(catalog, schema)
        if not exists:
            return "⚠️ **No test tables found!**\n\nCreate test data first (Step 4)"

        progress(0.1, desc=f"Auth: {auth_mode} | Loading template...")
        try:
            template = load_industry_template(industry)
        except ValueError as e:
            return f"❌ Error: {str(e)}"

        progress(0.2, desc="Running test queries...")

        # Simple test queries to show masking works
        test_queries = []
        for table in test_tables:
            test_queries.append(f"SELECT * FROM {catalog}.{schema}.{table} LIMIT 2;")

        results = []

        for idx, query in enumerate(test_queries):
            try:
                data = execute_sql(query, f"Test query {idx+1}", user_token)
                row_count = len(data) if data else 0
                results.append(f"✅ Query {idx+1} succeeded ({row_count} rows)")
                progress(0.2 + (0.7 * (idx + 1) / len(test_queries)), desc=f"Tested {idx + 1}/{len(test_queries)}")
            except Exception as e:
                results.append(f"⚠️ Query {idx+1} failed: {str(e)[:100]}")

        progress(1.0, desc="Complete!")

        output = f"✅ **Testing Complete!**\n\n📊 **Test Results:**\n\n"
        for r in results:
            output += f"- {r} \n"

        output += f"\n\n**Note:** Check the actual data in Databricks to see masking in action!"
        output += f"\n\nQuery your test tables:\n\n"
        for q in test_queries:
            output += f"- `{q}` \n"

        return output

    except Exception as e:
        return f"❌ **Testing Failed**\n\n{str(e)}"

# Gradio UI
with gr.Blocks(title="ABAC Industry Templates Deployer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🏭 ABAC Industry Templates Deployer")

    with gr.Tabs():
        with gr.Tab("🚀 Deployer"):
            gr.Markdown("""
            Deploy complete ABAC (Attribute-Based Access Control) setup to your Unity Catalog.
            
            ### Workflow:
            **Required Steps:**
            1. **Set Service Principal Permissions** - Grant privileges listed in 'Documentation' tab
            2. **Create Functions** - Deploy masking/filtering UDFs
            3. **Create Tag Policies** - Define governed tags
            4. **Create ABAC Policies** - Apply policies using tags
            
            **Optional Testing Steps:**\n
            5. **Create Test Data** - Generate sample tables (with _test suffix)\n
            6. **Tag Test Data** - Apply tags to test tables\n
            7. **Test Policies** - Run queries to verify masking works\n
            """)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Configuration")
                    catalog_dropdown = gr.Dropdown(
                        choices=get_catalogs(),
                        value=None,
                        label="Catalog",
                        info="Select target catalog",
                        interactive=True
                    )

                    schema_dropdown = gr.Dropdown(
                        label="Schema",
                        info="Select existing or type to create new schema",
                        interactive=True,
                        allow_custom_value=True
                    )

                    industry_dropdown = gr.Dropdown(
                        choices=get_available_industries(),
                        value="Finance",
                        label="Industry",
                        info="Select industry template",
                        interactive=True
                    )

                    use_user_auth = gr.Checkbox(
                        label="Use User Authorization",
                        value=False,
                        info="Run as your user (checked) or Service Principal (unchecked)"
                    )

                    refresh_btn = gr.Button("🔄 Refresh", size="sm")

                with gr.Column():
                    gr.Markdown("### Industry Templates Available:")
                    gr.Markdown("""
                    **7 Industries:**
                    - Finance ✅ Complete
                    - Healthcare ✅ Complete
                    - Insurance ✅ Complete
                    - Manufacturing ✅ Complete
                    - Retail ⚙️ Partial
                    - Telco ⚙️ Partial
                    - Government ⚙️ Partial
                    
                    **Each includes:**
                    - Masking/filtering functions
                    - Tag policy definitions
                    - ABAC policies (complete or placeholder)
                    - Test data templates
                    """)

            gr.Markdown("---")
            gr.Markdown("## Required Steps")

            with gr.Row():
                deploy_functions_btn = gr.Button("1️⃣ Create Functions", variant="primary", size="lg")
                deploy_tags_btn = gr.Button("2️⃣ Create Tag Policies", variant="primary", size="lg")
                deploy_abac_btn = gr.Button("3️⃣ Create ABAC Policies", variant="primary", size="lg")

            output_required = gr.Markdown(label="Status")

            gr.Markdown("---")
            gr.Markdown("## Optional Testing Steps")

            with gr.Row():
                create_test_btn = gr.Button("4️⃣ Create Test Data", size="lg")
                tag_test_btn = gr.Button("5️⃣ Tag Test Data", size="lg")
                test_policies_btn = gr.Button("6️⃣ Test Policies", size="lg")

            output_optional = gr.Markdown(label="Test Status")

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

            # Required steps
            deploy_functions_btn.click(
                fn=deploy_functions,
                inputs=[catalog_dropdown, schema_dropdown, industry_dropdown, use_user_auth],
                outputs=[output_required]
            )

            deploy_tags_btn.click(
                fn=deploy_tag_policies,
                inputs=[catalog_dropdown, schema_dropdown, industry_dropdown, use_user_auth],
                outputs=[output_required]
            )

            deploy_abac_btn.click(
                fn=deploy_abac_policies,
                inputs=[catalog_dropdown, schema_dropdown, industry_dropdown, use_user_auth],
                outputs=[output_required]
            )

            # Optional testing steps
            create_test_btn.click(
                fn=create_test_data,
                inputs=[catalog_dropdown, schema_dropdown, industry_dropdown, use_user_auth],
                outputs=[output_optional]
            )

            tag_test_btn.click(
                fn=tag_test_data,
                inputs=[catalog_dropdown, schema_dropdown, industry_dropdown, use_user_auth],
                outputs=[output_optional]
            )

            test_policies_btn.click(
                fn=test_policies,
                inputs=[catalog_dropdown, schema_dropdown, industry_dropdown, use_user_auth],
                outputs=[output_optional]
            )

        with gr.Tab("📚 Documentation"):
            gr.Markdown(DOCUMENTATION_MD)

    gr.Markdown("""
    ---
    ### 📚 Resources
    - [Unity Catalog ABAC Documentation](https://docs.databricks.com/data-governance/unity-catalog/abac/)
    - [GitHub Repository](https://github.com/AbhiDatabricks/sandbox)
    """)

if __name__ == "__main__":
    demo.launch()
