"""DTOs del contexto financiero."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class FinancialExtractionSummary:
    """Resume el volumen procesado durante una extraccion."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    solicitudes_nc: int = 0
    solicitudes_nc_chunks: int = 0
    precios_orden: int = 0
    precios_orden_chunks: int = 0
    notificaciones: int = 0
    notificaciones_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class FinancialStagingLoadSummary:
    """Resume el resultado de la carga del dominio financiero a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    solicitudes_nc: int = 0
    solicitudes_nc_chunks: int = 0
    precios_orden: int = 0
    precios_orden_chunks: int = 0
    notificaciones: int = 0
    notificaciones_chunks: int = 0
