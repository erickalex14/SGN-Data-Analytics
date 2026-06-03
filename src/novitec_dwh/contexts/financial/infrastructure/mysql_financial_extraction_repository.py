"""Repositorio MySQL para la extraccion del dominio financiero."""

from collections.abc import Iterator

from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLFinancialExtractionRepository:
    """Implementa la extraccion financiera desde el origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe la fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_credit_note_requests(
        self,
        chunk_size: int,
    ) -> Iterator[list[SolicitudNotaCredito]]:
        """Extrae solicitudes de nota de credito enriquecidas con la orden."""

        query = """
            SELECT
                sn.id,
                sn.nro_solicitud,
                sn.orden_id,
                o.nro_orden,
                sn.fecha_solicitud,
                sn.asunto,
                sn.detalles,
                sn.nombre_admin,
                sn.motivo_rechazo,
                sn.tecnico_nombre,
                sn.tecnico_id,
                sn.estado,
                sn.creado_en,
                sn.created_at
            FROM solicitudesnc sn
            INNER JOIN ordenes o
                ON o.id = sn.orden_id
            ORDER BY sn.id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [SolicitudNotaCredito(**row) for row in rows]

    def extract_order_prices(self, chunk_size: int) -> Iterator[list[PrecioOrden]]:
        """Extrae precios por orden con referencia al catalogo estandar."""

        query = """
            SELECT
                po.id,
                po.orden_id,
                o.nro_orden,
                po.precio_estandar_id,
                po.servicio,
                po.precio,
                po.descripcion,
                po.creado_en,
                pe.servicio AS servicio_estandar,
                pe.precio AS precio_estandar
            FROM preciosorden po
            INNER JOIN ordenes o
                ON o.id = po.orden_id
            LEFT JOIN preciosestandar pe
                ON pe.id = po.precio_estandar_id
            ORDER BY po.id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [PrecioOrden(**row) for row in rows]

    def extract_credit_note_notifications(
        self,
        chunk_size: int,
    ) -> Iterator[list[NotificacionNotaCredito]]:
        """Extrae notificaciones asociadas al flujo de notas de credito."""

        query = """
            SELECT
                n.id,
                n.usuario_id,
                u.nombre_tecnico AS usuario_nombre,
                n.tipo,
                n.mensaje,
                n.nc_id,
                n.orden_id,
                n.nro_orden,
                n.leida,
                n.created_at
            FROM notificaciones n
            LEFT JOIN usuarios u
                ON u.id = n.usuario_id
            WHERE n.tipo IN ('nc_solicitud', 'nc_aprobada', 'nc_rechazada')
            ORDER BY n.id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [NotificacionNotaCredito(**row) for row in rows]
