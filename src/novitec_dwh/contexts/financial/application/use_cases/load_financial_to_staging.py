"""Caso de uso para cargar el dominio financiero hacia staging PostgreSQL."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.financial.application.dto import FinancialStagingLoadSummary
from novitec_dwh.contexts.financial.application.staging_contracts import (
    FinancialRawReader,
    FinancialStagingRepository,
)

logger = logging.getLogger(__name__)


class LoadFinancialToStagingUseCase:
    """Orquesta la carga de datasets financieros desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: FinancialRawReader,
        staging_repository: FinancialStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe los adaptadores necesarios para leer y cargar la corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> FinancialStagingLoadSummary:
        """Ejecuta la carga completa del dominio financiero en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = FinancialStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga financiera a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_credit_note_requests(), start=1):
            self._staging_repository.load_credit_note_requests(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.solicitudes_nc += len(chunk)
            summary.solicitudes_nc_chunks += 1
            logger.info(
                "Lote %s de solicitudes de nota de credito cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_order_prices(), start=1):
            self._staging_repository.load_order_prices(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.precios_orden += len(chunk)
            summary.precios_orden_chunks += 1
            logger.info(
                "Lote %s de precios por orden cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(
            self._raw_reader.read_credit_note_notifications(),
            start=1,
        ):
            self._staging_repository.load_credit_note_notifications(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.notificaciones += len(chunk)
            summary.notificaciones_chunks += 1
            logger.info(
                "Lote %s de notificaciones de nota de credito cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)

        logger.info(
            "Carga financiera a staging finalizada. Solicitudes NC: %s | Precios orden: %s | Notificaciones: %s.",
            summary.solicitudes_nc,
            summary.precios_orden,
            summary.notificaciones,
        )

        return summary
