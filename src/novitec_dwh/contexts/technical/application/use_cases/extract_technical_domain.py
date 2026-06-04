"""Caso de uso para extraer el dominio tecnico completo."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.technical.application.contracts import TechnicalExtractionSink
from novitec_dwh.contexts.technical.application.dto import TechnicalExtractionSummary
from novitec_dwh.contexts.technical.domain.repositories import TechnicalExtractionRepository

logger = logging.getLogger(__name__)


class ExtractTechnicalDomainUseCase:
    """Orquesta la extraccion de las tablas tecnicas priorizadas."""

    def __init__(
        self,
        repository: TechnicalExtractionRepository,
        sink: TechnicalExtractionSink,
    ) -> None:
        """Recibe el repositorio concreto que conoce el origen de datos."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> TechnicalExtractionSummary:
        """Ejecuta la extraccion completa y devuelve un resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("technical_%Y%m%d_%H%M%S")
        summary = TechnicalExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info("Inicio de extraccion del dominio tecnico. Corrida: %s.", extraction_id)

        self._process_dataset(
            dataset_name="informes",
            chunk_iterator=self._repository.extract_reports(chunk_size=chunk_size),
            summary=summary,
            records_field="informes",
            chunks_field="informes_chunks",
            log_label="informes tecnicos",
        )
        self._process_dataset(
            dataset_name="informefotos",
            chunk_iterator=self._repository.extract_report_photo_metadata(chunk_size=chunk_size),
            summary=summary,
            records_field="informefotos",
            chunks_field="informefotos_chunks",
            log_label="metadatos de fotos de informes",
        )
        self._process_dataset(
            dataset_name="equipos",
            chunk_iterator=self._repository.extract_equipment(chunk_size=chunk_size),
            summary=summary,
            records_field="equipos",
            chunks_field="equipos_chunks",
            log_label="equipos",
        )
        self._process_dataset(
            dataset_name="equiposseries",
            chunk_iterator=self._repository.extract_equipment_series(chunk_size=chunk_size),
            summary=summary,
            records_field="equiposseries",
            chunks_field="equiposseries_chunks",
            log_label="series de equipos",
        )
        self._process_dataset(
            dataset_name="tiposdispositivo",
            chunk_iterator=self._repository.extract_device_types(chunk_size=chunk_size),
            summary=summary,
            records_field="tiposdispositivo",
            chunks_field="tiposdispositivo_chunks",
            log_label="tipos de dispositivo",
        )
        self._process_dataset(
            dataset_name="tiposservicio",
            chunk_iterator=self._repository.extract_service_types(chunk_size=chunk_size),
            summary=summary,
            records_field="tiposservicio",
            chunks_field="tiposservicio_chunks",
            log_label="tipos de servicio",
        )
        self._process_dataset(
            dataset_name="marcas",
            chunk_iterator=self._repository.extract_brands(chunk_size=chunk_size),
            summary=summary,
            records_field="marcas",
            chunks_field="marcas_chunks",
            log_label="marcas",
        )
        self._process_dataset(
            dataset_name="credencialesequipo",
            chunk_iterator=self._repository.extract_equipment_credentials_metadata(chunk_size=chunk_size),
            summary=summary,
            records_field="credencialesequipo",
            chunks_field="credencialesequipo_chunks",
            log_label="metadatos de acceso de equipos",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion tecnica finalizada. Informes: %s | Fotos: %s | Equipos: %s | Series: %s | Tipos dispositivo: %s | Tipos servicio: %s | Marcas: %s | Credenciales equipo: %s.",
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

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: TechnicalExtractionSummary,
        records_field: str,
        chunks_field: str,
        log_label: str,
    ) -> None:
        """Procesa un conjunto de datos en bloques y los persiste en la zona raw."""

        chunk_number = 0
        for chunk in chunk_iterator:
            chunk_number += 1
            setattr(summary, records_field, getattr(summary, records_field) + len(chunk))
            setattr(summary, chunks_field, getattr(summary, chunks_field) + 1)
            output_file = self._sink.write(
                dataset_name=dataset_name,
                chunk_number=chunk_number,
                records=chunk,
            )
            logger.info(
                "Lote %s de %s extraido y persistido correctamente. Registros: %s. Archivo: %s.",
                chunk_number,
                log_label,
                len(chunk),
                Path(output_file).as_posix(),
            )
