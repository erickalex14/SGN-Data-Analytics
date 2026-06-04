"""Contratos de aplicacion para el mart financiero."""

from typing import Protocol


class FinancialMartRepository(Protocol):
    """Contrato para construir el mart financiero desde staging."""

    def prepare_schema(self) -> None:
        """Crea o actualiza la estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia los hechos de una corrida previa del mismo identificador."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de fechas necesaria para la corrida."""

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de tecnicos necesaria para la corrida."""

    def load_credit_note_request_fact(self, extraction_id: str) -> int:
        """Carga el hecho de solicitudes de nota de credito."""

    def load_order_price_fact(self, extraction_id: str) -> int:
        """Carga el hecho de precios por orden."""

    def load_credit_note_notification_fact(self, extraction_id: str) -> int:
        """Carga el hecho de notificaciones de notas de credito."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza la auditoria de calidad y devuelve reglas y hallazgos."""
