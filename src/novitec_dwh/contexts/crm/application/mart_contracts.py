"""Contratos de aplicacion para el mart CRM."""

from typing import Protocol


class CrmMartRepository(Protocol):
    """Contrato para construir el mart CRM desde staging."""

    def prepare_schema(self) -> None:
        """Crea o actualiza la estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia los hechos de una corrida previa del mismo identificador."""

    def resolve_latest_extraction_id(self) -> str:
        """Obtiene la corrida CRM mas reciente disponible en staging."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de fechas necesaria para la corrida."""

    def load_customer_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de clientes necesaria para la corrida."""

    def load_company_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de empresas necesaria para la corrida."""

    def load_customer_fact(self, extraction_id: str) -> int:
        """Carga el hecho de clientes."""

    def load_company_fact(self, extraction_id: str) -> int:
        """Carga el hecho de empresas."""

    def load_customer_branch_fact(self, extraction_id: str) -> int:
        """Carga el hecho de sucursales cliente."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza la auditoria de calidad y devuelve reglas y hallazgos."""
