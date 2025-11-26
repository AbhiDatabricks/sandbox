## Finance ABAC Demo

A comprehensive ABAC (Attribute-Based Access Control) demonstration for the finance industry, featuring banking, payments, credit, and compliance use cases.

### 📊 Overview

**Database Schema (5 tables, 120 rows)**
- `customers` (20 rows) - Customer master data with PII (SSN, income, credit scores)
- `accounts` (25 rows) - Bank accounts (checking, savings)
- `credit_cards` (25 rows) - Credit card accounts (Visa, Mastercard, Amex, Discover)
- `transactions` (30 rows) - Financial transactions with fraud flags
- `loans` (20 rows) - Personal loans, auto loans, mortgages

**Masking Functions (16 total)**
- `mask_credit_card` - PCI-DSS compliant (show last 4)
- `mask_account_last4` - Bank account masking
- `mask_ssn_last4` - SSN masking (XXX-XX-1234)
- `mask_email` - Email privacy
- `mask_phone` - Phone masking
- `mask_amount_bucket` - Transaction amount ranges
- `mask_routing_number` - Routing number protection
- `mask_transaction_hash` - Transaction ID hashing
- `mask_customer_id_deterministic` - Cross-table analytics
- `mask_ip_address` - IP privacy (last octet)
- `mask_address_city_state` - Geographic data only
- `mask_income_bracket` - Income ranges
- Plus 4 row filter functions (business hours, fraud, regional)

**Deployment Options**
- Interactive Notebooks (4 .ipynb files)
- Configuration file (`config.yaml`)

### 🎭 Masking Examples:

```
Credit Card:  4532-1234-5678-9010 → ****-****-****-9010 (PCI-DSS)
Account:      1001234567 → ****4567
SSN:          123-45-6789 → XXX-XX-6789
Email:        john.smith@email.com → ****@email.com
Phone:        395-555-0101 → XXXX0101
Amount:       $8750.80 → $5K-$10K (bucket)
Customer ID:  C-1001 → CUST_abc123... (deterministic for joins)
IP Address:   192.168.1.100 → 192.168.1.***
Income:       $75000 → $75K-$100K (bracket)
```

### 🔒 Financial Compliance Features:

**PCI-DSS Compliance:**
- Credit card numbers show last 4 only
- Account numbers masked
- Transaction data protected
- Audit trail maintained

**Fraud Detection:**
- 3 transactions flagged as fraudulent
- IP tracking for investigation
- Device fingerprinting
- Status tracking (Under Review, Disputed, Blocked)

**Privacy Protection:**
- SSN masking
- Email/phone obfuscation
- Income bracketing (not exact figures)
- Address partial masking

### 📊 Data Statistics:
```
Total Records: 120
- 20 Customers across 10 states
- 25 Bank accounts (checking/savings)
- 25 Credit cards (4 types: Visa, MC, Amex, Discover)
- 30 Transactions across 19 merchant categories
- 20 Loans (Personal, Auto, Mortgage)
```

### 🚀 Quick Start:

**Using Notebooks**
1. Import the 4 `.ipynb` files to Databricks
2. Edit `config.yaml` to set your catalog name
3. Run notebooks 1 → 2 → 3 → 4


### 🎓 Finance-Specific Use Cases:

**1. Cross-Account Analytics (Deterministic Masking)**
```sql
-- Analysts can join customer data across tables without seeing real IDs
SELECT 
  mask_customer_id_deterministic(c.customer_id) AS masked_id,
  COUNT(t.transaction_id) AS transaction_count,
  SUM(t.amount) AS total_spent
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id;
```

**2. PCI-DSS Compliance (Credit Card Masking)**
```sql
-- Support agents see last 4 for verification only
SELECT 
  mask_credit_card(card_number) AS masked_card,
  card_type,
  expiry_date
FROM credit_cards;
```

**3. Fraud Investigation (IP Tracking)**
```sql
-- Fraud team sees masked IPs to identify patterns
SELECT 
  transaction_id,
  mask_ip_address(ip_address) AS network,
  amount,
  fraud_flag
FROM transactions
WHERE fraud_flag = true;
```

**4. Credit Analysis (Income Brackets)**
```sql
-- Underwriters see income ranges, not exact figures
SELECT 
  mask_income_bracket(annual_income) AS income_bracket,
  credit_score,
  COUNT(*) AS customer_count
FROM customers
GROUP BY mask_income_bracket(annual_income), credit_score;
```

**5. Transaction Reporting (Amount Bucketing)**
```sql
-- Management dashboards with amount ranges
SELECT 
  merchant_category,
  mask_amount_bucket(amount) AS amount_range,
  COUNT(*) AS transaction_count
FROM transactions
GROUP BY merchant_category, mask_amount_bucket(amount);
```

### 📁 File Structure:
```
finance/
├── config.yaml                          # Configuration (edit this!)
├── 1_Create_Functions.ipynb             # Notebook: Create masking + filtering functions
├── 2_Create_Tables.ipynb                # Notebook: Create schema & tables
├── 3_Setup_Tagging.ipynb                # Notebook: Define governed tags
├── 4_Test_ABAC_Policies.ipynb           # Notebook: Test functions through ABAC policies
├── README.md                            # This file
```

### 🔧 Configuration:

Edit `config.yaml` to set your Unity Catalog and schema:
```yaml
catalog: "your_catalog_name"  # Change this
schema: "finance"
```

All notebooks will automatically use these settings.

### 📚 References:
- [PCI-DSS Standards](https://www.pcisecuritystandards.org/)
- [Unity Catalog ABAC Documentation](https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/)
- [Databricks Financial Services Solutions](https://www.databricks.com/solutions/industries/financial-services)

---

**Note**: This is a demonstration environment. For production PCI-DSS certification, consult with security and compliance teams.

