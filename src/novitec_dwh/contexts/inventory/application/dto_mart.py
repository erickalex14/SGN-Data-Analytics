"""DTOs del mart de inventario."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class InventoryMartLoadSummary:
    """Resume el resultado de la carga del mart de inventario."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    repuestos: int = 0
    consumos_orden: int = 0
    solicitudes_repuesto: int = 0
    listas_compra: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0
