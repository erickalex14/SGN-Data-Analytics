"""Contratos de aplicacion del contexto organizacional."""

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Protocol


class OrganizationalExtractionSink(Protocol):
    """Define contrato de persistencia de extraccion organizacional."""

    @property
    def run_directory(self) -> Path | None:
        """Expone carpeta base generada para corrida actual."""

    @property
    def manifest_path(self) -> Path | None:
        """Expone ruta del manifiesto final de corrida."""

    def start(self, extraction_id: str, started_at: datetime) -> None:
        """Inicializa recursos necesarios para nueva corrida."""

    def write(self, dataset_name: str, chunk_number: int, records: Sequence[object]) -> Path:
        """Persiste lote de registros y devuelve ruta generada."""

    def finalize(self, summary: object) -> None:
        """Cierra corrida y persiste manifiesto final."""
