"""Caso de uso para publicar vistas semanticas de Power BI."""

from datetime import datetime
import logging

from novitec_dwh.contexts.executive.application.dto_semantic import (
    SemanticViewsBuildSummary,
)
from novitec_dwh.contexts.executive.application.semantic_contracts import (
    SemanticViewsRepository,
)

logger = logging.getLogger(__name__)


class BuildSemanticViewsUseCase:
    """Coordina la publicacion de vistas semanticas para consumo BI."""

    def __init__(self, repository: SemanticViewsRepository, semantic_schema: str) -> None:
        """Recibe el repositorio encargado de materializar las vistas."""

        self._repository = repository
        self._semantic_schema = semantic_schema

    def execute(self) -> SemanticViewsBuildSummary:
        """Publica las vistas semanticas y devuelve un resumen del proceso."""

        started_at = datetime.now()
        logger.info(
            "Inicio de publicacion de vistas semanticas para Power BI. Schema: %s.",
            self._semantic_schema,
        )

        published_views = self._repository.publish_views()

        summary = SemanticViewsBuildSummary(
            semantic_schema=self._semantic_schema,
            started_at=started_at,
            finished_at=datetime.now(),
            published_views=published_views,
        )
        logger.info(
            "Vistas semanticas publicadas correctamente. Schema: %s | Vistas: %s.",
            summary.semantic_schema,
            summary.published_views,
        )
        return summary
