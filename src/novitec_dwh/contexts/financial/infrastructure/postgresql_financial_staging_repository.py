"""Repositorio PostgreSQL para la carga del dominio financiero a staging."""

from importlib.resources import files
from typing import Final

from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

SOLICITUDES_NC_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_solicitud",
    "orden_id",
    "nro_orden",
    "fecha_solicitud",
    "asunto",
    "detalles",
    "nombre_admin",
    "motivo_rechazo",
    "tecnico_nombre",
    "tecnico_id",
    "estado",
    "creado_en",
    "created_at",
]

PRECIOS_ORDEN_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "orden_id",
    "nro_orden",
    "precio_estandar_id",
    "servicio",
    "precio",
    "descripcion",
    "creado_en",
    "servicio_estandar",
    "precio_estandar",
]

NOTIFICACIONES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "usuario_id",
    "usuario_nombre",
    "tipo",
    "mensaje",
    "nc_id",
    "orden_id",
    "nro_orden",
    "leida",
    "created_at",
]


class PostgreSQLFinancialStagingRepository:
    """Gestiona la persistencia staging del dominio financiero en PostgreSQL."""

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
            files("novitec_dwh.contexts.financial.infrastructure.sql")
            .joinpath("financial_staging.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{schema_name}", self._schema_name)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de la misma corrida antes de recargarla."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {self._schema_name}.stg_financial_credit_note_notifications
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
                cursor.execute(
                    f"""
                    DELETE FROM {self._schema_name}.stg_financial_order_prices
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
                cursor.execute(
                    f"""
                    DELETE FROM {self._schema_name}.stg_financial_credit_note_requests
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
            connection.commit()

    def load_credit_note_requests(
        self,
        extraction_id: str,
        records: list[SolicitudNotaCredito],
    ) -> None:
        """Carga solicitudes de nota de credito usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_solicitud,
                record.orden_id,
                record.nro_orden,
                record.fecha_solicitud,
                record.asunto,
                record.detalles,
                record.nombre_admin,
                record.motivo_rechazo,
                record.tecnico_nombre,
                record.tecnico_id,
                record.estado,
                record.creado_en,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows(
            table_name="stg_financial_credit_note_requests",
            columns=SOLICITUDES_NC_COLUMNS,
            rows=rows,
        )

    def load_order_prices(self, extraction_id: str, records: list[PrecioOrden]) -> None:
        """Carga precios por orden usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.orden_id,
                record.nro_orden,
                record.precio_estandar_id,
                record.servicio,
                record.precio,
                record.descripcion,
                record.creado_en,
                record.servicio_estandar,
                record.precio_estandar,
            )
            for record in records
        ]
        self._copy_rows(
            table_name="stg_financial_order_prices",
            columns=PRECIOS_ORDEN_COLUMNS,
            rows=rows,
        )

    def load_credit_note_notifications(
        self,
        extraction_id: str,
        records: list[NotificacionNotaCredito],
    ) -> None:
        """Carga notificaciones de nota de credito usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.usuario_id,
                record.usuario_nombre,
                record.tipo,
                record.mensaje,
                record.nc_id,
                record.orden_id,
                record.nro_orden,
                record.leida,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows(
            table_name="stg_financial_credit_note_notifications",
            columns=NOTIFICACIONES_COLUMNS,
            rows=rows,
        )

    def _copy_rows(self, table_name: str, columns: list[str], rows: list[tuple]) -> None:
        """Ejecuta una carga masiva eficiente hacia PostgreSQL."""

        if not rows:
            return

        columns_sql = ", ".join(columns)
        copy_sql = (
            f"COPY {self._schema_name}.{table_name} ({columns_sql}) "
            "FROM STDIN"
        )

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                with cursor.copy(copy_sql) as copy:
                    for row in rows:
                        copy.write_row(row)
            connection.commit()
