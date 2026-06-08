"""DTOs del contexto de garantias."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class WarrantyExtractionSummary:
    """Resume el volumen procesado durante una extraccion de garantias."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    cas: int = 0
    cas_chunks: int = 0
    usuariocas: int = 0
    usuariocas_chunks: int = 0
    ordenes_garantia: int = 0
    ordenes_garantia_chunks: int = 0
    ordenesempresas_garantia: int = 0
    ordenesempresas_garantia_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class WarrantyStagingLoadSummary:
    """Resume el resultado de la carga del dominio de garantias a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    cas: int = 0
    cas_chunks: int = 0
    usuariocas: int = 0
    usuariocas_chunks: int = 0
    ordenes_garantia: int = 0
    ordenes_garantia_chunks: int = 0
    ordenesempresas_garantia: int = 0
    ordenesempresas_garantia_chunks: int = 0
