CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_technical_date (
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

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_technical_technician (
    technician_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tecnico_id INTEGER NOT NULL UNIQUE,
    tecnico_nombre VARCHAR(100) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_technical_service_type (
    service_type_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    service_name VARCHAR(200) NOT NULL,
    service_description VARCHAR(500),
    standard_price NUMERIC(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_technical_brand (
    brand_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    brand_name VARCHAR(100) NOT NULL UNIQUE,
    source_id INTEGER,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_technical_reports (
    fact_technical_report_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    technician_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_technical_technician (technician_key),
    report_date_key INTEGER NOT NULL REFERENCES {mart_schema}.dim_technical_date (date_key),
    created_date_key INTEGER REFERENCES {mart_schema}.dim_technical_date (date_key),
    equipment_status VARCHAR(60),
    has_background BOOLEAN NOT NULL,
    has_process BOOLEAN NOT NULL,
    has_conclusion BOOLEAN NOT NULL,
    has_recommendations BOOLEAN NOT NULL,
    has_budget_json BOOLEAN NOT NULL,
    is_equipment_operational BOOLEAN NOT NULL,
    background_length INTEGER,
    process_length INTEGER,
    conclusion_length INTEGER,
    recommendation_length INTEGER,
    report_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_technical_reports UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_technical_reports_order
    ON {mart_schema}.fact_technical_reports (order_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_technical_report_photos (
    fact_technical_report_photo_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    report_source_id INTEGER NOT NULL,
    report_date_key INTEGER REFERENCES {mart_schema}.dim_technical_date (date_key),
    technician_key BIGINT REFERENCES {mart_schema}.dim_technical_technician (technician_key),
    photo_order INTEGER,
    file_name VARCHAR(255),
    mime_type VARCHAR(100),
    caption VARCHAR(255),
    has_binary_evidence BOOLEAN NOT NULL,
    has_file_name BOOLEAN NOT NULL,
    is_jpeg BOOLEAN NOT NULL,
    photo_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_technical_report_photos UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_technical_report_photos_report
    ON {mart_schema}.fact_technical_report_photos (report_source_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_technical_equipment (
    fact_technical_equipment_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    service_type_key BIGINT REFERENCES {mart_schema}.dim_technical_service_type (service_type_key),
    brand_key BIGINT REFERENCES {mart_schema}.dim_technical_brand (brand_key),
    billing_date_key INTEGER REFERENCES {mart_schema}.dim_technical_date (date_key),
    device_type_name VARCHAR(100),
    device_model VARCHAR(100),
    serial_number VARCHAR(100),
    inventory_product_code VARCHAR(30),
    has_password_provided BOOLEAN NOT NULL,
    has_failure_description BOOLEAN NOT NULL,
    has_observation BOOLEAN NOT NULL,
    has_billing_date BOOLEAN NOT NULL,
    equipment_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_technical_equipment UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_technical_equipment_service_type
    ON {mart_schema}.fact_technical_equipment (service_type_key);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_technical_equipment_access (
    fact_technical_equipment_access_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    equipment_source_id INTEGER NOT NULL,
    has_user_name BOOLEAN NOT NULL,
    is_pattern BOOLEAN NOT NULL,
    access_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_technical_equipment_access UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_technical_equipment_access_equipment
    ON {mart_schema}.fact_technical_equipment_access (equipment_source_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_technical_quality_audit (
    quality_audit_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(80) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_technical_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);
