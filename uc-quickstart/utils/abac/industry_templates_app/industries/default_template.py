"""
================================================================================
DEFAULT INDUSTRY ABAC TEMPLATE - COMPREHENSIVE SUPER-SET
================================================================================

This is the **MASTER TEMPLATE** containing the maximum coverage of all ABAC 
(Attribute-Based Access Control) capabilities. All other industry-specific 
templates (Finance, Healthcare, Manufacturing, etc.) are SUBSETS of this template.

TEMPLATE STATISTICS:
--------------------
| Component              | Count | Description                                    |
|------------------------|-------|------------------------------------------------|
| Column Masking Funcs   | 20    | Cover ALL PII types (SSN, email, phone, etc.)  |
| Row Filter Functions   | 8     | Time, value, flag, and status-based filters    |
| Tag Policies           | 8     | Generic names (no industry suffix)             |
| ABAC Policies          | 15    | 12 column masks + 3 row filters                |
| Test Tables            | 5     | Comprehensive test data with 46 total rows     |

COMPLIANCE FRAMEWORK MAPPING:
-----------------------------
| Framework   | Covered PII Types                                          |
|-------------|-----------------------------------------------------------|
| PCI-DSS     | credit_card, account_number, routing_number                |
| HIPAA       | ssn, dob, name, address, medical_record                    |
| GDPR        | ALL PII types (right to be forgotten, pseudonymization)    |
| CCPA        | ALL PII types (California consumer data)                   |
| SOX         | financial_record, audit trails                             |
| GLBA        | ssn, account_number, financial_record                      |
| FERPA       | name, dob, educational records                             |

NAMING CONVENTIONS:
-------------------
- Functions: `mask_<what>` for masking, `filter_<condition>` for row filters
- Tags: Generic names without industry suffix (e.g., `pii_type` not `pii_type_finance`)
- Policies: `mask_<type>_policy` or `filter_<condition>_policy`
- Test tables: `<entity>_test` suffix

USAGE NOTES:
------------
1. Deploy this template for MAXIMUM coverage across all use cases
2. Tag your columns with `pii_type` values to automatically apply masking
3. Tag your tables with `access_restriction` values to apply row filters
4. All policies apply to `account users` group by default (i.e., regular users)
5. Admins/owners see unmasked data unless explicitly included in policy target

QUICK START:
------------
1. Run Step 1 (Create Functions) to deploy all 28 functions
2. Run Step 2 (Create Tag Policies) to create the 8 tag definitions
3. Run Step 3 (Create ABAC Policies) to apply the 15 catalog-level policies
4. (Optional) Run Step 4-6 to create test data and verify masking works

For industry-specific templates with specialized naming conventions, see:
- finance_template.py (Banking, PCI-DSS focus)
- healthcare_template.py (HIPAA focus)
- manufacturing_template.py (IP protection, supply chain)
- insurance_template.py (Claims, underwriting)
- retail_template.py (E-commerce, customer data)
- telco_template.py (Subscriber data, CDRs)
- government_template.py (Security clearances, CUI)

================================================================================
"""

# =============================================================================
# TEMPLATE METADATA
# =============================================================================
INDUSTRY_NAME = "Default"
INDUSTRY_DESCRIPTION = (
    "Comprehensive ABAC super-set template with maximum coverage: "
    "20 masking functions, 8 row filters, 8 tag policies, 15 ABAC policies, "
    "and 5 test tables. Recommended for most use cases."
)

# =============================================================================
# STEP 1: MASKING AND FILTER FUNCTIONS
# =============================================================================
# Total: 28 functions (20 column masks + 8 row filters)
#
# FUNCTION CATEGORIES:
# --------------------
# A. Identity Masking (6): SSN, name, email, phone, address, DOB
# B. Financial Masking (4): credit card, account, routing, amount
# C. Technical Masking (4): IP address, device ID, timestamp, GPS
# D. General Purpose (6): string hash, partial mask, ID deterministic, etc.
# E. Row Filters (8): time-based, value-based, flag-based, status-based
#
# EXAMPLE USAGE:
# --------------
# SELECT mask_ssn(ssn) FROM customers;  -- Returns 'XXX-XX-6789'
# SELECT mask_email(email) FROM users;  -- Returns '****@example.com'
# SELECT * FROM sensitive_data WHERE filter_business_hours();  -- 9AM-5PM only
#
# =============================================================================

FUNCTIONS_SQL = """
-- #############################################################################
-- #                                                                           #
-- #                    COLUMN MASKING FUNCTIONS (20)                          #
-- #                                                                           #
-- # These functions transform sensitive data to protect privacy while         #
-- # preserving enough information for business operations.                    #
-- #                                                                           #
-- #############################################################################

-- =============================================================================
-- FUNCTION 1: mask_ssn
-- =============================================================================
-- PURPOSE:     Mask Social Security Numbers showing only last 4 digits
-- COMPLIANCE:  HIPAA, GLBA, CCPA, GDPR (pseudonymization)
-- INPUT:       '123-45-6789' or '123456789'
-- OUTPUT:      'XXX-XX-6789'
-- USE CASES:   Customer records, employee data, tax documents
-- NOTES:       Handles both formatted (###-##-####) and unformatted input
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_ssn(ssn STRING)
RETURNS STRING
COMMENT 'Mask SSN showing last 4 digits. Input: 123-45-6789 → Output: XXX-XX-6789. Compliant with HIPAA, GLBA, CCPA.'
RETURN CASE 
  WHEN ssn IS NULL OR ssn = '' THEN ssn 
  ELSE CONCAT('XXX-XX-', RIGHT(REGEXP_REPLACE(ssn, '[^0-9]', ''), 4)) 
END;

-- =============================================================================
-- FUNCTION 2: mask_email
-- =============================================================================
-- PURPOSE:     Mask email local part while preserving domain for context
-- COMPLIANCE:  GDPR (pseudonymization), CCPA
-- INPUT:       'john.smith@company.com'
-- OUTPUT:      '****@company.com'
-- USE CASES:   Contact lists, user accounts, marketing databases
-- NOTES:       Domain preserved for organizational context; local part hidden
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_email(email STRING)
RETURNS STRING
COMMENT 'Mask email local part, preserve domain. Input: john@example.com → Output: ****@example.com'
RETURN CASE 
  WHEN email IS NULL OR email = '' THEN email
  WHEN LOCATE('@', email) = 0 THEN '****'
  ELSE CONCAT('****@', SUBSTRING(email, LOCATE('@', email) + 1))
END;

-- =============================================================================
-- FUNCTION 3: mask_phone
-- =============================================================================
-- PURPOSE:     Mask phone numbers showing only last 4 digits
-- COMPLIANCE:  TCPA, GDPR, CCPA
-- INPUT:       '555-123-4567' or '5551234567' or '+1-555-123-4567'
-- OUTPUT:      'XXX-XXX-4567'
-- USE CASES:   Customer contact info, CRM systems, call center data
-- NOTES:       Handles various phone formats; strips non-numeric before masking
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_phone(phone STRING)
RETURNS STRING
COMMENT 'Mask phone number showing last 4 digits. Input: 555-123-4567 → Output: XXX-XXX-4567'
RETURN CASE 
  WHEN phone IS NULL OR phone = '' THEN phone
  WHEN LENGTH(REGEXP_REPLACE(phone, '[^0-9]', '')) < 4 THEN 'XXXX'
  ELSE CONCAT('XXX-XXX-', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4))
END;

-- =============================================================================
-- FUNCTION 4: mask_credit_card
-- =============================================================================
-- PURPOSE:     PCI-DSS compliant credit card masking (BIN + last 4 optional)
-- COMPLIANCE:  PCI-DSS Requirement 3.4 (render PAN unreadable)
-- INPUT:       '4532-1234-5678-9010' or '4532123456789010'
-- OUTPUT:      '****-****-****-9010'
-- USE CASES:   Payment processing, transaction logs, receipts
-- NOTES:       Shows only last 4 digits per PCI-DSS; first 6 (BIN) also allowed
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_credit_card(card_number STRING)
RETURNS STRING
COMMENT 'PCI-DSS compliant credit card masking. Input: 4532-1234-5678-9010 → Output: ****-****-****-9010'
RETURN CASE
  WHEN card_number IS NULL OR card_number = '' THEN card_number
  ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card_number, '[^0-9]', ''), 4))
END;

-- =============================================================================
-- FUNCTION 5: mask_account_number
-- =============================================================================
-- PURPOSE:     Mask bank/financial account numbers showing only last 4 digits
-- COMPLIANCE:  GLBA, SOX, PCI-DSS (for stored account data)
-- INPUT:       '1234567890' (any length)
-- OUTPUT:      '******7890'
-- USE CASES:   Bank statements, ACH processing, financial reports
-- NOTES:       Dynamically adjusts masking length based on input length
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_account_number(account_number STRING)
RETURNS STRING
COMMENT 'Mask account number showing last 4 digits. Input: 1234567890 → Output: ******7890'
RETURN CASE
  WHEN account_number IS NULL OR account_number = '' THEN account_number
  WHEN LENGTH(account_number) <= 4 THEN REPEAT('*', LENGTH(account_number))
  ELSE CONCAT(REPEAT('*', LENGTH(account_number) - 4), RIGHT(account_number, 4))
END;

-- =============================================================================
-- FUNCTION 6: mask_routing_number
-- =============================================================================
-- PURPOSE:     Mask ABA routing numbers showing only last 2 digits
-- COMPLIANCE:  GLBA, NACHA Operating Rules
-- INPUT:       '021000021'
-- OUTPUT:      '*******21'
-- USE CASES:   ACH processing, wire transfers, bank verification
-- NOTES:       US routing numbers are always 9 digits; last 2 sufficient for ID
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_routing_number(routing_number STRING)
RETURNS STRING
COMMENT 'Mask routing number showing last 2 digits. Input: 021000021 → Output: *******21'
RETURN CASE
  WHEN routing_number IS NULL OR routing_number = '' THEN routing_number
  ELSE CONCAT('*******', RIGHT(routing_number, 2))
END;

-- =============================================================================
-- FUNCTION 7: mask_name
-- =============================================================================
-- PURPOSE:     Partial name masking preserving first initial for context
-- COMPLIANCE:  HIPAA (Safe Harbor), GDPR (pseudonymization)
-- INPUT:       'John'
-- OUTPUT:      'J***'
-- USE CASES:   Patient lists, customer directories, HR reports
-- NOTES:       Preserves first character for sorting/grouping while hiding full name
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_name(name STRING)
RETURNS STRING
COMMENT 'Partial name masking. Input: John → Output: J***. Preserves first initial.'
RETURN CASE 
  WHEN name IS NULL OR name = '' THEN name
  WHEN LENGTH(name) = 1 THEN '*'
  ELSE CONCAT(LEFT(name, 1), REPEAT('*', LENGTH(name) - 1))
END;

-- =============================================================================
-- FUNCTION 8: mask_name_hash
-- =============================================================================
-- PURPOSE:     Complete anonymization via SHA-256 hash (one-way transformation)
-- COMPLIANCE:  GDPR Article 4(5) (pseudonymization), HIPAA Expert Determination
-- INPUT:       'John Smith'
-- OUTPUT:      'NAME_a8f5f167' (consistent hash for same input)
-- USE CASES:   Research data, analytics, data sharing with third parties
-- NOTES:       Deterministic - same input always produces same output (enables joins)
--              One-way - cannot reverse hash to get original name
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_name_hash(name STRING)
RETURNS STRING
COMMENT 'Hash name for complete anonymization. Input: John Smith → Output: NAME_a8f5f167. Deterministic and one-way.'
RETURN CASE 
  WHEN name IS NULL THEN NULL
  ELSE CONCAT('NAME_', SUBSTRING(SHA2(name, 256), 1, 8))
END;

-- =============================================================================
-- FUNCTION 9: mask_address
-- =============================================================================
-- PURPOSE:     Hide street address while preserving geographic context
-- COMPLIANCE:  HIPAA (geographic data), GDPR, CCPA
-- INPUT:       mask_address('123 Main St', 'New York', 'NY')
-- OUTPUT:      '*****, New York, NY'
-- USE CASES:   Shipping logs, customer analytics, location-based reports
-- NOTES:       Preserves city/state for geographic analysis while hiding street
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_address(address STRING, city STRING, state STRING)
RETURNS STRING
COMMENT 'Mask street address, show city/state. Input: (123 Main St, NYC, NY) → Output: *****, NYC, NY'
RETURN CASE
  WHEN city IS NULL AND state IS NULL THEN '*****, ***'
  WHEN state IS NULL THEN CONCAT('*****, ', city)
  WHEN city IS NULL THEN CONCAT('*****, ', state)
  ELSE CONCAT('*****, ', city, ', ', state)
END;

-- =============================================================================
-- FUNCTION 10: mask_dob
-- =============================================================================
-- PURPOSE:     Mask date of birth showing only birth year
-- COMPLIANCE:  HIPAA Safe Harbor (year allowed if age > 89), GDPR, COPPA
-- INPUT:       DATE '1985-03-15'
-- OUTPUT:      '****-**-** (1985)'
-- USE CASES:   Patient records, age verification, demographic analysis
-- NOTES:       Year preserved for age-based analytics; month/day hidden
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_dob(dob DATE)
RETURNS DATE
COMMENT 'Mask DOB showing year only. Input: 1985-03-15 → Output: 1985-01-01. HIPAA Safe Harbor compliant. Returns DATE type for ABAC compatibility.'
RETURN CASE
  WHEN dob IS NULL THEN NULL
  ELSE MAKE_DATE(YEAR(dob), 1, 1)
END;

-- =============================================================================
-- FUNCTION 11: mask_dob_age_range
-- =============================================================================
-- PURPOSE:     Convert DOB to age bucket (complete generalization)
-- COMPLIANCE:  HIPAA Expert Determination, GDPR, marketing regulations
-- INPUT:       DATE '1985-03-15' (for someone ~39 years old)
-- OUTPUT:      '35-44'
-- USE CASES:   Marketing segmentation, actuarial analysis, demographics
-- NOTES:       Standard marketing age buckets; completely hides exact age
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_dob_age_range(dob DATE)
RETURNS STRING
COMMENT 'Convert DOB to age range. Input: 1985-03-15 → Output: 35-44. Standard marketing buckets.'
RETURN CASE
  WHEN dob IS NULL THEN 'Unknown'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 18 THEN 'Under 18'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 25 THEN '18-24'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 35 THEN '25-34'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 45 THEN '35-44'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 55 THEN '45-54'
  WHEN DATEDIFF(CURRENT_DATE(), dob) / 365 < 65 THEN '55-64'
  ELSE '65+'
END;

-- =============================================================================
-- FUNCTION 12: mask_ip_address
-- =============================================================================
-- PURPOSE:     Mask IP address to subnet level (/16 equivalent)
-- COMPLIANCE:  GDPR (IP is PII in EU), CCPA, network security best practices
-- INPUT:       '192.168.1.100'
-- OUTPUT:      '192.168.*.*'
-- USE CASES:   Access logs, network analytics, security monitoring
-- NOTES:       Preserves first 2 octets for network identification; hides host
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING)
RETURNS STRING
COMMENT 'Mask IP to subnet level. Input: 192.168.1.100 → Output: 192.168.*.*. GDPR compliant.'
RETURN CASE
  WHEN ip IS NULL OR ip = '' THEN ip
  WHEN LOCATE('.', ip) = 0 THEN '***'
  ELSE CONCAT(SPLIT(ip, '\\\\.')[0], '.', SPLIT(ip, '\\\\.')[1], '.*.*')
END;

-- =============================================================================
-- FUNCTION 13: mask_amount_bucket
-- =============================================================================
-- PURPOSE:     Bucket financial amounts into ranges for privacy
-- COMPLIANCE:  Financial privacy regulations, internal data governance
-- INPUT:       5432.50
-- OUTPUT:      '$1K-$10K'
-- USE CASES:   Transaction reports, spending analysis, fraud detection tiers
-- NOTES:       Logarithmic buckets (10x each tier) balance privacy vs. utility
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_amount_bucket(amount DECIMAL(18,2))
RETURNS STRING
COMMENT 'Bucket amounts into ranges. Input: 5432.50 → Output: $1K-$10K. Logarithmic scale.'
RETURN CASE 
  WHEN amount IS NULL THEN 'Unknown' 
  WHEN amount < 0 THEN 'Negative'
  WHEN amount < 100 THEN '$0-$100'
  WHEN amount < 1000 THEN '$100-$1K'
  WHEN amount < 10000 THEN '$1K-$10K' 
  WHEN amount < 100000 THEN '$10K-$100K' 
  WHEN amount < 1000000 THEN '$100K-$1M'
  ELSE '$1M+'
END;

-- =============================================================================
-- FUNCTION 14: mask_salary_bucket
-- =============================================================================
-- PURPOSE:     Bucket salary into compensation ranges for HR privacy
-- COMPLIANCE:  Pay transparency laws, HR data governance, EEOC guidelines
-- INPUT:       95000.00
-- OUTPUT:      'Senior ($75K-$100K)'
-- USE CASES:   Compensation benchmarking, HR analytics, org planning
-- NOTES:       Named buckets (Entry, Junior, etc.) add business context
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_salary_bucket(salary DECIMAL(18,2))
RETURNS STRING
COMMENT 'Bucket salary into HR ranges. Input: 95000 → Output: Senior ($75K-$100K). Named career levels.'
RETURN CASE 
  WHEN salary IS NULL THEN 'Not Disclosed' 
  WHEN salary < 30000 THEN 'Entry (<$30K)'
  WHEN salary < 50000 THEN 'Junior ($30K-$50K)'
  WHEN salary < 75000 THEN 'Mid ($50K-$75K)'
  WHEN salary < 100000 THEN 'Senior ($75K-$100K)'
  WHEN salary < 150000 THEN 'Lead ($100K-$150K)'
  WHEN salary < 250000 THEN 'Principal ($150K-$250K)'
  ELSE 'Executive ($250K+)'
END;

-- =============================================================================
-- FUNCTION 15: mask_string_hash
-- =============================================================================
-- PURPOSE:     Complete anonymization via SHA-256 (irreversible)
-- COMPLIANCE:  GDPR (pseudonymization), research data de-identification
-- INPUT:       'Any sensitive string'
-- OUTPUT:      '9f86d081884c7d659a2feaa0c55ad015a3...' (64 char hex)
-- USE CASES:   Data sharing, research datasets, analytics
-- NOTES:       Full 256-bit hash; cannot be reversed; deterministic
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_string_hash(input STRING)
RETURNS STRING
COMMENT 'Complete SHA-256 anonymization. Input: any string → Output: 64-char hash. Irreversible.'
RETURN CASE
  WHEN input IS NULL THEN NULL
  ELSE SHA2(input, 256)
END;

-- =============================================================================
-- FUNCTION 16: mask_string_partial
-- =============================================================================
-- PURPOSE:     Generic partial masking preserving first and last characters
-- COMPLIANCE:  Various; provides context while hiding content
-- INPUT:       'SecretValue'
-- OUTPUT:      'S*********e'
-- USE CASES:   Generic sensitive fields, license keys, codes
-- NOTES:       Adaptive to string length; shows structure without content
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_string_partial(input STRING)
RETURNS STRING
COMMENT 'Partial masking. Input: SecretValue → Output: S*********e. First/last chars visible.'
RETURN CASE 
  WHEN input IS NULL OR input = '' THEN input
  WHEN LENGTH(input) <= 2 THEN REPEAT('*', LENGTH(input))
  WHEN LENGTH(input) = 3 THEN CONCAT(LEFT(input, 1), '*', RIGHT(input, 1))
  ELSE CONCAT(LEFT(input, 1), REPEAT('*', LENGTH(input) - 2), RIGHT(input, 1))
END;

-- =============================================================================
-- FUNCTION 17: mask_id_deterministic
-- =============================================================================
-- PURPOSE:     Pseudonymize IDs while preserving JOIN capability
-- COMPLIANCE:  GDPR pseudonymization, analytics data governance
-- INPUT:       'CUST-12345'
-- OUTPUT:      'ID_a8f5f167f44f' (consistent for same input)
-- USE CASES:   Cross-table analytics, de-identified datasets, data sharing
-- NOTES:       Same input ALWAYS produces same output (enables JOINs)
--              12-char hash prefix balances uniqueness vs. readability
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_id_deterministic(id STRING)
RETURNS STRING
COMMENT 'Deterministic ID masking for JOINs. Input: CUST-12345 → Output: ID_a8f5f167f44f. Consistent.'
RETURN CASE
  WHEN id IS NULL THEN NULL
  ELSE CONCAT('ID_', SUBSTRING(SHA2(id, 256), 1, 12))
END;

-- =============================================================================
-- FUNCTION 18: mask_timestamp_round
-- =============================================================================
-- PURPOSE:     Round timestamps to 15-minute intervals for temporal privacy
-- COMPLIANCE:  GDPR (behavioral data), analytics governance
-- INPUT:       '2024-01-15 10:23:45'
-- OUTPUT:      '2024-01-15 10:15:00'
-- USE CASES:   Access logs, activity tracking, time-series analytics
-- NOTES:       15-min granularity balances privacy vs. analytical utility
--              Adjust modulo value for different intervals (900=15min, 3600=1hr)
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_timestamp_round(ts TIMESTAMP)
RETURNS TIMESTAMP
COMMENT 'Round to 15-min intervals. Input: 10:23:45 → Output: 10:15:00. Privacy for time data.'
RETURN TO_TIMESTAMP(UNIX_TIMESTAMP(ts) - (UNIX_TIMESTAMP(ts) % 900));

-- =============================================================================
-- FUNCTION 19: mask_gps_precision
-- =============================================================================
-- PURPOSE:     Reduce GPS coordinate precision (~1km accuracy)
-- COMPLIANCE:  GDPR location data, CCPA, employee monitoring laws
-- INPUT:       40.7128 (latitude)
-- OUTPUT:      40.71 (~1.1km precision)
-- USE CASES:   Fleet tracking, delivery logistics, location analytics
-- NOTES:       2 decimal places ≈ 1.1km precision
--              Adjust precision: 1 dec = 11km, 3 dec = 110m, 4 dec = 11m
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_gps_precision(coordinate DOUBLE)
RETURNS DOUBLE
COMMENT 'Reduce GPS to ~1km precision. Input: 40.7128 → Output: 40.71. Location privacy.'
RETURN ROUND(coordinate, 2);

-- =============================================================================
-- FUNCTION 20: mask_serial_last4
-- =============================================================================
-- PURPOSE:     Mask serial numbers showing only last 4 characters
-- COMPLIANCE:  Asset tracking privacy, supply chain security
-- INPUT:       'SN-APPLE-001234'
-- OUTPUT:      'XXXXXXXXXXX1234'
-- USE CASES:   Inventory management, warranty tracking, asset reports
-- NOTES:       Last 4 often sufficient for identification in known contexts
-- =============================================================================
CREATE OR REPLACE FUNCTION mask_serial_last4(serial STRING)
RETURNS STRING
COMMENT 'Mask serial showing last 4. Input: SN-APPLE-001234 → Output: XXXXXXXXXXX1234'
RETURN CASE 
  WHEN serial IS NULL OR serial = '' THEN serial
  WHEN LENGTH(serial) <= 4 THEN REPEAT('X', LENGTH(serial))
  ELSE CONCAT(REPEAT('X', LENGTH(serial) - 4), RIGHT(serial, 4))
END;

-- #############################################################################
-- #                                                                           #
-- #                       ROW FILTER FUNCTIONS (8)                            #
-- #                                                                           #
-- # These functions control which ROWS users can see based on conditions.     #
-- # Unlike column masks (which hide values), row filters hide entire records. #
-- #                                                                           #
-- # USAGE: Apply to tables via ABAC policies with WHEN hasTagValue(...)       #
-- #                                                                           #
-- #############################################################################

-- =============================================================================
-- FUNCTION 21: filter_business_hours
-- =============================================================================
-- PURPOSE:     Restrict data access to standard business hours only
-- COMPLIANCE:  Data governance, insider threat mitigation, audit requirements
-- RETURNS:     TRUE if current time is 9 AM - 5 PM UTC, FALSE otherwise
-- USE CASES:   Sensitive data, production systems, regulated data
-- NOTES:       UTC timezone; adjust HOUR offset for local time zones
--              Tag tables with access_restriction='Business_Hours' to apply
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_business_hours()
RETURNS BOOLEAN
COMMENT 'Allow access 9AM-5PM UTC only. Returns TRUE during business hours. Tag: access_restriction=Business_Hours'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

-- =============================================================================
-- FUNCTION 22: filter_extended_hours
-- =============================================================================
-- PURPOSE:     Allow access during extended working hours
-- COMPLIANCE:  Shift-based access control, global team support
-- RETURNS:     TRUE if current time is 7 AM - 9 PM UTC, FALSE otherwise
-- USE CASES:   Support teams, global operations, shift workers
-- NOTES:       14-hour window accommodates multiple time zones
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_extended_hours()
RETURNS BOOLEAN
COMMENT 'Allow access 7AM-9PM UTC. Returns TRUE during extended hours. Tag: access_restriction=Extended_Hours'
RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 7 AND 21;

-- =============================================================================
-- FUNCTION 23: filter_maintenance_window
-- =============================================================================
-- PURPOSE:     Allow access only during off-hours maintenance window
-- COMPLIANCE:  Change management, production data protection
-- RETURNS:     TRUE if current time is 10 PM - 6 AM UTC, FALSE otherwise
-- USE CASES:   Production data, system tables, maintenance-only access
-- NOTES:       8-hour overnight window for maintenance operations
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_maintenance_window()
RETURNS BOOLEAN
COMMENT 'Allow access 10PM-6AM UTC (maintenance). Tag: access_restriction=Maintenance_Window'
RETURN HOUR(CURRENT_TIMESTAMP()) >= 22 OR HOUR(CURRENT_TIMESTAMP()) < 6;

-- =============================================================================
-- FUNCTION 24: filter_high_value
-- =============================================================================
-- PURPOSE:     Filter to show only high-value records (threshold-based)
-- COMPLIANCE:  Financial controls, fraud monitoring, escalation policies
-- INPUT:       Transaction/order amount
-- RETURNS:     TRUE if amount > $10,000, FALSE otherwise
-- USE CASES:   Fraud review queues, executive dashboards, audit samples
-- NOTES:       Adjust threshold (10000) as needed for your business
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_high_value(amount DECIMAL(18,2))
RETURNS BOOLEAN
COMMENT 'Filter for high-value (>$10K). Use: WHERE filter_high_value(amount)'
RETURN amount > 10000;

-- =============================================================================
-- FUNCTION 25: filter_flagged_only
-- =============================================================================
-- PURPOSE:     Show only records that have been flagged for review
-- COMPLIANCE:  Quality control, fraud investigation, exception handling
-- INPUT:       Boolean flag column
-- RETURNS:     TRUE if flag is TRUE, FALSE otherwise
-- USE CASES:   Fraud queues, QA review, exception reports
-- NOTES:       Combine with role-based access for investigation teams
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_flagged_only(flag BOOLEAN)
RETURNS BOOLEAN
COMMENT 'Show only flagged records. Use: WHERE filter_flagged_only(fraud_flag)'
RETURN flag = TRUE;

-- =============================================================================
-- FUNCTION 26: filter_active_only
-- =============================================================================
-- PURPOSE:     Show only records with 'Active' status
-- COMPLIANCE:  Data quality, operational focus, GDPR (data minimization)
-- INPUT:       Status column (string)
-- RETURNS:     TRUE if status = 'ACTIVE' (case-insensitive), FALSE otherwise
-- USE CASES:   Customer lists, employee directories, inventory views
-- NOTES:       Case-insensitive comparison; excludes archived/deleted records
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_active_only(status STRING)
RETURNS BOOLEAN
COMMENT 'Show only Active records. Use: WHERE filter_active_only(status)'
RETURN UPPER(status) = 'ACTIVE';

-- =============================================================================
-- FUNCTION 27: filter_deny_all
-- =============================================================================
-- PURPOSE:     Deny all access (emergency lockdown or explicit block)
-- COMPLIANCE:  Incident response, data quarantine, legal hold
-- RETURNS:     Always FALSE (no rows visible)
-- USE CASES:   Security incidents, data breach response, legal holds
-- NOTES:       Use sparingly - blocks ALL access to tagged data
--              Tag tables with access_restriction='Deny_All' for lockdown
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_deny_all()
RETURNS BOOLEAN
COMMENT 'DENY ALL access - returns FALSE always. Emergency lockdown function.'
RETURN FALSE;

-- =============================================================================
-- FUNCTION 28: filter_allow_all
-- =============================================================================
-- PURPOSE:     Allow all access (explicit permit, testing, override)
-- COMPLIANCE:  Testing environments, admin override, public data
-- RETURNS:     Always TRUE (all rows visible)
-- USE CASES:   Dev/test environments, public datasets, admin views
-- NOTES:       Essentially a no-op filter; use for explicit documentation
--              that a table has no row-level restrictions
-- =============================================================================
CREATE OR REPLACE FUNCTION filter_allow_all()
RETURNS BOOLEAN
COMMENT 'ALLOW ALL access - returns TRUE always. Use for explicitly unrestricted data.'
RETURN TRUE;
"""

# =============================================================================
# STEP 2: TAG POLICY DEFINITIONS
# =============================================================================
# 8 Generic Tag Policies (no industry suffix - works for ANY industry)
#
# TAG POLICIES vs TAGS:
# ---------------------
# - Tag POLICY: Account-level definition of allowed tag keys and values
# - Tag: Actual metadata applied to columns/tables using policy-defined keys
#
# HOW ABAC USES TAGS:
# -------------------
# 1. You define tag policies here (Step 2)
# 2. You apply tags to your columns: ALTER TABLE t ALTER COLUMN c SET TAGS ('pii_type'='ssn')
# 3. ABAC policies (Step 3) reference tags: MATCH COLUMNS hasTagValue('pii_type','ssn')
# 4. When a user queries, the policy checks tags and applies masking automatically
#
# NAMING CONVENTION:
# ------------------
# - Generic names (no suffix): pii_type, data_classification, etc.
# - Industry-specific templates use: pii_type_finance, pii_type_healthcare, etc.
# - Default template uses GENERIC names for maximum reusability
#
# =============================================================================

TAG_DEFINITIONS = [
    # =========================================================================
    # TAG 1: pii_type
    # =========================================================================
    # PURPOSE:     Identify the TYPE of personally identifiable information
    # USE CASE:    Tag columns to automatically apply appropriate masking
    # EXAMPLE:     ALTER TABLE users ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn')
    # ABAC USAGE:  MATCH COLUMNS hasTagValue('pii_type', 'ssn') AS ssn_col
    # VALUES:      19 PII types covering identity, financial, medical, technical
    # =========================================================================
    ("pii_type", "Type of personally identifiable information - drives automatic column masking", [
        # Identity PII
        "ssn",              # Social Security Number (US)
        "person_name",      # Full name or partial name (avoids SQL keyword 'name')
        "email",            # Email address
        "phone",            # Phone number
        "address",          # Physical address
        "dob",              # Date of birth
        "age",              # Exact age
        # Financial PII
        "credit_card",      # Credit/debit card number (PCI-DSS)
        "account_number",   # Bank account number
        "routing_number",   # Bank routing number
        "financial_record", # General financial data
        # Technical PII
        "ip_address",       # IP address (PII in GDPR)
        "device_id",        # Device identifier, MAC address
        "biometric",        # Fingerprint, face ID, voice print
        # Government ID
        "license_number",   # Driver's license
        "passport",         # Passport number
        "national_id",      # National ID (SSN in other countries)
        # Medical PII
        "medical_record",   # Medical record number (HIPAA)
        "genetic_data"      # Genetic/genomic data (GINA)
    ]),
    
    # =========================================================================
    # TAG 2: data_classification
    # =========================================================================
    # PURPOSE:     Security classification level for access control
    # USE CASE:    Restrict access based on clearance level
    # EXAMPLE:     ALTER TABLE secrets ALTER COLUMN data SET TAGS ('data_classification' = 'Restricted')
    # VALUES:      5 levels from Public to Top_Secret
    # =========================================================================
    ("data_classification", "Security classification level - Public to Top_Secret", [
        "Public",       # No restrictions, can be shared externally
        "Internal",     # Internal use only, not for external sharing
        "Confidential", # Limited distribution, need-to-know basis
        "Restricted",   # Highly restricted, specific authorization required
        "Top_Secret"    # Maximum protection, minimal access
    ]),
    
    # =========================================================================
    # TAG 3: compliance_requirement
    # =========================================================================
    # PURPOSE:     Regulatory compliance framework applicable to data
    # USE CASE:    Enforce compliance-specific handling and audit
    # EXAMPLE:     ALTER TABLE payments ALTER COLUMN card SET TAGS ('compliance_requirement' = 'PCI_DSS')
    # VALUES:      10 major compliance frameworks
    # =========================================================================
    ("compliance_requirement", "Regulatory compliance framework - PCI, HIPAA, GDPR, etc.", [
        "PCI_DSS",  # Payment Card Industry Data Security Standard
        "HIPAA",    # Health Insurance Portability and Accountability Act
        "GDPR",     # General Data Protection Regulation (EU)
        "CCPA",     # California Consumer Privacy Act
        "SOX",      # Sarbanes-Oxley Act (financial reporting)
        "GLBA",     # Gramm-Leach-Bliley Act (financial privacy)
        "FERPA",    # Family Educational Rights and Privacy Act
        "COPPA",    # Children's Online Privacy Protection Act
        "ITAR",     # International Traffic in Arms Regulations
        "None"      # No specific compliance requirement
    ]),
    
    # =========================================================================
    # TAG 4: sensitivity_level
    # =========================================================================
    # PURPOSE:     Business sensitivity for risk-based access decisions
    # USE CASE:    Apply stricter controls to higher sensitivity data
    # EXAMPLE:     ALTER TABLE salaries ALTER COLUMN amount SET TAGS ('sensitivity_level' = 'High')
    # VALUES:      4 levels (Low, Medium, High, Critical)
    # =========================================================================
    ("sensitivity_level", "Business sensitivity level - Low to Critical", [
        "Low",      # Minimal business impact if exposed
        "Medium",   # Moderate business impact
        "High",     # Significant business impact, needs protection
        "Critical"  # Severe impact, maximum protection required
    ]),
    
    # =========================================================================
    # TAG 5: data_purpose
    # =========================================================================
    # PURPOSE:     Intended purpose/department for data access
    # USE CASE:    Purpose-based access control, audit logging
    # EXAMPLE:     ALTER TABLE employees ALTER COLUMN salary SET TAGS ('data_purpose' = 'HR')
    # VALUES:      10 common business purposes
    # =========================================================================
    ("data_purpose", "Intended purpose for data access - Operations, Analytics, HR, etc.", [
        "Operations",   # Day-to-day business operations
        "Analytics",    # Business intelligence, data science
        "Reporting",    # Management/executive reporting
        "Audit",        # Internal/external audit activities
        "Marketing",    # Marketing campaigns, customer outreach
        "Research",     # R&D, product development
        "Support",      # Customer support, help desk
        "Compliance",   # Regulatory compliance activities
        "Legal",        # Legal hold, litigation support
        "HR"            # Human resources, employee data
    ]),
    
    # =========================================================================
    # TAG 6: access_restriction
    # =========================================================================
    # PURPOSE:     Time-based or condition-based access restrictions
    # USE CASE:    Apply row filters based on restriction type
    # EXAMPLE:     ALTER TABLE production_data SET TAGS ('access_restriction' = 'Business_Hours')
    # VALUES:      7 restriction types (maps to filter functions)
    # =========================================================================
    ("access_restriction", "Access restriction type - triggers row filter policies", [
        "Business_Hours",      # 9AM-5PM UTC only (filter_business_hours)
        "Extended_Hours",      # 7AM-9PM UTC (filter_extended_hours)
        "Maintenance_Window",  # 10PM-6AM UTC (filter_maintenance_window)
        "Region_Locked",       # Geographic restriction
        "Flagged_Only",        # Show only flagged records
        "Active_Only",         # Show only active records
        "None"                 # No time/condition restrictions
    ]),
    
    # =========================================================================
    # TAG 7: retention_policy
    # =========================================================================
    # PURPOSE:     Data retention period for lifecycle management
    # USE CASE:    Automate data deletion, archive, or legal hold
    # EXAMPLE:     ALTER TABLE logs SET TAGS ('retention_policy' = '90_Days')
    # VALUES:      7 retention periods
    # =========================================================================
    ("retention_policy", "Data retention period - for lifecycle management", [
        "30_Days",          # Short-term, operational data
        "90_Days",          # Quarterly retention
        "1_Year",           # Annual retention
        "3_Years",          # Medium-term compliance
        "7_Years",          # Long-term compliance (SOX, tax records)
        "Indefinite",       # No automatic deletion
        "Delete_Immediately" # Data marked for immediate removal
    ]),
    
    # =========================================================================
    # TAG 8: geographic_scope
    # =========================================================================
    # PURPOSE:     Geographic scope for data residency/sovereignty
    # USE CASE:    Enforce data localization requirements (GDPR, etc.)
    # EXAMPLE:     ALTER TABLE eu_customers SET TAGS ('geographic_scope' = 'Region_Only')
    # VALUES:      4 geographic scopes
    # =========================================================================
    ("geographic_scope", "Geographic scope for data residency and sovereignty", [
        "Country_Only",          # Data must stay in originating country
        "Region_Only",           # Data limited to region (EU, APAC, etc.)
        "Cross_Border_Approved", # Approved for cross-border transfer
        "Global"                 # No geographic restrictions
    ])
]

# =============================================================================
# STEP 3: ABAC POLICY DEFINITIONS
# =============================================================================
# 15 Catalog-Level ABAC Policies (12 column masks + 3 row filters)
#
# WHAT ARE ABAC POLICIES?
# -----------------------
# ABAC (Attribute-Based Access Control) policies automatically apply data
# protection based on TAGS attached to columns or tables.
#
# HOW IT WORKS:
# -------------
# 1. Tag your column: ALTER TABLE t ALTER COLUMN c SET TAGS ('pii_type'='ssn')
# 2. Policy matches: MATCH COLUMNS hasTagValue('pii_type', 'ssn')
# 3. Mask applies: User sees 'XXX-XX-1234' instead of '123-45-6789'
#
# POLICY SCOPE:
# -------------
# - These policies are at CATALOG level (apply to ALL schemas in catalog)
# - For schema-level policies, change "ON CATALOG {CATALOG}" to
#   "ON SCHEMA {CATALOG}.{SCHEMA}"
#
# TARGET GROUP:
# -------------
# - All policies target `account users` (all regular workspace users)
# - Catalog owners and admins see unmasked data (they're not in `account users`)
# - To exclude specific groups, use "FOR EXCEPT ('group_name')" instead
#
# POLICY NAMING:
# --------------
# - Column masks: mask_<pii_type>_policy
# - Row filters: filter_<condition>_policy
#
# =============================================================================

ABAC_POLICIES_SQL = """
-- #############################################################################
-- #                                                                           #
-- #                     COLUMN MASK POLICIES (12)                             #
-- #                                                                           #
-- # These policies automatically mask column values based on pii_type tags.   #
-- # Users in `account users` group see masked data.                           #
-- # Catalog/schema owners see unmasked data.                                  #
-- #                                                                           #
-- #############################################################################

-- =============================================================================
-- POLICY 1: mask_ssn_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'ssn'
-- MASK:        mask_ssn() → 'XXX-XX-1234'
-- COMPLIANCE:  HIPAA, GLBA, CCPA
-- EXAMPLE:     ALTER TABLE customers ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn');
-- =============================================================================
CREATE OR REPLACE POLICY mask_ssn_policy ON CATALOG {CATALOG}
COMMENT 'Auto-mask SSN columns (pii_type=ssn). Shows last 4 digits. HIPAA/GLBA compliant.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ssn
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'ssn') AS ssn_col
ON COLUMN ssn_col;

-- =============================================================================
-- POLICY 2: mask_email_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'email'
-- MASK:        mask_email() → '****@domain.com'
-- COMPLIANCE:  GDPR, CCPA
-- EXAMPLE:     ALTER TABLE users ALTER COLUMN email SET TAGS ('pii_type' = 'email');
-- =============================================================================
CREATE OR REPLACE POLICY mask_email_policy ON CATALOG {CATALOG}
COMMENT 'Auto-mask email columns (pii_type=email). Preserves domain. GDPR compliant.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_email 
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'email') AS email_col
ON COLUMN email_col;

-- =============================================================================
-- POLICY 3: mask_phone_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'phone'
-- MASK:        mask_phone() → 'XXX-XXX-1234'
-- COMPLIANCE:  TCPA, GDPR, CCPA
-- EXAMPLE:     ALTER TABLE contacts ALTER COLUMN phone SET TAGS ('pii_type' = 'phone');
-- =============================================================================
CREATE OR REPLACE POLICY mask_phone_policy ON CATALOG {CATALOG}
COMMENT 'Auto-mask phone columns (pii_type=phone). Shows last 4 digits. TCPA compliant.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_phone 
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'phone') AS phone_col
ON COLUMN phone_col;

-- =============================================================================
-- POLICY 4: mask_name_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'person_name'
-- MASK:        mask_name() → 'J***'
-- COMPLIANCE:  HIPAA Safe Harbor, GDPR pseudonymization
-- EXAMPLE:     ALTER TABLE patients ALTER COLUMN first_name SET TAGS ('pii_type' = 'person_name');
-- =============================================================================
CREATE OR REPLACE POLICY mask_name_policy ON CATALOG {CATALOG}
COMMENT 'Auto-mask name columns (pii_type=person_name). Shows first initial only.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_name
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'person_name') AS name_col
ON COLUMN name_col;

-- =============================================================================
-- POLICY 5: mask_credit_card_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'credit_card'
-- MASK:        mask_credit_card() → '****-****-****-1234'
-- COMPLIANCE:  PCI-DSS Requirement 3.4 (render PAN unreadable)
-- EXAMPLE:     ALTER TABLE payments ALTER COLUMN card_number SET TAGS ('pii_type' = 'credit_card');
-- NOTES:       This is a REQUIRED control for PCI-DSS compliance
-- =============================================================================
CREATE OR REPLACE POLICY mask_credit_card_policy ON CATALOG {CATALOG}
COMMENT 'PCI-DSS compliant credit card masking (pii_type=credit_card). Last 4 only.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_credit_card 
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'credit_card') AS card_col
ON COLUMN card_col;

-- =============================================================================
-- POLICY 6: mask_account_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'account_number'
-- MASK:        mask_account_number() → '******1234'
-- COMPLIANCE:  GLBA, SOX
-- EXAMPLE:     ALTER TABLE accounts ALTER COLUMN account_num SET TAGS ('pii_type' = 'account_number');
-- =============================================================================
CREATE OR REPLACE POLICY mask_account_policy ON CATALOG {CATALOG}
COMMENT 'Mask bank account numbers (pii_type=account_number). Last 4 visible.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_account_number
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'account_number') AS account_col
ON COLUMN account_col;

-- =============================================================================
-- POLICY 7: mask_ip_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'ip_address'
-- MASK:        mask_ip_address() → '192.168.*.*'
-- COMPLIANCE:  GDPR (IP is PII in EU), CCPA
-- EXAMPLE:     ALTER TABLE logs ALTER COLUMN client_ip SET TAGS ('pii_type' = 'ip_address');
-- =============================================================================
CREATE OR REPLACE POLICY mask_ip_policy ON CATALOG {CATALOG}
COMMENT 'Mask IP addresses to subnet level (pii_type=ip_address). GDPR compliant.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_ip_address
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'ip_address') AS ip_col
ON COLUMN ip_col;

-- =============================================================================
-- POLICY 8: mask_dob_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'dob'
-- MASK:        mask_dob() → '****-**-** (1985)'
-- COMPLIANCE:  HIPAA Safe Harbor (year allowed if age > 89), COPPA
-- EXAMPLE:     ALTER TABLE patients ALTER COLUMN date_of_birth SET TAGS ('pii_type' = 'dob');
-- =============================================================================
CREATE OR REPLACE POLICY mask_dob_policy ON CATALOG {CATALOG}
COMMENT 'Mask DOB showing year only (pii_type=dob). HIPAA Safe Harbor compliant.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_dob
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'dob') AS dob_col
ON COLUMN dob_col;

-- =============================================================================
-- POLICY 9: mask_amount_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'financial_record'
-- MASK:        mask_amount_bucket() → '$1K-$10K'
-- COMPLIANCE:  Financial privacy, data governance
-- EXAMPLE:     ALTER TABLE transactions ALTER COLUMN amount SET TAGS ('pii_type' = 'financial_record');
-- =============================================================================
CREATE OR REPLACE POLICY mask_amount_policy ON CATALOG {CATALOG}
COMMENT 'Bucket financial amounts into ranges (pii_type=financial_record).'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_amount_bucket
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'financial_record') AS amount_col
ON COLUMN amount_col;

-- =============================================================================
-- POLICY 10: mask_salary_policy
-- =============================================================================
-- TRIGGER:     Column tagged with data_purpose = 'HR' AND sensitivity_level = 'High'
-- MASK:        mask_salary_bucket() → 'Senior ($75K-$100K)'
-- COMPLIANCE:  Pay transparency laws, HR data governance
-- EXAMPLE:     ALTER TABLE employees ALTER COLUMN salary SET TAGS ('sensitivity_level'='High', 'data_purpose'='HR');
-- NOTES:       Uses combined tags for more precise targeting
-- =============================================================================
CREATE OR REPLACE POLICY mask_salary_policy ON CATALOG {CATALOG}
COMMENT 'Bucket salary into ranges for HR privacy (sensitivity_level=High + data_purpose=HR).'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_salary_bucket
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('data_purpose', 'HR') AND hasTagValue('sensitivity_level', 'High') AS salary_col
ON COLUMN salary_col;

-- =============================================================================
-- POLICY 11: mask_device_id_policy
-- =============================================================================
-- TRIGGER:     Column tagged with pii_type = 'device_id'
-- MASK:        mask_serial_last4() → 'XXXXXXXX1234'
-- COMPLIANCE:  Asset tracking, supply chain security
-- EXAMPLE:     ALTER TABLE assets ALTER COLUMN serial_number SET TAGS ('pii_type' = 'device_id');
-- =============================================================================
CREATE OR REPLACE POLICY mask_device_id_policy ON CATALOG {CATALOG}
COMMENT 'Mask device IDs/serial numbers (pii_type=device_id). Last 4 visible.'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_serial_last4
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('pii_type', 'device_id') AS device_col
ON COLUMN device_col;

-- =============================================================================
-- POLICY 12: mask_timestamp_policy
-- =============================================================================
-- TRIGGER:     Column tagged with sensitivity_level = 'High' AND data_purpose = 'Audit'
-- MASK:        mask_timestamp_round() → rounds to 15-minute intervals
-- COMPLIANCE:  Privacy for high-sensitivity audit data
-- EXAMPLE:     ALTER TABLE audit_log ALTER COLUMN event_time SET TAGS ('sensitivity_level'='High', 'data_purpose'='Audit');
-- NOTES:       Useful for preventing timing-based user behavior analysis
-- =============================================================================
CREATE OR REPLACE POLICY mask_timestamp_policy ON CATALOG {CATALOG}
COMMENT 'Round timestamps to 15-min intervals (sensitivity_level=High + data_purpose=Audit).'
COLUMN MASK {CATALOG}.{SCHEMA}.mask_timestamp_round
TO `account users`
FOR TABLES
MATCH COLUMNS hasTagValue('sensitivity_level', 'High') AND hasTagValue('data_purpose', 'Audit') AS ts_col
ON COLUMN ts_col;

-- #############################################################################
-- #                                                                           #
-- #                        ROW FILTER POLICIES (3)                            #
-- #                                                                           #
-- # These policies filter which ROWS users can see based on table-level tags. #
-- # Unlike column masks, row filters hide entire records.                     #
-- #                                                                           #
-- # HOW IT WORKS:                                                             #
-- # 1. Tag your TABLE: ALTER TABLE t SET TAGS ('access_restriction'='...')    #
-- # 2. Policy applies the filter function to all queries on that table        #
-- # 3. Only rows where filter returns TRUE are visible                        #
-- #                                                                           #
-- #############################################################################

-- =============================================================================
-- POLICY 13: filter_business_hours_policy
-- =============================================================================
-- TRIGGER:     Table tagged with access_restriction = 'Business_Hours'
-- FILTER:      filter_business_hours() → TRUE only 9AM-5PM UTC
-- COMPLIANCE:  Data governance, insider threat mitigation
-- EXAMPLE:     ALTER TABLE production_data SET TAGS ('access_restriction' = 'Business_Hours');
-- NOTES:       Users querying outside 9-5 UTC see zero rows
-- =============================================================================
CREATE OR REPLACE POLICY filter_business_hours_policy ON CATALOG {CATALOG}
COMMENT 'Restrict table access to 9AM-5PM UTC (access_restriction=Business_Hours).'
ROW FILTER {CATALOG}.{SCHEMA}.filter_business_hours
TO `account users`
FOR TABLES
WHEN hasTagValue('access_restriction', 'Business_Hours');

-- =============================================================================
-- POLICY 14: filter_extended_hours_policy
-- =============================================================================
-- TRIGGER:     Table tagged with access_restriction = 'Extended_Hours'
-- FILTER:      filter_extended_hours() → TRUE only 7AM-9PM UTC
-- COMPLIANCE:  Shift-based access, global team support
-- EXAMPLE:     ALTER TABLE support_data SET TAGS ('access_restriction' = 'Extended_Hours');
-- =============================================================================
CREATE OR REPLACE POLICY filter_extended_hours_policy ON CATALOG {CATALOG}
COMMENT 'Restrict table access to 7AM-9PM UTC (access_restriction=Extended_Hours).'
ROW FILTER {CATALOG}.{SCHEMA}.filter_extended_hours
TO `account users`
FOR TABLES
WHEN hasTagValue('access_restriction', 'Extended_Hours');

-- =============================================================================
-- POLICY 15: filter_maintenance_policy
-- =============================================================================
-- TRIGGER:     Table tagged with access_restriction = 'Maintenance_Window'
-- FILTER:      filter_maintenance_window() → TRUE only 10PM-6AM UTC
-- COMPLIANCE:  Change management, production data protection
-- EXAMPLE:     ALTER TABLE system_tables SET TAGS ('access_restriction' = 'Maintenance_Window');
-- NOTES:       Useful for tables that should only be modified during off-hours
-- =============================================================================
CREATE OR REPLACE POLICY filter_maintenance_policy ON CATALOG {CATALOG}
COMMENT 'Restrict table access to 10PM-6AM UTC maintenance window (access_restriction=Maintenance_Window).'
ROW FILTER {CATALOG}.{SCHEMA}.filter_maintenance_window
TO `account users`
FOR TABLES
WHEN hasTagValue('access_restriction', 'Maintenance_Window');
"""

# =============================================================================
# STEP 4: TEST TABLE CREATION
# =============================================================================
# 5 Comprehensive Test Tables with 46 total sample rows
#
# PURPOSE:
# --------
# These tables demonstrate ABAC in action. Each table contains columns
# that will be tagged in Step 5, then masked/filtered when queried.
#
# TABLE SUMMARY:
# --------------
# | Table              | Rows | Purpose                                    |
# |--------------------|------|--------------------------------------------|
# | users_test         | 8    | Customer PII (SSN, email, phone, DOB)      |
# | transactions_test  | 10   | Financial data (cards, amounts, IPs)       |
# | employees_test     | 10   | HR data (salary, SSN, performance)         |
# | assets_test        | 8    | Inventory (serial numbers, GPS, costs)     |
# | audit_log_test     | 10   | Access logs (timestamps, IPs, actions)     |
#
# NAMING CONVENTION:
# ------------------
# All test tables use `_test` suffix to keep them separate from production.
#
# AFTER STEP 5 (tagging):
# -----------------------
# When you query these tables as a regular user, you'll see:
# - SSN: 'XXX-XX-1234' (masked)
# - Email: '****@example.com' (masked)
# - Credit Card: '****-****-****-1234' (masked)
# - Salary: 'Senior ($75K-$100K)' (bucketed)
# etc.
#
# =============================================================================

TEST_TABLES_SQL = """
-- #############################################################################
-- #                                                                           #
-- #                     TEST TABLE 1: USERS                                   #
-- #                                                                           #
-- # Customer/User PII data demonstrating identity masking                     #
-- #                                                                           #
-- #############################################################################
-- =============================================================================
CREATE TABLE IF NOT EXISTS users_test (
  user_id STRING NOT NULL COMMENT 'Unique user identifier',
  first_name STRING NOT NULL COMMENT 'First name (PII)',
  last_name STRING NOT NULL COMMENT 'Last name (PII)',
  email STRING COMMENT 'Email address (PII)',
  phone STRING COMMENT 'Phone number (PII)',
  ssn STRING COMMENT 'Social Security Number (Sensitive PII)',
  date_of_birth DATE COMMENT 'Date of birth (PII)',
  street_address STRING COMMENT 'Street address (PII)',
  city STRING COMMENT 'City',
  state STRING COMMENT 'State/Province',
  zip_code STRING COMMENT 'Postal code',
  country STRING DEFAULT 'USA' COMMENT 'Country',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Record creation timestamp',
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'Last update timestamp',
  status STRING DEFAULT 'Active' COMMENT 'Account status',
  CONSTRAINT pk_users_test PRIMARY KEY (user_id)
) USING DELTA
COMMENT 'Test table: Customer/User PII data for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO users_test (user_id, first_name, last_name, email, phone, ssn, date_of_birth, street_address, city, state, zip_code) VALUES
('U-1001', 'John', 'Smith', 'john.smith@example.com', '555-123-4567', '123-45-6789', '1985-03-15', '123 Main Street', 'New York', 'NY', '10001'),
('U-1002', 'Sarah', 'Johnson', 'sarah.johnson@example.com', '555-234-5678', '234-56-7890', '1990-07-22', '456 Oak Avenue', 'Los Angeles', 'CA', '90001'),
('U-1003', 'Michael', 'Williams', 'mike.williams@example.com', '555-345-6789', '345-67-8901', '1982-11-30', '789 Pine Road', 'Chicago', 'IL', '60601'),
('U-1004', 'Emily', 'Brown', 'emily.brown@example.com', '555-456-7890', '456-78-9012', '1995-05-10', '321 Elm Street', 'Houston', 'TX', '77001'),
('U-1005', 'David', 'Jones', 'david.jones@example.com', '555-567-8901', '567-89-0123', '1978-09-05', '654 Maple Drive', 'Phoenix', 'AZ', '85001'),
('U-1006', 'Lisa', 'Garcia', 'lisa.garcia@example.com', '555-678-9012', '678-90-1234', '1988-12-18', '987 Cedar Lane', 'Philadelphia', 'PA', '19101'),
('U-1007', 'James', 'Miller', 'james.miller@example.com', '555-789-0123', '789-01-2345', '1992-04-25', '147 Birch Court', 'San Antonio', 'TX', '78201'),
('U-1008', 'Jennifer', 'Davis', 'jennifer.davis@example.com', '555-890-1234', '890-12-3456', '1987-08-08', '258 Spruce Way', 'San Diego', 'CA', '92101');

-- =============================================================================
-- TABLE 2: TRANSACTIONS - Financial transaction records
-- =============================================================================
CREATE TABLE IF NOT EXISTS transactions_test (
  transaction_id STRING NOT NULL COMMENT 'Unique transaction ID',
  user_id STRING NOT NULL COMMENT 'Foreign key to users',
  account_number STRING COMMENT 'Account number (PII)',
  card_number STRING COMMENT 'Credit card number (PCI)',
  transaction_type STRING COMMENT 'Type: Purchase, Refund, Transfer, etc.',
  amount DECIMAL(18,2) COMMENT 'Transaction amount',
  currency STRING DEFAULT 'USD' COMMENT 'Currency code',
  merchant_name STRING COMMENT 'Merchant/vendor name',
  merchant_category STRING COMMENT 'Merchant category code',
  ip_address STRING COMMENT 'Client IP address (PII)',
  device_id STRING COMMENT 'Device identifier',
  location_city STRING COMMENT 'Transaction city',
  location_country STRING COMMENT 'Transaction country',
  transaction_timestamp TIMESTAMP COMMENT 'Transaction date/time',
  fraud_flag BOOLEAN DEFAULT FALSE COMMENT 'Fraud indicator',
  status STRING DEFAULT 'Completed' COMMENT 'Transaction status',
  CONSTRAINT pk_transactions_test PRIMARY KEY (transaction_id)
) USING DELTA
COMMENT 'Test table: Financial transactions for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO transactions_test (transaction_id, user_id, account_number, card_number, transaction_type, amount, merchant_name, merchant_category, ip_address, device_id, location_city, location_country, transaction_timestamp, fraud_flag) VALUES
('TXN-10001', 'U-1001', '1234567890', '4532-1234-5678-9010', 'Purchase', 125.50, 'Amazon', 'Online Retail', '192.168.1.100', 'DEV-001-A', 'New York', 'USA', '2024-01-15 10:30:00', FALSE),
('TXN-10002', 'U-1001', '1234567890', '4532-1234-5678-9010', 'Purchase', 85.75, 'Whole Foods', 'Grocery', '192.168.1.101', 'DEV-001-A', 'New York', 'USA', '2024-01-15 14:22:00', FALSE),
('TXN-10003', 'U-1002', '2345678901', '5425-2345-6789-0123', 'Transfer', 5500.00, 'Wire Transfer', 'Banking', '10.0.1.50', 'DEV-002-B', 'Los Angeles', 'USA', '2024-01-16 09:15:00', FALSE),
('TXN-10004', 'U-1003', '3456789012', '3782-3456-7890-1234', 'Purchase', 15250.00, 'Best Buy', 'Electronics', '172.16.0.25', 'DEV-003-C', 'Chicago', 'USA', '2024-01-16 16:45:00', TRUE),
('TXN-10005', 'U-1001', '1234567890', '4532-1234-5678-9010', 'Refund', -250.00, 'Amazon', 'Online Retail', '192.168.1.102', 'DEV-001-A', 'New York', 'USA', '2024-01-17 11:00:00', FALSE),
('TXN-10006', 'U-1004', '4567890123', '4916-4567-8901-2345', 'Purchase', 2340.00, 'Delta Airlines', 'Travel', '192.168.2.50', 'DEV-004-D', 'Houston', 'USA', '2024-01-17 08:30:00', FALSE),
('TXN-10007', 'U-1005', '5678901234', '4024-5678-9012-3456', 'Purchase', 89.99, 'Netflix', 'Entertainment', '10.10.10.10', 'DEV-005-E', 'Phoenix', 'USA', '2024-01-18 19:00:00', FALSE),
('TXN-10008', 'U-1006', '6789012345', '5105-6789-0123-4567', 'Transfer', 25000.00, 'Investment Account', 'Financial', '192.168.3.75', 'DEV-006-F', 'Philadelphia', 'USA', '2024-01-18 10:00:00', FALSE),
('TXN-10009', 'U-1002', '2345678901', '5425-2345-6789-0123', 'Purchase', 450.00, 'Apple Store', 'Electronics', '10.0.1.51', 'DEV-002-B', 'Los Angeles', 'USA', '2024-01-19 13:30:00', FALSE),
('TXN-10010', 'U-1007', '7890123456', '4716-7890-1234-5678', 'Purchase', 67.50, 'Uber Eats', 'Food Delivery', '192.168.4.100', 'DEV-007-G', 'San Antonio', 'USA', '2024-01-19 20:15:00', FALSE);

-- =============================================================================
-- TABLE 3: EMPLOYEES - HR/Employee records
-- =============================================================================
CREATE TABLE IF NOT EXISTS employees_test (
  employee_id STRING NOT NULL COMMENT 'Unique employee ID',
  first_name STRING NOT NULL COMMENT 'First name (PII)',
  last_name STRING NOT NULL COMMENT 'Last name (PII)',
  email STRING COMMENT 'Work email (PII)',
  phone STRING COMMENT 'Phone number (PII)',
  ssn STRING COMMENT 'SSN (Sensitive PII)',
  date_of_birth DATE COMMENT 'DOB (PII)',
  hire_date DATE COMMENT 'Employment start date',
  department STRING COMMENT 'Department name',
  job_title STRING COMMENT 'Job title',
  manager_id STRING COMMENT 'Manager employee ID',
  salary DECIMAL(18,2) COMMENT 'Annual salary (Sensitive)',
  bonus DECIMAL(18,2) COMMENT 'Annual bonus (Sensitive)',
  office_location STRING COMMENT 'Office location',
  access_level STRING COMMENT 'Security clearance level',
  performance_rating STRING COMMENT 'Latest performance rating',
  status STRING DEFAULT 'Active' COMMENT 'Employment status',
  CONSTRAINT pk_employees_test PRIMARY KEY (employee_id)
) USING DELTA
COMMENT 'Test table: Employee/HR records for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO employees_test (employee_id, first_name, last_name, email, phone, ssn, date_of_birth, hire_date, department, job_title, manager_id, salary, bonus, office_location, access_level, performance_rating, status) VALUES
('EMP-001', 'Robert', 'Anderson', 'robert.anderson@company.com', '555-111-2222', '111-22-3333', '1980-06-15', '2015-03-01', 'Engineering', 'Senior Engineer', 'EMP-010', 125000.00, 15000.00, 'New York', 'L3', 'Exceeds', 'Active'),
('EMP-002', 'Maria', 'Martinez', 'maria.martinez@company.com', '555-222-3333', '222-33-4444', '1985-09-20', '2018-07-15', 'Engineering', 'Staff Engineer', 'EMP-001', 145000.00, 20000.00, 'New York', 'L3', 'Exceeds', 'Active'),
('EMP-003', 'William', 'Taylor', 'william.taylor@company.com', '555-333-4444', '333-44-5555', '1990-02-28', '2020-01-10', 'Engineering', 'Engineer', 'EMP-001', 95000.00, 8000.00, 'San Francisco', 'L2', 'Meets', 'Active'),
('EMP-004', 'Patricia', 'Thomas', 'patricia.thomas@company.com', '555-444-5555', '444-55-6666', '1975-11-05', '2010-05-20', 'Finance', 'Finance Director', 'EMP-010', 175000.00, 35000.00, 'Chicago', 'L4', 'Exceeds', 'Active'),
('EMP-005', 'Christopher', 'Jackson', 'chris.jackson@company.com', '555-555-6666', '555-66-7777', '1988-07-12', '2019-09-01', 'Marketing', 'Marketing Manager', 'EMP-010', 110000.00, 12000.00, 'Los Angeles', 'L2', 'Meets', 'Active'),
('EMP-006', 'Jessica', 'White', 'jessica.white@company.com', '555-666-7777', '666-77-8888', '1992-04-30', '2021-02-15', 'HR', 'HR Specialist', 'EMP-008', 75000.00, 5000.00, 'New York', 'L2', 'Meets', 'Active'),
('EMP-007', 'Daniel', 'Harris', 'daniel.harris@company.com', '555-777-8888', '777-88-9999', '1983-12-10', '2016-11-01', 'Legal', 'Legal Counsel', 'EMP-010', 165000.00, 25000.00, 'New York', 'L4', 'Exceeds', 'Active'),
('EMP-008', 'Nancy', 'Clark', 'nancy.clark@company.com', '555-888-9999', '888-99-0000', '1978-08-22', '2012-04-15', 'HR', 'HR Director', 'EMP-010', 155000.00, 22000.00, 'New York', 'L4', 'Exceeds', 'Active'),
('EMP-009', 'Matthew', 'Lewis', 'matthew.lewis@company.com', '555-999-0000', '999-00-1111', '1995-01-18', '2022-06-01', 'Engineering', 'Junior Engineer', 'EMP-003', 72000.00, 4000.00, 'San Francisco', 'L1', 'Meets', 'Active'),
('EMP-010', 'Elizabeth', 'Robinson', 'elizabeth.robinson@company.com', '555-000-1111', '000-11-2222', '1970-03-25', '2008-01-15', 'Executive', 'VP Operations', NULL, 250000.00, 75000.00, 'New York', 'L5', 'Exceeds', 'Active');

-- =============================================================================
-- TABLE 4: ASSETS - Inventory/Equipment tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS assets_test (
  asset_id STRING NOT NULL COMMENT 'Unique asset ID',
  asset_name STRING NOT NULL COMMENT 'Asset name/description',
  asset_type STRING COMMENT 'Type: Hardware, Software, Vehicle, etc.',
  serial_number STRING COMMENT 'Serial number (Sensitive)',
  manufacturer STRING COMMENT 'Manufacturer name',
  model STRING COMMENT 'Model number',
  purchase_date DATE COMMENT 'Acquisition date',
  purchase_cost DECIMAL(18,2) COMMENT 'Original cost (Sensitive)',
  current_value DECIMAL(18,2) COMMENT 'Depreciated value',
  location STRING COMMENT 'Physical location',
  assigned_to STRING COMMENT 'Employee ID if assigned',
  latitude DOUBLE COMMENT 'GPS latitude',
  longitude DOUBLE COMMENT 'GPS longitude',
  warranty_expiry DATE COMMENT 'Warranty end date',
  maintenance_schedule STRING COMMENT 'Maintenance frequency',
  criticality STRING COMMENT 'Business criticality: Low/Medium/High/Critical',
  status STRING DEFAULT 'Active' COMMENT 'Asset status',
  CONSTRAINT pk_assets_test PRIMARY KEY (asset_id)
) USING DELTA
COMMENT 'Test table: Asset/Inventory tracking for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO assets_test (asset_id, asset_name, asset_type, serial_number, manufacturer, model, purchase_date, purchase_cost, current_value, location, assigned_to, latitude, longitude, warranty_expiry, maintenance_schedule, criticality, status) VALUES
('AST-001', 'MacBook Pro 16', 'Hardware', 'SN-APPLE-001234', 'Apple', 'MacBook Pro 16 M3', '2024-01-10', 3499.00, 3200.00, 'New York Office', 'EMP-001', 40.7128, -74.0060, '2027-01-10', 'Annual', 'High', 'Active'),
('AST-002', 'Dell Server Rack', 'Hardware', 'SN-DELL-005678', 'Dell', 'PowerEdge R750', '2023-06-15', 15000.00, 12000.00, 'Data Center A', NULL, 37.7749, -122.4194, '2026-06-15', 'Quarterly', 'Critical', 'Active'),
('AST-003', 'Company Vehicle', 'Vehicle', 'VIN-12345678901234567', 'Tesla', 'Model Y', '2023-09-01', 55000.00, 48000.00, 'Los Angeles Office', 'EMP-005', 34.0522, -118.2437, '2027-09-01', 'Monthly', 'Medium', 'Active'),
('AST-004', 'Cisco Switch', 'Hardware', 'SN-CISCO-009012', 'Cisco', 'Catalyst 9300', '2022-03-20', 8500.00, 5500.00, 'Data Center B', NULL, 41.8781, -87.6298, '2025-03-20', 'Bi-Annual', 'Critical', 'Active'),
('AST-005', 'Salesforce License', 'Software', 'LIC-SF-2024-001', 'Salesforce', 'Enterprise Edition', '2024-01-01', 18000.00, 18000.00, 'Cloud', NULL, NULL, NULL, '2024-12-31', 'N/A', 'High', 'Active'),
('AST-006', 'Office Printer', 'Hardware', 'SN-HP-003456', 'HP', 'LaserJet Pro MFP', '2023-11-10', 1200.00, 1000.00, 'Chicago Office', NULL, 41.8781, -87.6298, '2025-11-10', 'Monthly', 'Low', 'Active'),
('AST-007', 'Conference Room System', 'Hardware', 'SN-ZOOM-007890', 'Zoom', 'Rooms Kit', '2023-08-05', 4500.00, 3800.00, 'New York Office', NULL, 40.7128, -74.0060, '2025-08-05', 'Quarterly', 'Medium', 'Active'),
('AST-008', 'Forklift', 'Vehicle', 'SN-CAT-112233', 'Caterpillar', 'DP25N', '2021-04-15', 35000.00, 22000.00, 'Warehouse A', 'EMP-009', 40.7282, -73.7949, '2024-04-15', 'Weekly', 'High', 'Active');

-- =============================================================================
-- TABLE 5: AUDIT_LOG - System access/activity log
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_log_test (
  log_id STRING NOT NULL COMMENT 'Unique log entry ID',
  event_timestamp TIMESTAMP NOT NULL COMMENT 'Event timestamp',
  user_id STRING COMMENT 'User who performed action',
  user_email STRING COMMENT 'User email (PII)',
  ip_address STRING COMMENT 'Client IP (PII)',
  user_agent STRING COMMENT 'Browser/client info',
  action_type STRING COMMENT 'Action: Login, Logout, Read, Write, Delete, etc.',
  resource_type STRING COMMENT 'Resource type: Table, File, API, etc.',
  resource_name STRING COMMENT 'Resource identifier',
  action_status STRING COMMENT 'Success, Failure, Denied',
  error_message STRING COMMENT 'Error details if failed',
  session_id STRING COMMENT 'Session identifier',
  request_id STRING COMMENT 'Unique request ID',
  duration_ms INT COMMENT 'Action duration in milliseconds',
  data_accessed_bytes BIGINT COMMENT 'Data volume accessed',
  sensitive_data_flag BOOLEAN DEFAULT FALSE COMMENT 'Sensitive data accessed',
  CONSTRAINT pk_audit_log_test PRIMARY KEY (log_id)
) USING DELTA
COMMENT 'Test table: System audit/access log for ABAC testing'
TBLPROPERTIES ('delta.feature.allowColumnDefaults' = 'supported');

INSERT INTO audit_log_test (log_id, event_timestamp, user_id, user_email, ip_address, user_agent, action_type, resource_type, resource_name, action_status, error_message, session_id, request_id, duration_ms, data_accessed_bytes, sensitive_data_flag) VALUES
('LOG-000001', '2024-01-15 08:00:15', 'U-1001', 'john.smith@example.com', '192.168.1.100', 'Mozilla/5.0 Chrome/120', 'Login', 'System', 'auth_service', 'Success', NULL, 'SES-001', 'REQ-0001', 245, 0, FALSE),
('LOG-000002', '2024-01-15 08:05:30', 'U-1001', 'john.smith@example.com', '192.168.1.100', 'Mozilla/5.0 Chrome/120', 'Read', 'Table', 'customers', 'Success', NULL, 'SES-001', 'REQ-0002', 1250, 524288, TRUE),
('LOG-000003', '2024-01-15 08:10:45', 'U-1001', 'john.smith@example.com', '192.168.1.100', 'Mozilla/5.0 Chrome/120', 'Write', 'Table', 'orders', 'Success', NULL, 'SES-001', 'REQ-0003', 890, 2048, FALSE),
('LOG-000004', '2024-01-15 09:00:00', 'U-1002', 'sarah.johnson@example.com', '10.0.1.50', 'Mozilla/5.0 Firefox/121', 'Login', 'System', 'auth_service', 'Success', NULL, 'SES-002', 'REQ-0004', 198, 0, FALSE),
('LOG-000005', '2024-01-15 09:15:22', 'U-1002', 'sarah.johnson@example.com', '10.0.1.50', 'Mozilla/5.0 Firefox/121', 'Read', 'Table', 'transactions', 'Success', NULL, 'SES-002', 'REQ-0005', 2100, 1048576, TRUE),
('LOG-000006', '2024-01-15 09:30:00', 'U-1003', 'mike.williams@example.com', '172.16.0.25', 'Mozilla/5.0 Safari/17', 'Login', 'System', 'auth_service', 'Failure', 'Invalid password', NULL, 'REQ-0006', 156, 0, FALSE),
('LOG-000007', '2024-01-15 09:31:00', 'U-1003', 'mike.williams@example.com', '172.16.0.25', 'Mozilla/5.0 Safari/17', 'Login', 'System', 'auth_service', 'Failure', 'Invalid password', NULL, 'REQ-0007', 145, 0, FALSE),
('LOG-000008', '2024-01-15 09:32:00', 'U-1003', 'mike.williams@example.com', '172.16.0.25', 'Mozilla/5.0 Safari/17', 'Login', 'System', 'auth_service', 'Denied', 'Account locked', NULL, 'REQ-0008', 89, 0, FALSE),
('LOG-000009', '2024-01-15 10:00:00', 'EMP-004', 'patricia.thomas@company.com', '192.168.3.75', 'Internal API', 'Read', 'Table', 'employees', 'Success', NULL, 'SES-003', 'REQ-0009', 3500, 2097152, TRUE),
('LOG-000010', '2024-01-15 10:30:00', 'EMP-008', 'nancy.clark@company.com', '192.168.1.200', 'Internal API', 'Delete', 'Table', 'terminated_employees', 'Denied', 'Insufficient permissions', 'SES-004', 'REQ-0010', 45, 0, TRUE);
"""

# =============================================================================
# STEP 5: TAG APPLICATIONS (for test tables)
# =============================================================================
TAG_APPLICATIONS_SQL = """
-- =============================================================================
-- USERS_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn', 'data_classification' = 'Restricted', 'compliance_requirement' = 'GLBA');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN email SET TAGS ('pii_type' = 'email', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN phone SET TAGS ('pii_type' = 'phone', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN first_name SET TAGS ('pii_type' = 'person_name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN last_name SET TAGS ('pii_type' = 'person_name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN date_of_birth SET TAGS ('pii_type' = 'dob', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.users_test ALTER COLUMN street_address SET TAGS ('pii_type' = 'address', 'data_classification' = 'Confidential');

-- =============================================================================
-- TRANSACTIONS_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN account_number SET TAGS ('pii_type' = 'account_number', 'data_classification' = 'Restricted', 'compliance_requirement' = 'PCI_DSS');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN card_number SET TAGS ('pii_type' = 'credit_card', 'data_classification' = 'Restricted', 'compliance_requirement' = 'PCI_DSS');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN ip_address SET TAGS ('pii_type' = 'ip_address', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN device_id SET TAGS ('pii_type' = 'device_id', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.transactions_test ALTER COLUMN amount SET TAGS ('pii_type' = 'financial_record', 'sensitivity_level' = 'High');

-- =============================================================================
-- EMPLOYEES_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN ssn SET TAGS ('pii_type' = 'ssn', 'data_classification' = 'Restricted', 'data_purpose' = 'HR');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN email SET TAGS ('pii_type' = 'email', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN phone SET TAGS ('pii_type' = 'phone', 'data_classification' = 'Confidential');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN first_name SET TAGS ('pii_type' = 'person_name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN last_name SET TAGS ('pii_type' = 'person_name', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN date_of_birth SET TAGS ('pii_type' = 'dob', 'data_classification' = 'Confidential', 'data_purpose' = 'HR');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN salary SET TAGS ('sensitivity_level' = 'High', 'data_purpose' = 'HR', 'data_classification' = 'Restricted');
ALTER TABLE {CATALOG}.{SCHEMA}.employees_test ALTER COLUMN bonus SET TAGS ('sensitivity_level' = 'High', 'data_purpose' = 'HR', 'data_classification' = 'Restricted');

-- =============================================================================
-- ASSETS_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN serial_number SET TAGS ('pii_type' = 'device_id', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN purchase_cost SET TAGS ('sensitivity_level' = 'Medium', 'data_purpose' = 'Operations');
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN latitude SET TAGS ('pii_type' = 'location', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.assets_test ALTER COLUMN longitude SET TAGS ('pii_type' = 'location', 'data_classification' = 'Internal');

-- =============================================================================
-- AUDIT_LOG_TEST Table Tags
-- =============================================================================
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test ALTER COLUMN user_email SET TAGS ('pii_type' = 'email', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test ALTER COLUMN ip_address SET TAGS ('pii_type' = 'ip_address', 'data_classification' = 'Internal');
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test ALTER COLUMN event_timestamp SET TAGS ('sensitivity_level' = 'High', 'data_purpose' = 'Audit');
ALTER TABLE {CATALOG}.{SCHEMA}.audit_log_test SET TAGS ('access_restriction' = 'Business_Hours');
"""

# List of test tables created
TEST_TABLES = ["users_test", "transactions_test", "employees_test", "assets_test", "audit_log_test"]
