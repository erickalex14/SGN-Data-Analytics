"""Repositorio PostgreSQL para la carga del dominio de inventario a staging."""

from importlib.resources import files
from typing import Final

from novitec_dwh.contexts.inventory.domain.entities import (
    ListaCompra,
    OrdenRepuesto,
    ProductoInventario,
    Repuesto,
    SolicitudRepuesto,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

REPUESTOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "codigo",
    "nro_parte",
    "nombre",
    "descripcion",
    "marca_id",
    "tipo_dispositivo_id",
    "creado_en",
    "modificado_en",
    "stock",
    "costo",
    "bodega",
]

PRODUCTOSINVENTARIO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "codigo",
    "descripcion",
    "marca_id",
    "tipo_dispositivo_id",
    "tipo_dispositivo_codigo",
]

ORDEN_REPUESTOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "orden_id",
    "repuesto_id",
    "cantidad",
    "fecha",
    "usuario_id",
]

SOLICITUDESREPUESTO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_solicitud",
    "orden_id",
    "tecnico_id",
    "tecnico_nombre",
    "repuesto_nombre",
    "nro_parte",
    "nro_parte_inv_id",
    "repuesto_codigo",
    "repuesto_inv_id",
    "link_compra",
    "cantidad",
    "descripcion",
    "estado",
    "motivo_rechazo",
    "aprobado_por",
    "repuesto_id",
    "lista_compra_id",
    "fecha_solicitud",
    "fecha_gestion",
    "created_at",
]

LISTASCOMPRA_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_lista",
    "creado_por",
    "creado_por_id",
    "fecha_creacion",
    "estado",
    "observacion",
    "created_at",
]


class PostgreSQLInventoryStagingRepository:
    """Gestiona la persistencia staging del dominio de inventario en PostgreSQL."""

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
            files("novitec_dwh.contexts.inventory.infrastructure.sql")
            .joinpath("inventory_staging.sql")
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
            "stg_inventory_purchase_lists",
            "stg_inventory_spare_part_requests",
            "stg_inventory_order_spare_parts",
            "stg_inventory_products",
            "stg_inventory_spare_parts",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._schema_name}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def load_spare_parts(self, extraction_id: str, records: list[Repuesto]) -> None:
        """Carga repuestos usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.codigo,
                record.nro_parte,
                record.nombre,
                record.descripcion,
                record.marca_id,
                record.tipo_dispositivo_id,
                record.creado_en,
                record.modificado_en,
                record.stock,
                record.costo,
                record.bodega,
            )
            for record in records
        ]
        self._copy_rows("stg_inventory_spare_parts", REPUESTOS_COLUMNS, rows)

    def load_inventory_products(
        self,
        extraction_id: str,
        records: list[ProductoInventario],
    ) -> None:
        """Carga productos de inventario usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.codigo,
                record.descripcion,
                record.marca_id,
                record.tipo_dispositivo_id,
                record.tipo_dispositivo_codigo,
            )
            for record in records
        ]
        self._copy_rows("stg_inventory_products", PRODUCTOSINVENTARIO_COLUMNS, rows)

    def load_order_spare_parts(
        self,
        extraction_id: str,
        records: list[OrdenRepuesto],
    ) -> None:
        """Carga repuestos instalados por orden usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.orden_id,
                record.repuesto_id,
                record.cantidad,
                record.fecha,
                record.usuario_id,
            )
            for record in records
        ]
        self._copy_rows("stg_inventory_order_spare_parts", ORDEN_REPUESTOS_COLUMNS, rows)

    def load_spare_part_requests(
        self,
        extraction_id: str,
        records: list[SolicitudRepuesto],
    ) -> None:
        """Carga solicitudes de repuesto usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_solicitud,
                record.orden_id,
                record.tecnico_id,
                record.tecnico_nombre,
                record.repuesto_nombre,
                record.nro_parte,
                record.nro_parte_inv_id,
                record.repuesto_codigo,
                record.repuesto_inv_id,
                record.link_compra,
                record.cantidad,
                record.descripcion,
                record.estado,
                record.motivo_rechazo,
                record.aprobado_por,
                record.repuesto_id,
                record.lista_compra_id,
                record.fecha_solicitud,
                record.fecha_gestion,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_inventory_spare_part_requests", SOLICITUDESREPUESTO_COLUMNS, rows)

    def load_purchase_lists(self, extraction_id: str, records: list[ListaCompra]) -> None:
        """Carga listas de compra usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_lista,
                record.creado_por,
                record.creado_por_id,
                record.fecha_creacion,
                record.estado,
                record.observacion,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_inventory_purchase_lists", LISTASCOMPRA_COLUMNS, rows)

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
