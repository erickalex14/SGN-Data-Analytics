"""Contratos del proceso de vistas semanticas."""

from typing import Protocol


class SemanticViewsRepository(Protocol):
    """Define operaciones para publicar vistas semanticas en PostgreSQL."""

    def publish_views(self) -> int:
        """Crea o actualiza las vistas semanticas y devuelve el total publicado."""
