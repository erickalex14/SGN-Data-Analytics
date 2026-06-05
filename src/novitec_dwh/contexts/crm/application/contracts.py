"""Contratos de aplicacion del contexto CRM."""

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol


class CrmExtractionSink(Protocol):
    """Define el contrato de persistencia de la extraccion CRM."""

    @property
    def run_directory(self) -> Path | None:
        """Expone la carpeta base generada para la corrida actual."""

    @property
    def manifest_path(self) -> Path | None:
        """Expone la ruta del manifiesto final de la corrida."""

    def start(self, extraction_id: str, started_at: datetime) -> None:
        """Inicializa los recursos necesarios para una nueva corrida."""

    def write(self, dataset_name: str, chunk_number: int, records: Sequence[object]) -> Path:
        """Persiste un lote de registros y devuelve la ruta del archivo generado."""

    def finalize(self, summary: object) -> None:
        """Cierra la corrida y persiste el manifiesto final."""
