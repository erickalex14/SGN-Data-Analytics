"""DTOs del mart tecnico."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TechnicalMartLoadSummary:
    """Resume el resultado de la carga del mart tecnico."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    informes: int = 0
    fotos_informes: int = 0
    equipos: int = 0
    accesos_equipos: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0
