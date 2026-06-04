"""DTOs del contexto operativo."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OperationalExtractionSummary:
    """Resume el volumen procesado durante una extraccion operativa."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    vista_ordenes: int = 0
    vista_ordenes_chunks: int = 0
    ordenes: int = 0
    ordenes_chunks: int = 0
    ordenes_empresas: int = 0
    ordenes_empresas_chunks: int = 0
    preordenes: int = 0
    preordenes_chunks: int = 0
    orden_empresa_tecnicos: int = 0
    orden_empresa_tecnicos_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None
