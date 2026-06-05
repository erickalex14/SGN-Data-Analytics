"""Contratos de aplicacion para el mart de inventario."""

from typing import Protocol


class InventoryMartRepository(Protocol):
    """Contrato para construir el mart de inventario desde staging."""

    def prepare_schema(self) -> None:
        """Crea o actualiza la estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia los hechos de una corrida previa del mismo identificador."""

    def resolve_latest_extraction_id(self) -> str:
        """Obtiene la corrida de inventario mas reciente disponible en staging."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de fechas necesaria para la corrida."""

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de tecnicos necesaria para la corrida."""

    def load_spare_part_dimension(self, extraction_id: str) -> None:
        """Carga la dimension de repuestos necesaria para la corrida."""

    def load_spare_part_fact(self, extraction_id: str) -> int:
        """Carga el hecho principal de repuestos."""

    def load_order_consumption_fact(self, extraction_id: str) -> int:
        """Carga el hecho de consumo de repuestos por orden."""

    def load_spare_part_request_fact(self, extraction_id: str) -> int:
        """Carga el hecho de solicitudes de repuesto."""

    def load_purchase_list_fact(self, extraction_id: str) -> int:
        """Carga el hecho de listas de compra."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza la auditoria de calidad y devuelve reglas y hallazgos."""
