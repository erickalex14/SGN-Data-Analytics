"""DTOs del contexto tecnico."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TechnicalExtractionSummary:
    """Resume el volumen procesado durante una extraccion tecnica."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    informes: int = 0
    informes_chunks: int = 0
    informefotos: int = 0
    informefotos_chunks: int = 0
    equipos: int = 0
    equipos_chunks: int = 0
    equiposseries: int = 0
    equiposseries_chunks: int = 0
    tiposdispositivo: int = 0
    tiposdispositivo_chunks: int = 0
    tiposservicio: int = 0
    tiposservicio_chunks: int = 0
    marcas: int = 0
    marcas_chunks: int = 0
    credencialesequipo: int = 0
    credencialesequipo_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class TechnicalStagingLoadSummary:
    """Resume el resultado de la carga del dominio tecnico a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    informes: int = 0
    informes_chunks: int = 0
    informefotos: int = 0
    informefotos_chunks: int = 0
    equipos: int = 0
    equipos_chunks: int = 0
    equiposseries: int = 0
    equiposseries_chunks: int = 0
    tiposdispositivo: int = 0
    tiposdispositivo_chunks: int = 0
    tiposservicio: int = 0
    tiposservicio_chunks: int = 0
    marcas: int = 0
    marcas_chunks: int = 0
    credencialesequipo: int = 0
    credencialesequipo_chunks: int = 0
