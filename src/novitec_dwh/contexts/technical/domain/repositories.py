"""Contratos del dominio tecnico."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.technical.domain.entities import (
    CredencialEquipoMetadata,
    EquipoSerie,
    EquipoTecnico,
    InformeFotoMetadata,
    InformeTecnico,
    Marca,
    TipoDispositivo,
    TipoServicio,
)


class TechnicalExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio tecnico."""

    def extract_reports(self, chunk_size: int) -> Iterator[list[InformeTecnico]]:
        """Extrae informes tecnicos por lotes."""

    def extract_report_photo_metadata(self, chunk_size: int) -> Iterator[list[InformeFotoMetadata]]:
        """Extrae metadatos de fotos de informes por lotes."""

    def extract_equipment(self, chunk_size: int) -> Iterator[list[EquipoTecnico]]:
        """Extrae el maestro de equipos por lotes."""

    def extract_equipment_series(self, chunk_size: int) -> Iterator[list[EquipoSerie]]:
        """Extrae series adicionales de equipos por lotes."""

    def extract_device_types(self, chunk_size: int) -> Iterator[list[TipoDispositivo]]:
        """Extrae tipos de dispositivo por lotes."""

    def extract_service_types(self, chunk_size: int) -> Iterator[list[TipoServicio]]:
        """Extrae tipos de servicio por lotes."""

    def extract_brands(self, chunk_size: int) -> Iterator[list[Marca]]:
        """Extrae marcas por lotes."""

    def extract_equipment_credentials_metadata(
        self,
        chunk_size: int,
    ) -> Iterator[list[CredencialEquipoMetadata]]:
        """Extrae metadatos de acceso de equipos sin contrasenas."""
