"""Repositorio MySQL para la extraccion del dominio de inventario."""

from collections.abc import Iterator

from novitec_dwh.contexts.inventory.domain.entities import (
    ListaCompra,
    OrdenRepuesto,
    ProductoInventario,
    Repuesto,
    SolicitudRepuesto,
)
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLInventoryExtractionRepository:
    """Implementa la extraccion de inventario desde el origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe la fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_spare_parts(self, chunk_size: int) -> Iterator[list[Repuesto]]:
        """Extrae el catalogo maestro de repuestos para analitica de materiales."""

        query = """
            SELECT
                id,
                codigo,
                nro_parte,
                nombre,
                descripcion,
                marca_id,
                tipo_dispositivo_id,
                creado_en,
                modificado_en,
                stock,
                costo,
                bodega
            FROM repuestos
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [Repuesto(**row) for row in rows]

    def extract_inventory_products(self, chunk_size: int) -> Iterator[list[ProductoInventario]]:
        """Extrae el catalogo clasificador de productos de inventario."""

        query = """
            SELECT
                id,
                codigo,
                descripcion,
                marca_id,
                tipo_dispositivo_id,
                tipo_dispositivo_codigo
            FROM productosinventario
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [ProductoInventario(**row) for row in rows]

    def extract_order_spare_parts(self, chunk_size: int) -> Iterator[list[OrdenRepuesto]]:
        """Extrae los repuestos consumidos dentro de las ordenes tecnicas."""

        query = """
            SELECT
                id,
                orden_id,
                repuesto_id,
                cantidad,
                fecha,
                usuario_id
            FROM orden_repuestos
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [OrdenRepuesto(**row) for row in rows]

    def extract_spare_part_requests(self, chunk_size: int) -> Iterator[list[SolicitudRepuesto]]:
        """Extrae solicitudes de repuestos pendientes o ya gestionadas."""

        query = """
            SELECT
                id,
                nro_solicitud,
                orden_id,
                tecnico_id,
                tecnico_nombre,
                repuesto_nombre,
                nro_parte,
                nro_parte_inv_id,
                repuesto_codigo,
                repuesto_inv_id,
                link_compra,
                cantidad,
                descripcion,
                estado,
                motivo_rechazo,
                aprobado_por,
                repuesto_id,
                lista_compra_id,
                fecha_solicitud,
                fecha_gestion,
                created_at
            FROM solicitudesrepuesto
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [SolicitudRepuesto(**row) for row in rows]

    def extract_purchase_lists(self, chunk_size: int) -> Iterator[list[ListaCompra]]:
        """Extrae listas de compra consolidadas para abastecimiento."""

        query = """
            SELECT
                id,
                nro_lista,
                creado_por,
                creado_por_id,
                fecha_creacion,
                estado,
                observacion,
                created_at
            FROM listascompra
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [ListaCompra(**row) for row in rows]
