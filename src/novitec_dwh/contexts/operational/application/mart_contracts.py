"""Contratos de aplicacion para el mart operativo."""

from typing import Protocol


class OperationalMartRepository(Protocol):
    """Contrato para construir el mart operativo desde staging."""

    def prepare_schema(self) -> None:
        """Crea o actualiza la estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia los hechos de una corrida previa del mismo identificador."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de fechas necesaria para la corrida."""

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de tecnicos necesaria para la corrida."""

    def load_branch_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de sucursales necesaria para la corrida."""

    def load_order_fact(self, extraction_id: str) -> int:
        """Carga el hecho principal de ordenes."""

    def load_preorder_fact(self, extraction_id: str) -> int:
        """Carga el hecho de preordenes."""

    def load_company_order_assignment_fact(self, extraction_id: str) -> int:
        """Carga el hecho de asignaciones tecnico-orden empresarial."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza la auditoria de calidad y devuelve reglas y hallazgos."""
