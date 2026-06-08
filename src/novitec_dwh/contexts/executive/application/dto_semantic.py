"""DTOs del proceso de publicacion de vistas semanticas."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SemanticViewsBuildSummary:
    """Resume la publicacion de vistas semanticas para Power BI."""

    semantic_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    published_views: int = 0
