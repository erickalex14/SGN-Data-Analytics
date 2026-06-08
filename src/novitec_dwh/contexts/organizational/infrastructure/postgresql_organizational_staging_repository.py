"""Repositorio PostgreSQL para carga del dominio organizacional a staging."""

from importlib.resources import files
from typing import Final

from novitec_dwh.contexts.organizational.domain.entities import (
    GrupoAcceso,
    PermisoGrupo,
    PermisoUsuario,
    RolUsuario,
    SucursalPropia,
    UsuarioInterno,
    UsuarioSucursal,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

SUCURSALES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_sucursal",
    "ciudad",
    "secuencial",
    "nro_base",
]

ROLES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "rol",
]

GRUPOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nombre",
    "descripcion",
    "es_superadmin",
    "created_at",
]

USUARIOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "usuario",
    "nombre_tecnico",
    "telefono",
    "correo_tec",
    "acceso_nc",
    "rol_id",
    "sucursal_id",
    "activo",
    "grupo_id",
]

USUARIOS_SUCURSALES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "usuario_id",
    "sucursal_id",
]

PERMISOS_GRUPO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "grupo_id",
    "modulo",
    "accion",
    "permitido",
]

PERMISOS_USUARIO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "usuario_id",
    "modulo",
    "accion",
    "permitido",
    "created_at",
]


class PostgreSQLOrganizationalStagingRepository:
    """Gestiona persistencia staging organizacional en PostgreSQL."""

    def __init__(
        self,
        connection_factory: PostgreSQLConnectionFactory,
        schema_name: str,
    ) -> None:
        """Recibe fabrica de conexiones y schema objetivo."""

        self._connection_factory = connection_factory
        self._schema_name = schema_name

    def prepare_schema(self) -> None:
        """Crea schema y tablas staging requeridas si no existen."""

        ddl_template = (
            files("novitec_dwh.contexts.organizational.infrastructure.sql")
            .joinpath("organizational_staging.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{schema_name}", self._schema_name)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de misma corrida antes de recargar."""

        tables = [
            "stg_organizational_user_permissions",
            "stg_organizational_group_permissions",
            "stg_organizational_user_branches",
            "stg_organizational_users",
            "stg_organizational_access_groups",
            "stg_organizational_roles",
            "stg_organizational_branches",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._schema_name}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def load_branches(self, extraction_id: str, records: list[SucursalPropia]) -> None:
        """Carga sucursales usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_sucursal,
                record.ciudad,
                record.secuencial,
                record.nro_base,
            )
            for record in records
        ]
        self._copy_rows("stg_organizational_branches", SUCURSALES_COLUMNS, rows)

    def load_roles(self, extraction_id: str, records: list[RolUsuario]) -> None:
        """Carga roles usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.rol,
            )
            for record in records
        ]
        self._copy_rows("stg_organizational_roles", ROLES_COLUMNS, rows)

    def load_access_groups(self, extraction_id: str, records: list[GrupoAcceso]) -> None:
        """Carga grupos de acceso usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nombre,
                record.descripcion,
                record.es_superadmin,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_organizational_access_groups", GRUPOS_COLUMNS, rows)

    def load_users(self, extraction_id: str, records: list[UsuarioInterno]) -> None:
        """Carga usuarios internos usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.usuario,
                record.nombre_tecnico,
                record.telefono,
                record.correo_tec,
                record.acceso_nc,
                record.rol_id,
                record.sucursal_id,
                record.activo,
                record.grupo_id,
            )
            for record in records
        ]
        self._copy_rows("stg_organizational_users", USUARIOS_COLUMNS, rows)

    def load_user_branches(self, extraction_id: str, records: list[UsuarioSucursal]) -> None:
        """Carga asignaciones usuario sucursal usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.usuario_id,
                record.sucursal_id,
            )
            for record in records
        ]
        self._copy_rows(
            "stg_organizational_user_branches",
            USUARIOS_SUCURSALES_COLUMNS,
            rows,
        )

    def load_group_permissions(self, extraction_id: str, records: list[PermisoGrupo]) -> None:
        """Carga permisos de grupo usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.grupo_id,
                record.modulo,
                record.accion,
                record.permitido,
            )
            for record in records
        ]
        self._copy_rows(
            "stg_organizational_group_permissions",
            PERMISOS_GRUPO_COLUMNS,
            rows,
        )

    def load_user_permissions(self, extraction_id: str, records: list[PermisoUsuario]) -> None:
        """Carga permisos de usuario usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.usuario_id,
                record.modulo,
                record.accion,
                record.permitido,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows(
            "stg_organizational_user_permissions",
            PERMISOS_USUARIO_COLUMNS,
            rows,
        )

    def _copy_rows(self, table_name: str, columns: list[str], rows: list[tuple]) -> None:
        """Ejecuta carga masiva eficiente hacia PostgreSQL."""

        if not rows:
            return

        columns_sql = ", ".join(columns)
        copy_sql = f"COPY {self._schema_name}.{table_name} ({columns_sql}) FROM STDIN"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                with cursor.copy(copy_sql) as copy:
                    for row in rows:
                        copy.write_row(row)
            connection.commit()
