"""DTOs del mart del dominio organizacional."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OrganizationalMartLoadSummary:
    """Resume resultado de carga del mart organizacional."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    usuarios: int = 0
    usuarios_sucursales: int = 0
    permisos_grupo: int = 0
    permisos_usuario: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0
