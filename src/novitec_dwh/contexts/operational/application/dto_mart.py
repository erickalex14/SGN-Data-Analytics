"""DTOs del mart operativo."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OperationalMartLoadSummary:
    """Resume el resultado de la carga del mart operativo."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    ordenes: int = 0
    preordenes: int = 0
    asignaciones_tecnicos: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0
