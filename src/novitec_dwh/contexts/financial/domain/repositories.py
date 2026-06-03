"""Contratos del dominio financiero."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)


class FinancialExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio financiero."""

    def extract_credit_note_requests(
        self,
        chunk_size: int,
    ) -> Iterator[list[SolicitudNotaCredito]]:
        """Extrae solicitudes de nota de credito por lotes."""

    def extract_order_prices(self, chunk_size: int) -> Iterator[list[PrecioOrden]]:
        """Extrae precios facturados por orden en lotes."""

    def extract_credit_note_notifications(
        self,
        chunk_size: int,
    ) -> Iterator[list[NotificacionNotaCredito]]:
        """Extrae notificaciones vinculadas a notas de credito por lotes."""
