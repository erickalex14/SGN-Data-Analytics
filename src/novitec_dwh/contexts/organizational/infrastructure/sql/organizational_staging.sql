CREATE SCHEMA IF NOT EXISTS {schema_name};

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_branches (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nro_sucursal INTEGER NOT NULL,
    ciudad VARCHAR(120) NOT NULL,
    secuencial VARCHAR(20) NOT NULL,
    nro_base VARCHAR(20),
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_branches PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_branches_nro_sucursal
    ON {schema_name}.stg_organizational_branches (nro_sucursal);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_roles (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    rol VARCHAR(60) NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_roles PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_roles_rol
    ON {schema_name}.stg_organizational_roles (rol);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_access_groups (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    descripcion VARCHAR(255),
    es_superadmin BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_access_groups PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_access_groups_nombre
    ON {schema_name}.stg_organizational_access_groups (nombre);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_users (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    usuario VARCHAR(30) NOT NULL,
    nombre_tecnico VARCHAR(120) NOT NULL,
    telefono VARCHAR(30),
    correo_tec VARCHAR(180),
    acceso_nc BOOLEAN NOT NULL,
    rol_id INTEGER NOT NULL,
    sucursal_id INTEGER NOT NULL,
    activo BOOLEAN NOT NULL,
    grupo_id INTEGER,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_users PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_users_usuario
    ON {schema_name}.stg_organizational_users (usuario);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_user_branches (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    sucursal_id INTEGER NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_user_branches PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_user_branches_usuario
    ON {schema_name}.stg_organizational_user_branches (usuario_id);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_group_permissions (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    modulo VARCHAR(80) NOT NULL,
    accion VARCHAR(20) NOT NULL,
    permitido BOOLEAN NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_group_permissions PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_group_permissions_grupo
    ON {schema_name}.stg_organizational_group_permissions (grupo_id, modulo, accion);

CREATE TABLE IF NOT EXISTS {schema_name}.stg_organizational_user_permissions (
    extraction_id VARCHAR(64) NOT NULL,
    source_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    modulo VARCHAR(80) NOT NULL,
    accion VARCHAR(20) NOT NULL,
    permitido BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_stg_organizational_user_permissions PRIMARY KEY (extraction_id, source_id)
);

CREATE INDEX IF NOT EXISTS idx_stg_organizational_user_permissions_usuario
    ON {schema_name}.stg_organizational_user_permissions (usuario_id, modulo, accion);
