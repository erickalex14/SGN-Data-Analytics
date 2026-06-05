"""Repositorio PostgreSQL para la carga del dominio CRM a staging."""

from importlib.resources import files
from typing import Final

from novitec_dwh.contexts.crm.domain.entities import Cliente, Empresa, SucursalCliente
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

CLIENTES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nombres",
    "apellidos",
    "identificacion",
    "numero_contacto",
    "correo",
    "direccion_clientes",
]

EMPRESAS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nombre",
    "ruc",
    "telefono",
    "correo",
    "direccion_empresa",
    "created_at",
]

SUCURSALESCLIENTE_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "codigo",
    "numero",
    "nombre",
    "provincia",
    "novitec_sucursal",
    "activa",
    "created_at",
]


class PostgreSQLCrmStagingRepository:
    """Gestiona la persistencia staging del dominio CRM en PostgreSQL."""

    def __init__(
        self,
        connection_factory: PostgreSQLConnectionFactory,
        schema_name: str,
    ) -> None:
        """Recibe la fabrica de conexiones y el schema objetivo."""

        self._connection_factory = connection_factory
        self._schema_name = schema_name

    def prepare_schema(self) -> None:
        """Crea el schema y las tablas staging requeridas si no existen."""

        ddl_template = (
            files("novitec_dwh.contexts.crm.infrastructure.sql")
            .joinpath("crm_staging.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{schema_name}", self._schema_name)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de la misma corrida antes de recargarla."""

        tables = [
            "stg_crm_customer_branches",
            "stg_crm_companies",
            "stg_crm_customers",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._schema_name}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def load_customers(self, extraction_id: str, records: list[Cliente]) -> None:
        """Carga clientes usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nombres,
                record.apellidos,
                record.identificacion,
                record.numero_contacto,
                record.correo,
                record.direccion_clientes,
            )
            for record in records
        ]
        self._copy_rows("stg_crm_customers", CLIENTES_COLUMNS, rows)

    def load_companies(self, extraction_id: str, records: list[Empresa]) -> None:
        """Carga empresas usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nombre,
                record.ruc,
                record.telefono,
                record.correo,
                record.direccion_empresa,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_crm_companies", EMPRESAS_COLUMNS, rows)

    def load_customer_branches(
        self,
        extraction_id: str,
        records: list[SucursalCliente],
    ) -> None:
        """Carga sucursales cliente usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.codigo,
                record.numero,
                record.nombre,
                record.provincia,
                record.novitec_sucursal,
                record.activa,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_crm_customer_branches", SUCURSALESCLIENTE_COLUMNS, rows)

    def _copy_rows(self, table_name: str, columns: list[str], rows: list[tuple]) -> None:
        """Ejecuta una carga masiva eficiente hacia PostgreSQL."""

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
