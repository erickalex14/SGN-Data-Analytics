CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_financial_credit_note_requests (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_solicitud VARCHAR(20) NOT NULL,
    orden_id INTEGER NOT NULL,
    nro_orden VARCHAR(30),
    fecha_solicitud DATE NOT NULL,
    asunto VARCHAR(200) NOT NULL,
    detalles TEXT NOT NULL,
    nombre_admin VARCHAR(100),
    motivo_rechazo TEXT,
    tecnico_nombre VARCHAR(100) NOT NULL,
    tecnico_id INTEGER NOT NULL,
    estado VARCHAR(20) NOT NULL,
    creado_en TIMESTAMP NULL,
    created_at TIMESTAMP NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_financial_credit_note_requests
        PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_financial_credit_note_requests_orden
    ON {schema_name}.stg_financial_credit_note_requests (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_financial_order_prices (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    orden_id INTEGER NOT NULL,
    nro_orden VARCHAR(30),
    precio_estandar_id INTEGER,
    servicio VARCHAR(200) NOT NULL,
    precio NUMERIC(10, 2) NOT NULL,
    descripcion VARCHAR(500),
    creado_en TIMESTAMP NULL,
    servicio_estandar VARCHAR(200),
    precio_estandar NUMERIC(10, 2),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_financial_order_prices
        PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_financial_order_prices_orden
    ON {schema_name}.stg_financial_order_prices (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_financial_credit_note_notifications (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    usuario_nombre VARCHAR(100),
    tipo VARCHAR(30) NOT NULL,
    mensaje VARCHAR(300) NOT NULL,
    nc_id INTEGER,
    orden_id INTEGER,
    nro_orden VARCHAR(30),
    leida BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_financial_credit_note_notifications
        PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_financial_credit_note_notifications_orden
    ON {schema_name}.stg_financial_credit_note_notifications (orden_id);
