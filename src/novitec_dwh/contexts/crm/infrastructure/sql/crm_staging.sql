CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_crm_customers (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nombres VARCHAR(120) NOT NULL,
    apellidos VARCHAR(120) NOT NULL,
    identificacion VARCHAR(30) NOT NULL,
    numero_contacto VARCHAR(40) NOT NULL,
    correo VARCHAR(180),
    direccion_clientes VARCHAR(255),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_crm_customers PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_crm_customers_identificacion
    ON {schema_name}.stg_crm_customers (identificacion);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_crm_companies (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nombre VARCHAR(180) NOT NULL,
    ruc VARCHAR(30) NOT NULL,
    telefono VARCHAR(40),
    correo VARCHAR(180),
    direccion_empresa VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_crm_companies PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_crm_companies_ruc
    ON {schema_name}.stg_crm_companies (ruc);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_crm_customer_branches (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    codigo VARCHAR(30) NOT NULL,
    numero INTEGER NOT NULL,
    nombre VARCHAR(180) NOT NULL,
    provincia VARCHAR(120),
    novitec_sucursal VARCHAR(120),
    activa BOOLEAN NOT NULL,
    created_at TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_crm_customer_branches PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_crm_customer_branches_codigo
    ON {schema_name}.stg_crm_customer_branches (codigo);
