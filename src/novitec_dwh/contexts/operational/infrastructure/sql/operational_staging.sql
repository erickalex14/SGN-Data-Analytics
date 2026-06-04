CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_operational_order_view (
    extraction_id VARCHAR(64) NOT NULL,
    orden_id INTEGER NOT NULL,
    nro_orden VARCHAR(30) NOT NULL,
    tipo_orden VARCHAR(20) NOT NULL,
    estado_orden VARCHAR(50),
    estado_repuesto VARCHAR(50),
    estado_garantia VARCHAR(20),
    motivo_ingreso VARCHAR(120),
    fecha_de_ingreso TIMESTAMP NULL,
    fecha_prometido DATE NULL,
    fecha_entrega TIMESTAMP NULL,
    nro_factura VARCHAR(20),
    nro_factura_2 VARCHAR(20),
    nro_sucursal_cliente VARCHAR(20),
    tecnico_id INTEGER,
    sucursal_id INTEGER,
    ingresado_por INTEGER,
    cliente_id INTEGER,
    empresa_id INTEGER,
    equipo_id INTEGER,
    cliente VARCHAR(200),
    nombres VARCHAR(200),
    apellidos VARCHAR(200),
    identificacion VARCHAR(30),
    numero_contacto VARCHAR(30),
    correo VARCHAR(150),
    direccion VARCHAR(255),
    tipo VARCHAR(100),
    marca VARCHAR(100),
    modelo VARCHAR(100),
    serie VARCHAR(120),
    falla TEXT,
    observacion TEXT,
    fecha_facturacion VARCHAR(20),
    tecnico VARCHAR(100),
    sucursal VARCHAR(100),
    fecha_de_ingreso_fmt VARCHAR(30),
    fecha_prometido_fmt VARCHAR(20),
    fecha_entrega_fmt VARCHAR(20),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_operational_order_view PRIMARY KEY (extraction_id, orden_id, tipo_orden)
);

CREATE INDEX IF NOT EXISTS idx_stg_operational_order_view_order
    ON {schema_name}.stg_operational_order_view (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_operational_personal_orders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_orden VARCHAR(30),
    nro_factura VARCHAR(20),
    nro_factura_2 VARCHAR(20),
    motivo_ingreso VARCHAR(80) NOT NULL,
    nro_sucursal_cliente VARCHAR(20),
    cliente_id INTEGER NOT NULL,
    equipo_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    sucursal_id INTEGER NOT NULL,
    fecha_de_ingreso TIMESTAMP NULL,
    estado_orden VARCHAR(50),
    estado_repuesto VARCHAR(50),
    estado_garantia VARCHAR(20),
    garantia_tipo VARCHAR(20),
    garantia_cas VARCHAR(100),
    cas_id INTEGER,
    cas_fecha_envio DATE NULL,
    cas_fecha_retorno DATE NULL,
    cas_numero_caso VARCHAR(60),
    ingresado_por INTEGER,
    fecha_prometido DATE NULL,
    modificado_por INTEGER,
    fecha_modificacion TIMESTAMP NULL,
    fecha_entrega TIMESTAMP NULL,
    fecha_finalizacion TIMESTAMP NULL,
    valor_estandar_id INTEGER,
    repuesto_inventario_id INTEGER,
    observacion TEXT,
    tipo_servicio_id INTEGER,
    tipo_servicio_texto VARCHAR(255),
    fecha_facturacion DATE NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_operational_personal_orders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_operational_personal_orders_order
    ON {schema_name}.stg_operational_personal_orders (source_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_operational_company_orders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_orden VARCHAR(30) NOT NULL,
    empresa_id INTEGER NOT NULL,
    subtipo VARCHAR(50) NOT NULL,
    nro_sucursal_cliente VARCHAR(20),
    equipo_id INTEGER,
    tipo_servicio VARCHAR(255),
    nro_ticket VARCHAR(100),
    descripcion TEXT,
    tecnico_id INTEGER NOT NULL,
    sucursal_id INTEGER NOT NULL,
    cas_id INTEGER,
    ingresado_por INTEGER,
    fecha_prometido DATE NULL,
    estado VARCHAR(50) NOT NULL,
    valor_hora NUMERIC(10, 2),
    horas_trabajadas NUMERIC(8, 2),
    fecha_ingreso TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_operational_company_orders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_operational_company_orders_order
    ON {schema_name}.stg_operational_company_orders (source_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_operational_preorders (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    orden_id INTEGER,
    fecha_registro TIMESTAMP NULL,
    nro_preorden VARCHAR(20) NOT NULL,
    sucursal_id INTEGER NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    identificacion VARCHAR(20),
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    nro_factura VARCHAR(20),
    codigo_producto VARCHAR(50),
    desc_producto VARCHAR(255),
    marca_producto VARCHAR(100),
    tipo_producto VARCHAR(100),
    detalle_equipo TEXT,
    foto_1 VARCHAR(255),
    foto_2 VARCHAR(255),
    foto_3 VARCHAR(255),
    foto_4 VARCHAR(255),
    estado VARCHAR(20),
    created_at TIMESTAMP NULL,
    nro_sucursal_cliente INTEGER,
    ciudad_procedencia VARCHAR(100),
    fecha_facturacion DATE NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_operational_preorders PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_operational_preorders_order
    ON {schema_name}.stg_operational_preorders (orden_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_operational_order_company_technicians (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    orden_empresa_id INTEGER NOT NULL,
    tecnico_id INTEGER NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_operational_order_company_technicians PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_operational_order_company_technicians_order
    ON {schema_name}.stg_operational_order_company_technicians (orden_empresa_id);
