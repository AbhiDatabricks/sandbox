# ABAC Industry Demos for Unity Catalog

Comprehensive Attribute-Based Access Control (ABAC) demonstrations across 7 industries, featuring data masking, row filtering, and tag-based policies for Databricks Unity Catalog.

## 📊 Available Industries

| Industry | Description | Tables | Functions |
|----------|-------------|--------|-----------|
| **Retail** | Customer data, orders, products, reviews | 5 | 9 |
| **Telco** | Subscriber data, plans, usage, support | 4 | 7 |
| **Insurance** | Policies, claims, customers, payments | 4 | 6 |
| **Government** | Citizens, permits, services, payments | 4 | 7 |
| **Finance** | Accounts, transactions, loans, credit cards | 5 | 16 |
| **Manufacturing** | Assets, maintenance, specs, shipments | 6 | 17 |
| **Healthcare** | Patients, providers, visits, prescriptions | 6 | 9 |

---

## 🚀 Quick Start

### Step 1: Choose an Industry
Navigate to any industry folder:
```bash
cd retail/    # or telco, insurance, finance, etc.
```

### Step 2: Configure
Edit `config.yaml` with your Unity Catalog name:
```yaml
catalog: "your_catalog_name"  # Change this
schema: "retail"
```

### Step 3: Import Notebooks
Import the 4 `.ipynb` files to Databricks:
- `1_Create_Functions.ipynb` - Create masking functions
- `2_Create_Schema.ipynb` - Create database schema
- `3_Create_Extended_Tables.ipynb` - Add supplementary tables
- `4_Test_Masking.ipynb` - Test all functions

### Step 4: Run Sequentially
Execute notebooks in order (1 → 2 → 3 → 4). All notebooks automatically read from `config.yaml`.

---

## 📁 Structure

Each industry folder contains:

```
<industry>/
├── config.yaml                     # Configuration (edit this!)
├── 1_Create_Functions.ipynb        # Notebook: Masking functions
├── 2_Create_Schema.ipynb           # Notebook: Core schema
├── 3_Create_Extended_Tables.ipynb  # Notebook: Extended tables
├── 4_Test_Masking.ipynb            # Notebook: Testing
├── README.md                       # Industry-specific documentation
├── sql/                            # SQL source files
│   ├── 0.1<industry>_abac_functions.sql
│   ├── 0.2<industry>_database_schema.sql
│   ├── 0.3<industry>_extended_tables.sql
│   └── 6.Test<Industry>Data_Simple.sql
└── scripts/                        # Automation scripts (optional)
    ├── config.yaml
    └── execute_sql_configurable.py
```

---

## 🎯 Features

### Masking Functions
Each industry includes specialized masking functions:
- **Email masking** - Show domain only
- **Phone masking** - Show last 4 digits
- **Credit card masking** - PCI-DSS compliant
- **SSN masking** - Partial masking
- **Amount bucketing** - Privacy-preserving analytics
- **Deterministic hashing** - Cross-table joins
- **Complete redaction** - Sensitive fields
- **Industry-specific functions** - Tailored to each domain

### Row Filters
Time-based and attribute-based row filtering:
- Business hours only
- Regional access control
- Role-based filtering
- Sensitive data access

### Tag-Based Policies
Pre-defined tags for ABAC policies:
- PII levels
- Data classification
- Compliance requirements (PCI, HIPAA, etc.)
- Purpose limitation

---

## 💡 Deployment Methods

### Method 1: Notebooks (Recommended)
**Best for**: Demos, training, interactive use

1. Import `.ipynb` files to Databricks
2. Edit `config.yaml`
3. Run notebooks sequentially

**Pros**: Rich documentation, interactive, easy to customize

---

### Method 2: SQL Files
**Best for**: SQL-focused users, quick setup

1. Import SQL files from `sql/` folder to Databricks
2. Files become Databricks SQL notebooks automatically
3. Run in order

**Pros**: Lightweight, SQL-native

---

### Method 3: Python Automation
**Best for**: CI/CD, automation, batch deployment

1. Edit `scripts/config.yaml`
2. Run: `python scripts/execute_sql_configurable.py`

**Pros**: Fully automated, repeatable, CI/CD friendly

---

## 🔧 Configuration

### Single Source of Truth
All 4 notebooks in each industry read from one `config.yaml`:

```yaml
# config.yaml
catalog: "your_catalog"  # Change once
schema: "industry_name"
```

No hardcoding in notebooks - everything comes from config!

### Benefits
- ✅ Edit one file, affects all notebooks
- ✅ No searching for hardcoded values
- ✅ Consistent across all notebooks
- ✅ Less error-prone

---

## 📚 Industry-Specific Features

### Retail
- Customer PII masking
- Transaction amount bucketing
- Product cost redaction
- Order amount privacy

### Telco
- Subscriber data protection
- Network usage masking
- Billing data privacy
- Device information redaction

### Insurance
- Policy number masking
- Claim amount bucketing
- Customer PII protection
- Payment data privacy

### Government
- Citizen data protection
- Permit information masking
- Service record privacy
- Payment details redaction

### Finance
- **PCI-DSS compliant** credit card masking
- SSN masking (XXX-XX-1234)
- Account number protection
- Transaction amount bucketing
- Income bracketing
- Fraud detection scenarios

### Manufacturing
- **Intellectual property** protection
- Product spec redaction
- CAD file URI hashing
- Supplier cost masking
- GPS precision reduction
- Employee PII protection

### Healthcare
- **HIPAA compliant** PHI masking
- Patient name partial masking
- DOB to age groups
- Insurance number masking
- Provider information protection
- Prescription data privacy

---

## 🎓 Use Cases

### 1. Data Governance
Demonstrate Unity Catalog ABAC capabilities with industry-specific examples.

### 2. Compliance
Show PCI-DSS, HIPAA, GDPR, and CCPA compliance patterns.

### 3. Role-Based Access
Implement different data views for:
- Analysts (aggregated data)
- Support staff (masked PII)
- Administrators (full access)
- Auditors (read-only)

### 4. Self-Service Analytics
Enable data access while protecting sensitive information.

### 5. Training & Demos
Industry-specific scenarios for customer demonstrations and internal training.

---

## 🔐 Compliance

### PCI-DSS (Finance, Retail)
- Credit card number masking (last 4 only)
- Account number protection
- Transaction data safeguards
- Audit trail maintenance

### HIPAA (Healthcare)
- PHI masking and redaction
- Patient identifier protection
- Provider information safeguards
- Temporal access controls

### GDPR (All Industries)
- PII masking and anonymization
- Right to be forgotten patterns
- Data minimization examples
- Purpose limitation demonstrations

---

## 📊 Data Statistics

| Industry | Tables | Total Rows | Functions | Tags |
|----------|--------|------------|-----------|------|
| Retail | 5 | 26 | 9 | 3 |
| Telco | 4 | 12 | 7 | 3 |
| Insurance | 4 | 11 | 6 | 3 |
| Government | 4 | 11 | 7 | 3 |
| Finance | 5 | 120 | 16 | 3 |
| Manufacturing | 6 | 153 | 17 | 3 |
| Healthcare | 6 | 92 | 9 | 8 |

**Total**: 34 tables, 425+ rows, 71 functions across 7 industries

---

## 🛠️ Prerequisites

- Databricks workspace with Unity Catalog enabled
- SQL Warehouse or Cluster
- CREATE SCHEMA permission
- CREATE FUNCTION permission
- CREATE TABLE permission

---

## 📖 Documentation

Each industry folder contains:
- **README.md** - Industry-specific documentation
- **Notebooks** - Step-by-step implementation guides
- **SQL files** - Raw SQL for reference

---

## 🤝 Contributing

To add a new industry:

1. Create industry folder: `mkdir new_industry`
2. Add SQL files to `new_industry/sql/`
3. Create 4 notebooks following the pattern
4. Add `config.yaml`
5. Update this README

---

## 📚 Additional Resources

- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [ABAC Documentation](https://docs.databricks.com/data-governance/unity-catalog/attribute-based-access-control.html)
- [Row and Column Filters](https://docs.databricks.com/security/privacy/row-and-column-filters.html)
- [Data Masking](https://docs.databricks.com/security/privacy/data-masking.html)

---

## ⚠️ Important Notes

- **Demo Environment**: These are demonstrations, not production-ready implementations
- **Compliance**: For production compliance (PCI-DSS, HIPAA), consult security/compliance teams
- **Testing**: Always test in non-production environments first
- **Customization**: Adapt masking functions and policies to your specific requirements

---

## 🎯 Getting Help

1. Check industry-specific README.md files
2. Review notebook documentation (comprehensive explanations in each cell)
3. Examine SQL files in `sql/` folders for raw queries
4. Refer to Databricks Unity Catalog documentation

---

**Version**: 2.0  
**Last Updated**: October 2025  
**Status**: Production-Ready Demonstrations

---

## 🏆 Best Practices

### Security
- Start with most restrictive policies
- Test with different user roles
- Audit policy effectiveness regularly
- Document all access patterns

### Performance
- Use deterministic masking for joins
- Cache frequently accessed masked data
- Monitor query performance impact
- Optimize row filters

### Maintenance
- Keep functions and policies in version control
- Document policy changes
- Regular compliance reviews
- Update masking logic as regulations change

---

**Ready to get started?** Choose an industry folder and begin with the notebooks!

