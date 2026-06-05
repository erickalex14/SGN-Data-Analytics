"""Caso de uso para cargar el dominio tecnico hacia staging PostgreSQL."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.technical.application.dto import TechnicalStagingLoadSummary
from novitec_dwh.contexts.technical.application.staging_contracts import (
    TechnicalRawReader,
    TechnicalStagingRepository,
)

logger = logging.getLogger(__name__)


class LoadTechnicalToStagingUseCase:
    """Orquesta la carga de datasets tecnicos desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: TechnicalRawReader,
        staging_repository: TechnicalStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe los adaptadores necesarios para leer y cargar la corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> TechnicalStagingLoadSummary:
        """Ejecuta la carga completa del dominio tecnico en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = TechnicalStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga tecnica a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_reports(), start=1):
            self._staging_repository.load_reports(extraction_id=extraction_id, records=chunk)
            summary.informes += len(chunk)
            summary.informes_chunks += 1
            logger.info(
                "Lote %s de informes tecnicos cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_report_photo_metadata(), start=1):
            self._staging_repository.load_report_photo_metadata(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.informefotos += len(chunk)
            summary.informefotos_chunks += 1
            logger.info(
                "Lote %s de metadatos de fotos cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_equipment(), start=1):
            self._staging_repository.load_equipment(extraction_id=extraction_id, records=chunk)
            summary.equipos += len(chunk)
            summary.equipos_chunks += 1
            logger.info(
                "Lote %s de equipos cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_equipment_series(), start=1):
            self._staging_repository.load_equipment_series(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.equiposseries += len(chunk)
            summary.equiposseries_chunks += 1
            logger.info(
                "Lote %s de series de equipos cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_device_types(), start=1):
            self._staging_repository.load_device_types(extraction_id=extraction_id, records=chunk)
            summary.tiposdispositivo += len(chunk)
            summary.tiposdispositivo_chunks += 1
            logger.info(
                "Lote %s de tipos de dispositivo cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_service_types(), start=1):
            self._staging_repository.load_service_types(extraction_id=extraction_id, records=chunk)
            summary.tiposservicio += len(chunk)
            summary.tiposservicio_chunks += 1
            logger.info(
                "Lote %s de tipos de servicio cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_brands(), start=1):
            self._staging_repository.load_brands(extraction_id=extraction_id, records=chunk)
            summary.marcas += len(chunk)
            summary.marcas_chunks += 1
            logger.info(
                "Lote %s de marcas cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(
            self._raw_reader.read_equipment_credentials_metadata(),
            start=1,
        ):
            self._staging_repository.load_equipment_credentials_metadata(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.credencialesequipo += len(chunk)
            summary.credencialesequipo_chunks += 1
            logger.info(
                "Lote %s de metadatos de credenciales cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Carga tecnica a staging finalizada. Informes: %s | Fotos: %s | Equipos: %s | Series: %s | Tipos dispositivo: %s | Tipos servicio: %s | Marcas: %s | Credenciales: %s.",
            summary.informes,
            summary.informefotos,
            summary.equipos,
            summary.equiposseries,
            summary.tiposdispositivo,
            summary.tiposservicio,
            summary.marcas,
            summary.credencialesequipo,
        )
        return summary
