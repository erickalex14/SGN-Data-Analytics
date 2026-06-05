CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_reports (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    orden_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    antecedentes TEXT,
    proceso TEXT,
    conclusion TEXT,
    recomendaciones TEXT,
    estado_equipo VARCHAR(60),
    fecha_informe DATE NOT NULL,
    fecha_creacion TIMESTAMP NULL,
    presupuesto_json TEXT,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_reports PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_technical_reports_order
    ON {schema_name}.stg_technical_reports (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_report_photos (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    informe_id INTEGER NOT NULL,
    caption VARCHAR(255),
    nombre_archivo VARCHAR(255),
    tipo_mime VARCHAR(100),
    orden_foto INTEGER,
    tiene_foto BOOLEAN NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_report_photos PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_technical_report_photos_report
    ON {schema_name}.stg_technical_report_photos (informe_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_equipment (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    tipo_servicio_id INTEGER,
    tipo_servicio_texto VARCHAR(100),
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    serie VARCHAR(100) NOT NULL,
    contrasena_equipo VARCHAR(100),
    falla TEXT,
    observacion TEXT,
    fecha_facturacion DATE NULL,
    producto_inventario_codigo VARCHAR(30),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_equipment PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_technical_equipment_product
    ON {schema_name}.stg_technical_equipment (producto_inventario_codigo);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_equipment_series (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    serie VARCHAR(100) NOT NULL,
    orden INTEGER NOT NULL,
    created_at TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_equipment_series PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_technical_equipment_series_equipment
    ON {schema_name}.stg_technical_equipment_series (equipo_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_device_types (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    codigo VARCHAR(10) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_device_types PRIMARY KEY (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_service_types (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    descripcion VARCHAR(500),
    precio NUMERIC(10, 2) NOT NULL,
    activo BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_service_types PRIMARY KEY (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_brands (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_brands PRIMARY KEY (extraction_id, source_id)
);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_technical_equipment_credentials (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    usuario VARCHAR(100),
    es_patron BOOLEAN NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_technical_equipment_credentials PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_technical_equipment_credentials_equipment
    ON {schema_name}.stg_technical_equipment_credentials (equipo_id);
