"""Protocolos compartidos entre capa de aplicacion e infraestructura."""

from collections.abc import Iterator
from typing import Protocol, TypeVar

EntityType = TypeVar("EntityType")


class ChunkExtractor(Protocol[EntityType]):
    """Define un contrato generico de extraccion paginada por lotes."""

    def extract(self, chunk_size: int) -> Iterator[list[EntityType]]:
        """Extrae entidades en bloques controlados para optimizar memoria."""
