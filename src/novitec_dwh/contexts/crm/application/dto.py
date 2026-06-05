"""DTOs del contexto CRM."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CrmExtractionSummary:
    """Resume el volumen procesado durante una extraccion CRM."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    clientes: int = 0
    clientes_chunks: int = 0
    empresas: int = 0
    empresas_chunks: int = 0
    sucursalescliente: int = 0
    sucursalescliente_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class CrmStagingLoadSummary:
    """Resume el resultado de la carga del dominio CRM a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    clientes: int = 0
    clientes_chunks: int = 0
    empresas: int = 0
    empresas_chunks: int = 0
    sucursalescliente: int = 0
    sucursalescliente_chunks: int = 0
