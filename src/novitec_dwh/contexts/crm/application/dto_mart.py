"""DTOs del mart CRM."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class CrmMartLoadSummary:
    """Resume el resultado de la carga del mart CRM."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    clientes: int = 0
    empresas: int = 0
    sucursalescliente: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0
