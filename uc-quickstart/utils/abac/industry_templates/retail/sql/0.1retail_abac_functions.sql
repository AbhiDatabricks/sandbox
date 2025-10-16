-- RETAIL & E-COMMERCE ABAC FUNCTIONS
USE CATALOG apscat;
USE SCHEMA retail;

-- 1. EMAIL MASKING
CREATE OR REPLACE FUNCTION mask_email(email STRING) RETURNS STRING
COMMENT 'Mask email local part' RETURN CASE WHEN email IS NULL OR email = '' THEN email
WHEN email NOT LIKE '%@%' THEN '****' ELSE CONCAT('****@', SPLIT(email, '@')[1]) END;

-- 2. PHONE MASKING  
CREATE OR REPLACE FUNCTION mask_phone(phone STRING) RETURNS STRING
COMMENT 'Mask phone showing last 4' RETURN CASE WHEN phone IS NULL THEN phone
ELSE CONCAT('XXXX', RIGHT(REGEXP_REPLACE(phone, '[^0-9]', ''), 4)) END;

-- 3. CREDIT CARD LAST 4
CREATE OR REPLACE FUNCTION mask_credit_card_last4(card STRING) RETURNS STRING
COMMENT 'Show last 4 of card' RETURN CASE WHEN card IS NULL THEN card
WHEN LENGTH(card) < 4 THEN '****' ELSE CONCAT('****-****-****-', RIGHT(REGEXP_REPLACE(card, '[^0-9]', ''), 4)) END;

-- 4. ADDRESS PARTIAL (City, State only)
CREATE OR REPLACE FUNCTION mask_address_partial(address STRING) RETURNS STRING
COMMENT 'Show city/state only' RETURN CASE WHEN address IS NULL THEN address
WHEN address LIKE '%,%' THEN CONCAT(SPLIT(address, ',')[1], ', ', SUBSTRING(SPLIT(address, ',')[2], 1, 2))
ELSE '[REDACTED]' END;

-- 5. ORDER AMOUNT BUCKETING
CREATE OR REPLACE FUNCTION mask_order_amount_bucket(amount DECIMAL(12,2)) RETURNS STRING
COMMENT 'Order amount ranges' RETURN CASE WHEN amount IS NULL THEN 'Unknown' WHEN amount < 0 THEN 'Refund'
WHEN amount = 0 THEN '$0' WHEN amount < 50 THEN '$0-$50' WHEN amount < 100 THEN '$50-$100'
WHEN amount < 250 THEN '$100-$250' WHEN amount < 500 THEN '$250-$500' WHEN amount < 1000 THEN '$500-$1K'
ELSE '$1K+' END;

-- 6. CUSTOMER ID DETERMINISTIC
CREATE OR REPLACE FUNCTION mask_customer_id_hash(customer_id STRING) RETURNS STRING
COMMENT 'Deterministic customer ID' RETURN CASE WHEN customer_id IS NULL THEN customer_id
ELSE CONCAT('CUST_', SUBSTRING(SHA2(customer_id, 256), 1, 12)) END;

-- 7. PRODUCT COST MASKING
CREATE OR REPLACE FUNCTION mask_product_cost(cost DECIMAL(12,2)) RETURNS STRING
COMMENT 'Hide wholesale cost' RETURN '[REDACTED]';

-- 8. IP ADDRESS MASKING
CREATE OR REPLACE FUNCTION mask_ip_address(ip STRING) RETURNS STRING
COMMENT 'Mask last octet' RETURN CASE WHEN ip IS NULL OR ip NOT LIKE '%.%.%.%' THEN ip
ELSE CONCAT(SPLIT(ip, '\\.')[0], '.', SPLIT(ip, '\\.')[1], '.', SPLIT(ip, '\\.')[2], '.***') END;

-- 9. BUSINESS HOURS FILTER
CREATE OR REPLACE FUNCTION filter_business_hours() RETURNS BOOLEAN
COMMENT 'Business hours only' RETURN HOUR(CURRENT_TIMESTAMP()) BETWEEN 9 AND 17;

SELECT '✅ Retail ABAC functions created!' AS status;
