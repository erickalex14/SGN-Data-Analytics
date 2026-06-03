"""Contratos de aplicacion para la carga financiera a staging."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)


class FinancialRawReader(Protocol):
    """Contrato para leer datasets financieros desde la zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida la corrida raw objetivo."""

    def read_credit_note_requests(self) -> Iterator[list[SolicitudNotaCredito]]:
        """Lee solicitudes de nota de credito desde raw por lotes."""

    def read_order_prices(self) -> Iterator[list[PrecioOrden]]:
        """Lee precios por orden desde raw por lotes."""

    def read_credit_note_notifications(self) -> Iterator[list[NotificacionNotaCredito]]:
        """Lee notificaciones de nota de credito desde raw por lotes."""


class FinancialStagingRepository(Protocol):
    """Contrato para persistir el dominio financiero en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura tecnica requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa el estado necesario para una corrida concreta."""

    def load_credit_note_requests(
        self,
        extraction_id: str,
        records: list[SolicitudNotaCredito],
    ) -> None:
        """Carga solicitudes de nota de credito en staging."""

    def load_order_prices(self, extraction_id: str, records: list[PrecioOrden]) -> None:
        """Carga precios por orden en staging."""

    def load_credit_note_notifications(
        self,
        extraction_id: str,
        records: list[NotificacionNotaCredito],
    ) -> None:
        """Carga notificaciones de nota de credito en staging."""
