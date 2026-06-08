"""Contratos de aplicacion para el mart de garantias."""

from typing import Protocol


class WarrantyMartRepository(Protocol):
    """Contrato para construir el mart de garantias desde staging."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia la informacion previa de una corrida concreta."""

    def resolve_latest_extraction_id(self) -> str:
        """Obtiene la corrida mas reciente disponible en staging."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de fechas necesaria para la corrida."""

    def load_service_center_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de centros autorizados de servicio."""

    def load_user_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de usuarios y tecnicos asociados al dominio."""

    def load_personal_order_fact(self, extraction_id: str) -> int:
        """Carga el hecho de ordenes personales con garantia."""

    def load_company_order_fact(self, extraction_id: str) -> int:
        """Carga el hecho de ordenes empresariales con CAS."""

    def load_user_assignment_fact(self, extraction_id: str) -> int:
        """Carga el hecho de asignaciones entre usuarios y CAS."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza la auditoria de calidad y devuelve reglas y hallazgos."""
