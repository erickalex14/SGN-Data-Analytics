CREATE SCHEMA IF NOT EXISTS {mart_schema};

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_organizational_date (
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

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_organizational_branch (
    branch_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    branch_number INTEGER NOT NULL,
    city_name VARCHAR(120) NOT NULL,
    sequential_code VARCHAR(20) NOT NULL,
    base_number VARCHAR(20),
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_organizational_role (
    role_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    role_name VARCHAR(60) NOT NULL,
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_organizational_access_group (
    access_group_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    group_name VARCHAR(120) NOT NULL,
    description VARCHAR(255),
    is_superadmin BOOLEAN NOT NULL,
    created_date_key INTEGER REFERENCES {mart_schema}.dim_organizational_date (date_key),
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.dim_organizational_user (
    user_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_id INTEGER NOT NULL UNIQUE,
    user_login VARCHAR(30) NOT NULL,
    user_name VARCHAR(120) NOT NULL,
    phone_number VARCHAR(30),
    email VARCHAR(180),
    first_extraction_id VARCHAR(64) NOT NULL,
    last_extraction_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_organizational_users (
    fact_organizational_user_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    user_key BIGINT NOT NULL REFERENCES {mart_schema}.dim_organizational_user (user_key),
    role_key BIGINT REFERENCES {mart_schema}.dim_organizational_role (role_key),
    branch_key BIGINT REFERENCES {mart_schema}.dim_organizational_branch (branch_key),
    access_group_key BIGINT REFERENCES {mart_schema}.dim_organizational_access_group (access_group_key),
    has_phone BOOLEAN NOT NULL,
    has_email BOOLEAN NOT NULL,
    can_access_nc BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    has_access_group BOOLEAN NOT NULL,
    user_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_organizational_users UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_organizational_user_branches (
    fact_organizational_user_branch_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    user_key BIGINT REFERENCES {mart_schema}.dim_organizational_user (user_key),
    branch_key BIGINT REFERENCES {mart_schema}.dim_organizational_branch (branch_key),
    user_id INTEGER NOT NULL,
    branch_id INTEGER NOT NULL,
    assignment_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_organizational_user_branches UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_organizational_group_permissions (
    fact_organizational_group_permission_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    access_group_key BIGINT REFERENCES {mart_schema}.dim_organizational_access_group (access_group_key),
    group_id INTEGER NOT NULL,
    module_name VARCHAR(80) NOT NULL,
    action_name VARCHAR(20) NOT NULL,
    is_allowed BOOLEAN NOT NULL,
    permission_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_organizational_group_permissions UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.fact_organizational_user_permissions (
    fact_organizational_user_permission_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    user_key BIGINT REFERENCES {mart_schema}.dim_organizational_user (user_key),
    created_date_key INTEGER REFERENCES {mart_schema}.dim_organizational_date (date_key),
    user_id INTEGER NOT NULL,
    module_name VARCHAR(80) NOT NULL,
    action_name VARCHAR(20) NOT NULL,
    is_allowed BOOLEAN NOT NULL,
    permission_count INTEGER NOT NULL DEFAULT 1,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_fact_organizational_user_permissions UNIQUE (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {mart_schema}.etl_organizational_quality_audit (
    quality_audit_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    extraction_id VARCHAR(64) NOT NULL,
    entity_name VARCHAR(80) NOT NULL,
    rule_name VARCHAR(120) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    affected_rows INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_etl_organizational_quality_audit UNIQUE (extraction_id, entity_name, rule_name)
);
