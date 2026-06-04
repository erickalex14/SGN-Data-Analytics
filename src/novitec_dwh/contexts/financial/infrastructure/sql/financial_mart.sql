CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_financial_date (
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

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_financial_technician (
    technician_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tecnico_id INTEGER NOT NULL UNIQUE,
    tecnico_nombre VARCHAR(100) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_financial_credit_note_requests (
    fact_credit_note_request_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    request_number VARCHAR(20) NOT NULL,
    order_id INTEGER NOT NULL,
    order_number VARCHAR(30),
    request_date_key INTEGER NOT NULL REFERENCES {mart_schema}.dim_financial_date (date_key),
    created_date_key INTEGER REFERENCES {mart_schema}.dim_financial_date (date_key),
    technician_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_financial_technician (technician_key),
    status_name VARCHAR(20) NOT NULL,
    subject_name VARCHAR(200) NOT NULL,
    admin_name VARCHAR(100),
    rejection_reason TEXT,
    request_count INTEGER NOT NULL DEFAULT 1,
    is_pending BOOLEAN NOT NULL,
    is_approved BOOLEAN NOT NULL,
    is_rejected BOOLEAN NOT NULL,
    created_at TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_financial_credit_note_requests UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_financial_credit_note_requests_order
    ON {mart_schema}.fact_financial_credit_note_requests (order_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_financial_order_prices (
    fact_order_price_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    order_number VARCHAR(30),
    created_date_key INTEGER REFERENCES {mart_schema}.dim_financial_date (date_key),
    price_standard_id INTEGER,
    service_name VARCHAR(200) NOT NULL,
    standard_service_name VARCHAR(200),
    amount NUMERIC(10, 2) NOT NULL,
    standard_amount NUMERIC(10, 2),
    record_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_financial_order_prices UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_financial_order_prices_order
    ON {mart_schema}.fact_financial_order_prices (order_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_financial_credit_note_notifications (
    fact_credit_note_notification_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    order_id INTEGER,
    order_number VARCHAR(30),
    nc_id INTEGER,
    notification_date_key INTEGER NOT NULL REFERENCES {mart_schema}.dim_financial_date (date_key),
    technician_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_financial_technician (technician_key),
    notification_type VARCHAR(30) NOT NULL,
    is_read BOOLEAN NOT NULL,
    notification_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_financial_credit_note_notifications UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_financial_credit_note_notifications_order
    ON {mart_schema}.fact_financial_credit_note_notifications (order_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_financial_quality_audit (
    quality_audit_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(80) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_financial_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);

CREATE INDEX IF NOT EXISTS idx_etl_financial_quality_audit_extraction
    ON {mart_schema}.etl_financial_quality_audit (extraction_id);
