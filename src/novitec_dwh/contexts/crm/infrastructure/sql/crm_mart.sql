CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_crm_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year_number INTEGER NOT NULL,
    quarter_number INTEGER NOT NULL,
    month_number INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day_number INTEGER NOT NULL,
    iso_week_number INTEGER NOT NULL,
    day_of_week_number INTEGER NOT NULL,
    day_of_week_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_crm_customer (
    customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    full_name VARCHAR(220) NOT NULL,
    first_name VARCHAR(120) NOT NULL,
    last_name VARCHAR(120) NOT NULL,
    identification VARCHAR(30) NOT NULL,
    phone_number VARCHAR(40) NOT NULL,
    email VARCHAR(180),
    address VARCHAR(255),
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_crm_company (
    company_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    company_name VARCHAR(180) NOT NULL,
    ruc VARCHAR(30) NOT NULL,
    phone_number VARCHAR(40),
    email VARCHAR(180),
    address VARCHAR(255),
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_crm_customers (
    fact_crm_customer_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    customer_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_crm_customer (customer_key),
    has_email BOOLEAN NOT NULL,
    has_address BOOLEAN NOT NULL,
    has_phone BOOLEAN NOT NULL,
    customer_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_crm_customers UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_crm_companies (
    fact_crm_company_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    company_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_crm_company (company_key),
    created_date_key INTEGER REFERENCES {mart_schema}.dim_crm_date (date_key),
    has_phone BOOLEAN NOT NULL,
    has_email BOOLEAN NOT NULL,
    has_address BOOLEAN NOT NULL,
    company_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_crm_companies UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_crm_customer_branches (
    fact_crm_customer_branch_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    created_date_key INTEGER REFERENCES {mart_schema}.dim_crm_date (date_key),
    branch_code VARCHAR(30) NOT NULL,
    branch_number INTEGER NOT NULL,
    branch_name VARCHAR(180) NOT NULL,
    province VARCHAR(120),
    novitec_branch_name VARCHAR(120),
    is_active BOOLEAN NOT NULL,
    branch_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_crm_customer_branches UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_crm_customer_branches_code
    ON {mart_schema}.fact_crm_customer_branches (branch_code);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_crm_quality_audit (
    quality_audit_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(80) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_crm_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);
