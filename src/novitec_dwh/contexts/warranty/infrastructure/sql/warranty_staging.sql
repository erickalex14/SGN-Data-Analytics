CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_warranty_service_centers (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    prefijo VARCHAR(20),
    marca VARCHAR(80),
    telefono VARCHAR(40),
    correo VARCHAR(120),
    direccion VARCHAR(200),
    ciudad VARCHAR(80),
    contacto VARCHAR(100),
    notas TEXT,
    activo BOOLEAN NOT NULL,
    creado_en TIMESTAMP NOT NULL,
    actualizado_en TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_warranty_service_centers PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_warranty_service_centers_nombre
    ON {schema_name}.stg_warranty_service_centers (nombre);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_warranty_user_assignments (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    usuario_login VARCHAR(20) NOT NULL,
    usuario_nombre VARCHAR(120) NOT NULL,
    cas_id INTEGER NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_warranty_user_assignments PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_warranty_user_assignments_usuario
    ON {schema_name}.stg_warranty_user_assignments (usuario_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_warranty_personal_orders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_orden VARCHAR(30),
    cliente_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    sucursal_id INTEGER NOT NULL,
    fecha_de_ingreso TIMESTAMP NULL,
    estado_orden VARCHAR(50),
    estado_garantia VARCHAR(20),
    garantia_tipo VARCHAR(20),
    garantia_cas VARCHAR(100),
    cas_id INTEGER,
    cas_fecha_envio DATE,
    cas_fecha_retorno DATE,
    cas_numero_caso VARCHAR(60),
    fecha_prometido DATE,
    fecha_entrega TIMESTAMP NULL,
    fecha_finalizacion TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_warranty_personal_orders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_warranty_personal_orders_cas
    ON {schema_name}.stg_warranty_personal_orders (cas_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_warranty_company_orders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_orden VARCHAR(30) NOT NULL,
    empresa_id INTEGER NOT NULL,
    equipo_id INTEGER,
    tecnico_id INTEGER NOT NULL,
    sucursal_id INTEGER NOT NULL,
    cas_id INTEGER,
    fecha_ingreso TIMESTAMP NOT NULL,
    fecha_prometido DATE,
    estado VARCHAR(50) NOT NULL,
    valor_hora NUMERIC(10, 2),
    horas_trabajadas NUMERIC(8, 2),
    nro_ticket VARCHAR(100),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_warranty_company_orders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_warranty_company_orders_cas
    ON {schema_name}.stg_warranty_company_orders (cas_id);
