"""Contratos de aplicacion para el mart tecnico."""

from typing import Protocol


class TechnicalMartRepository(Protocol):
    """Contrato para construir el mart tecnico desde staging."""

    def prepare_schema(self) -> None:
        """Crea o actualiza la estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia los hechos de una corrida previa del mismo identificador."""

    def resolve_latest_extraction_id(self) -> str:
        """Obtiene la corrida tecnica mas reciente disponible en staging."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de fechas necesaria para la corrida."""

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de tecnicos necesaria para la corrida."""

    def load_service_type_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de tipos de servicio necesaria para la corrida."""

    def load_brand_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de marcas necesaria para la corrida."""

    def load_report_fact(self, extraction_id: str) -> int:
        """Carga el hecho principal de informes tecnicos."""

    def load_report_photo_fact(self, extraction_id: str) -> int:
        """Carga el hecho de evidencia fotografica."""

    def load_equipment_fact(self, extraction_id: str) -> int:
        """Carga el hecho de equipos intervenidos."""

    def load_equipment_access_fact(self, extraction_id: str) -> int:
        """Carga el hecho de accesos proporcionados por el cliente."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza la auditoria de calidad y devuelve reglas y hallazgos."""
