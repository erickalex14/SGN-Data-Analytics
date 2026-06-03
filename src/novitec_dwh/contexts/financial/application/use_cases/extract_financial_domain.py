"""Caso de uso para extraer el dominio financiero completo."""

import logging
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.financial.application.contracts import FinancialExtractionSink
from novitec_dwh.contexts.financial.application.dto import FinancialExtractionSummary
from novitec_dwh.contexts.financial.domain.repositories import FinancialExtractionRepository

logger = logging.getLogger(__name__)


class ExtractFinancialDomainUseCase:
    """Orquesta la extraccion de las tablas financieras priorizadas."""

    def __init__(
        self,
        repository: FinancialExtractionRepository,
        sink: FinancialExtractionSink,
    ) -> None:
        """Recibe el repositorio concreto que conoce el origen de datos."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> FinancialExtractionSummary:
        """Ejecuta la extraccion completa y devuelve un resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("financial_%Y%m%d_%H%M%S")
        summary = FinancialExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info("Inicio de extraccion del dominio financiero. Corrida: %s.", extraction_id)

        self._process_dataset(
            dataset_name="solicitudes_nc",
            chunk_iterator=self._repository.extract_credit_note_requests(chunk_size=chunk_size),
            summary=summary,
            records_field="solicitudes_nc",
            chunks_field="solicitudes_nc_chunks",
            log_label="solicitudes de nota de credito",
        )

        self._process_dataset(
            dataset_name="precios_orden",
            chunk_iterator=self._repository.extract_order_prices(chunk_size=chunk_size),
            summary=summary,
            records_field="precios_orden",
            chunks_field="precios_orden_chunks",
            log_label="precios por orden",
        )

        self._process_dataset(
            dataset_name="notificaciones",
            chunk_iterator=self._repository.extract_credit_note_notifications(chunk_size=chunk_size),
            summary=summary,
            records_field="notificaciones",
            chunks_field="notificaciones_chunks",
            log_label="notificaciones de nota de credito",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion financiera finalizada. Solicitudes NC: %s en %s lotes | Precios orden: %s en %s lotes | Notificaciones: %s en %s lotes.",
            summary.solicitudes_nc,
            summary.solicitudes_nc_chunks,
            summary.precios_orden,
            summary.precios_orden_chunks,
            summary.notificaciones,
            summary.notificaciones_chunks,
        )

        return summary

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: FinancialExtractionSummary,
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
