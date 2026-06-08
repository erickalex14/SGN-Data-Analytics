"""DTOs del mart del dominio de garantias."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class WarrantyMartLoadSummary:
    """Resume el resultado de la construccion del mart de garantias."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    ordenes_personales: int = 0
    ordenes_empresariales: int = 0
    asignaciones_usuario_cas: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0
