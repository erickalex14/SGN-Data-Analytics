"""Modelos base reutilizables del dominio."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AuditMetadata:
    """Representa metadatos comunes de trazabilidad."""

    created_at: datetime | None = None
    updated_at: datetime | None = None
