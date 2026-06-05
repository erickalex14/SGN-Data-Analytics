"""Contratos de aplicacion para la carga tecnica a staging."""

from collections.abc import Iterator
from pathlib import Path
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


class TechnicalRawReader(Protocol):
    """Contrato para leer datasets tecnicos desde la zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida la corrida raw objetivo."""

    def read_reports(self) -> Iterator[list[InformeTecnico]]:
        """Lee informes tecnicos desde raw por lotes."""

    def read_report_photo_metadata(self) -> Iterator[list[InformeFotoMetadata]]:
        """Lee metadatos de fotos de informes desde raw por lotes."""

    def read_equipment(self) -> Iterator[list[EquipoTecnico]]:
        """Lee equipos desde raw por lotes."""

    def read_equipment_series(self) -> Iterator[list[EquipoSerie]]:
        """Lee series de equipos desde raw por lotes."""

    def read_device_types(self) -> Iterator[list[TipoDispositivo]]:
        """Lee tipos de dispositivo desde raw por lotes."""

    def read_service_types(self) -> Iterator[list[TipoServicio]]:
        """Lee tipos de servicio desde raw por lotes."""

    def read_brands(self) -> Iterator[list[Marca]]:
        """Lee marcas desde raw por lotes."""

    def read_equipment_credentials_metadata(
        self,
    ) -> Iterator[list[CredencialEquipoMetadata]]:
        """Lee metadatos de credenciales de equipo desde raw por lotes."""


class TechnicalStagingRepository(Protocol):
    """Contrato para persistir el dominio tecnico en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura tecnica requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa el estado necesario para una corrida concreta."""

    def load_reports(self, extraction_id: str, records: list[InformeTecnico]) -> None:
        """Carga informes tecnicos en staging."""

    def load_report_photo_metadata(
        self,
        extraction_id: str,
        records: list[InformeFotoMetadata],
    ) -> None:
        """Carga metadatos de fotos de informes en staging."""

    def load_equipment(self, extraction_id: str, records: list[EquipoTecnico]) -> None:
        """Carga equipos en staging."""

    def load_equipment_series(self, extraction_id: str, records: list[EquipoSerie]) -> None:
        """Carga series de equipos en staging."""

    def load_device_types(self, extraction_id: str, records: list[TipoDispositivo]) -> None:
        """Carga tipos de dispositivo en staging."""

    def load_service_types(self, extraction_id: str, records: list[TipoServicio]) -> None:
        """Carga tipos de servicio en staging."""

    def load_brands(self, extraction_id: str, records: list[Marca]) -> None:
        """Carga marcas en staging."""

    def load_equipment_credentials_metadata(
        self,
        extraction_id: str,
        records: list[CredencialEquipoMetadata],
    ) -> None:
        """Carga metadatos de credenciales de equipo en staging."""
