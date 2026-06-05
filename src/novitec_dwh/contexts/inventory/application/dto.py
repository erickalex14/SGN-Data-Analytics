"""DTOs del contexto de inventario."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class InventoryExtractionSummary:
    """Resume el volumen procesado durante una extraccion de inventario."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    repuestos: int = 0
    repuestos_chunks: int = 0
    productosinventario: int = 0
    productosinventario_chunks: int = 0
    orden_repuestos: int = 0
    orden_repuestos_chunks: int = 0
    solicitudesrepuesto: int = 0
    solicitudesrepuesto_chunks: int = 0
    listascompra: int = 0
    listascompra_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class InventoryStagingLoadSummary:
    """Resume el resultado de la carga del dominio de inventario a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    repuestos: int = 0
    repuestos_chunks: int = 0
    productosinventario: int = 0
    productosinventario_chunks: int = 0
    orden_repuestos: int = 0
    orden_repuestos_chunks: int = 0
    solicitudesrepuesto: int = 0
    solicitudesrepuesto_chunks: int = 0
    listascompra: int = 0
    listascompra_chunks: int = 0
