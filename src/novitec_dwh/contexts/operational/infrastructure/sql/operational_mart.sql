CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_operational_date (
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

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_operational_technician (
    technician_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tecnico_id INTEGER NOT NULL UNIQUE,
    tecnico_nombre VARCHAR(100) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_operational_branch (
    branch_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sucursal_id INTEGER NOT NULL UNIQUE,
    sucursal_nombre VARCHAR(100) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_operational_orders (
    fact_operational_order_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_order_id INTEGER NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    order_number VARCHAR(30) NOT NULL,
    intake_date_key INTEGER REFERENCES {mart_schema}.dim_operational_date (date_key),
    promised_date_key INTEGER REFERENCES {mart_schema}.dim_operational_date (date_key),
    delivery_date_key INTEGER REFERENCES {mart_schema}.dim_operational_date (date_key),
    billing_date_key INTEGER REFERENCES {mart_schema}.dim_operational_date (date_key),
    technician_key BIGINT REFERENCES {mart_schema}.dim_operational_technician (technician_key),
    branch_key BIGINT REFERENCES {mart_schema}.dim_operational_branch (branch_key),
    order_status VARCHAR(50),
    replacement_status VARCHAR(50),
    warranty_status VARCHAR(20),
    intake_reason VARCHAR(120),
    customer_type VARCHAR(20) NOT NULL,
    customer_name VARCHAR(200),
    device_type VARCHAR(100),
    device_brand VARCHAR(100),
    has_invoice BOOLEAN NOT NULL,
    is_delivered BOOLEAN NOT NULL,
    is_open BOOLEAN NOT NULL,
    is_warranty BOOLEAN NOT NULL,
    order_count INTEGER NOT NULL DEFAULT 1,
    cycle_days INTEGER,
    promised_cycle_days INTEGER,
    delay_days INTEGER,
    worked_hours NUMERIC(8, 2),
    hourly_rate NUMERIC(10, 2),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_operational_orders UNIQUE (extraction_id, source_order_id, order_type)
);

CREATE INDEX IF NOT EXISTS idx_fact_operational_orders_status
    ON {mart_schema}.fact_operational_orders (order_status);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_operational_preorders (
    fact_operational_preorder_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    linked_order_id INTEGER,
    registration_date_key INTEGER REFERENCES {mart_schema}.dim_operational_date (date_key),
    branch_key BIGINT REFERENCES {mart_schema}.dim_operational_branch (branch_key),
    preorder_number VARCHAR(20) NOT NULL,
    preorder_status VARCHAR(20),
    customer_name VARCHAR(200),
    city_name VARCHAR(100),
    has_invoice BOOLEAN NOT NULL,
    has_photos BOOLEAN NOT NULL,
    preorder_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_operational_preorders UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_operational_company_order_assignments (
    fact_operational_company_assignment_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    source_order_id INTEGER NOT NULL,
    technician_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_operational_technician (technician_key),
    assignment_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_operational_company_order_assignments UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_operational_quality_audit (
    quality_audit_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(80) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_operational_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);
