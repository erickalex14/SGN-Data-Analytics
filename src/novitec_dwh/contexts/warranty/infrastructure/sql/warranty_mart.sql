CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_warranty_date (
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

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_warranty_service_center (
    service_center_key BIGSERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    service_center_name VARCHAR(120) NOT NULL,
    prefix_code VARCHAR(20),
    brand_name VARCHAR(80),
    phone_number VARCHAR(40),
    email VARCHAR(120),
    address TEXT,
    city_name VARCHAR(80),
    contact_name VARCHAR(100),
    notes TEXT,
    is_active BOOLEAN NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_warranty_user (
    user_key BIGSERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    user_login VARCHAR(40),
    user_name VARCHAR(120) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_warranty_personal_orders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    opened_date_key INTEGER,
    promised_date_key INTEGER,
    shipped_date_key INTEGER,
    returned_date_key INTEGER,
    delivered_date_key INTEGER,
    finalized_date_key INTEGER,
    service_center_key BIGINT,
    technician_key BIGINT,
    branch_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    equipment_id INTEGER NOT NULL,
    order_number VARCHAR(30),
    order_status VARCHAR(60),
    warranty_status VARCHAR(40),
    warranty_type VARCHAR(40),
    service_center_name VARCHAR(120),
    case_number VARCHAR(60),
    cycle_days INTEGER,
    sla_days INTEGER,
    has_case_number BOOLEAN NOT NULL,
    has_return_date BOOLEAN NOT NULL,
    is_closed BOOLEAN NOT NULL,
    order_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_fact_warranty_personal_orders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_warranty_personal_orders_service_center
    ON {mart_schema}.fact_warranty_personal_orders (service_center_key);

CREATE INDEX IF NOT EXISTS idx_fact_warranty_personal_orders_technician
    ON {mart_schema}.fact_warranty_personal_orders (technician_key);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_warranty_company_orders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    opened_date_key INTEGER,
    promised_date_key INTEGER,
    service_center_key BIGINT,
    technician_key BIGINT,
    branch_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    equipment_id INTEGER,
    order_number VARCHAR(30) NOT NULL,
    order_status VARCHAR(60) NOT NULL,
    ticket_number VARCHAR(100),
    hourly_rate NUMERIC(10, 2),
    worked_hours NUMERIC(8, 2),
    estimated_revenue NUMERIC(12, 2),
    cycle_days INTEGER,
    sla_days INTEGER,
    has_ticket_number BOOLEAN NOT NULL,
    has_worked_hours BOOLEAN NOT NULL,
    order_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_fact_warranty_company_orders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_warranty_company_orders_service_center
    ON {mart_schema}.fact_warranty_company_orders (service_center_key);

CREATE INDEX IF NOT EXISTS idx_fact_warranty_company_orders_technician
    ON {mart_schema}.fact_warranty_company_orders (technician_key);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_warranty_user_assignments (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    user_key BIGINT,
    service_center_key BIGINT,
    user_id INTEGER NOT NULL,
    service_center_id INTEGER NOT NULL,
    assignment_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_fact_warranty_user_assignments PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_warranty_user_assignments_user
    ON {mart_schema}.fact_warranty_user_assignments (user_key);

CREATE INDEX IF NOT EXISTS idx_fact_warranty_user_assignments_service_center
    ON {mart_schema}.fact_warranty_user_assignments (service_center_key);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_warranty_quality_audit (
    quality_audit_key BIGSERIAL PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(60) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_warranty_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);
