CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_inventory_date (
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

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_inventory_technician (
    technician_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tecnico_id INTEGER NOT NULL UNIQUE,
    tecnico_nombre VARCHAR(120) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_inventory_spare_part (
    spare_part_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    spare_part_code VARCHAR(60) NOT NULL,
    part_number VARCHAR(100),
    spare_part_name VARCHAR(180) NOT NULL,
    brand_source_id INTEGER,
    device_type_source_id INTEGER,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_inventory_spare_parts (
    fact_inventory_spare_part_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    spare_part_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_inventory_spare_part (spare_part_key),
    created_date_key INTEGER REFERENCES {mart_schema}.dim_inventory_date (date_key),
    updated_date_key INTEGER REFERENCES {mart_schema}.dim_inventory_date (date_key),
    current_stock INTEGER NOT NULL,
    current_cost NUMERIC(10, 2) NOT NULL,
    warehouse_number SMALLINT NOT NULL,
    has_stock BOOLEAN NOT NULL,
    has_part_number BOOLEAN NOT NULL,
    spare_part_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_inventory_spare_parts UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_spare_parts_key
    ON {mart_schema}.fact_inventory_spare_parts (spare_part_key);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_inventory_order_spare_parts (
    fact_inventory_order_spare_part_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL,
    spare_part_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_inventory_spare_part (spare_part_key),
    movement_date_key INTEGER REFERENCES {mart_schema}.dim_inventory_date (date_key),
    installer_user_id INTEGER,
    quantity INTEGER NOT NULL,
    has_installer_user BOOLEAN NOT NULL,
    consumption_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_inventory_order_spare_parts UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_order_spare_parts_order
    ON {mart_schema}.fact_inventory_order_spare_parts (order_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_inventory_spare_part_requests (
    fact_inventory_spare_part_request_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    request_number VARCHAR(30) NOT NULL,
    order_id INTEGER NOT NULL,
    technician_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_inventory_technician (technician_key),
    spare_part_key BIGINT REFERENCES {mart_schema}.dim_inventory_spare_part (spare_part_key),
    request_date_key INTEGER NOT NULL REFERENCES {mart_schema}.dim_inventory_date (date_key),
    management_date_key INTEGER REFERENCES {mart_schema}.dim_inventory_date (date_key),
    approved_by VARCHAR(120),
    request_status VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    is_approved BOOLEAN NOT NULL,
    is_rejected BOOLEAN NOT NULL,
    is_pending BOOLEAN NOT NULL,
    has_purchase_link BOOLEAN NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_inventory_spare_part_requests UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_spare_part_requests_order
    ON {mart_schema}.fact_inventory_spare_part_requests (order_id);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_inventory_purchase_lists (
    fact_inventory_purchase_list_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    list_number VARCHAR(30) NOT NULL,
    creator_user_id INTEGER,
    creation_date_key INTEGER NOT NULL REFERENCES {mart_schema}.dim_inventory_date (date_key),
    created_date_key INTEGER NOT NULL REFERENCES {mart_schema}.dim_inventory_date (date_key),
    list_status VARCHAR(20) NOT NULL,
    has_observation BOOLEAN NOT NULL,
    purchase_list_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_inventory_purchase_lists UNIQUE (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_fact_inventory_purchase_lists_number
    ON {mart_schema}.fact_inventory_purchase_lists (list_number);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_inventory_quality_audit (
    quality_audit_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(80) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_inventory_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);
