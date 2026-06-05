CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_inventory_spare_parts (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    codigo VARCHAR(60) NOT NULL,
    nro_parte VARCHAR(100),
    nombre VARCHAR(180) NOT NULL,
    descripcion VARCHAR(400),
    marca_id VARCHAR(36),
    tipo_dispositivo_id VARCHAR(36),
    creado_en TIMESTAMP NULL,
    modificado_en TIMESTAMP NULL,
    stock INTEGER NOT NULL,
    costo NUMERIC(10, 2) NOT NULL,
    bodega SMALLINT NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_inventory_spare_parts PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_inventory_spare_parts_codigo
    ON {schema_name}.stg_inventory_spare_parts (codigo);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_inventory_products (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    codigo VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    marca_id INTEGER NOT NULL,
    tipo_dispositivo_id INTEGER,
    tipo_dispositivo_codigo VARCHAR(10),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_inventory_products PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_inventory_products_codigo
    ON {schema_name}.stg_inventory_products (codigo);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_inventory_order_spare_parts (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    orden_id INTEGER NOT NULL,
    repuesto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    fecha TIMESTAMP NULL,
    usuario_id INTEGER,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_inventory_order_spare_parts PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_inventory_order_spare_parts_orden
    ON {schema_name}.stg_inventory_order_spare_parts (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_inventory_spare_part_requests (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_solicitud VARCHAR(30) NOT NULL,
    orden_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    tecnico_nombre VARCHAR(120) NOT NULL,
    repuesto_nombre VARCHAR(200) NOT NULL,
    nro_parte VARCHAR(100),
    nro_parte_inv_id INTEGER,
    repuesto_codigo VARCHAR(60),
    repuesto_inv_id INTEGER,
    link_compra VARCHAR(500),
    cantidad INTEGER NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) NOT NULL,
    motivo_rechazo TEXT,
    aprobado_por VARCHAR(120),
    repuesto_id INTEGER,
    lista_compra_id INTEGER,
    fecha_solicitud DATE NOT NULL,
    fecha_gestion TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_inventory_spare_part_requests PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_inventory_spare_part_requests_orden
    ON {schema_name}.stg_inventory_spare_part_requests (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_inventory_purchase_lists (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_lista VARCHAR(30) NOT NULL,
    creado_por VARCHAR(120) NOT NULL,
    creado_por_id INTEGER,
    fecha_creacion DATE NOT NULL,
    estado VARCHAR(20) NOT NULL,
    observacion TEXT,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_inventory_purchase_lists PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_inventory_purchase_lists_nro
    ON {schema_name}.stg_inventory_purchase_lists (nro_lista);
