"""Caso de uso para construir el mart financiero desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.financial.application.dto import FinancialMartLoadSummary
from novitec_dwh.contexts.financial.application.mart_contracts import (
    FinancialMartRepository,
)

logger = logging.getLogger(__name__)


class LoadFinancialMartUseCase:
    """Orquesta la construccion del mart financiero desde staging."""

    def __init__(
        self,
        mart_repository: FinancialMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe el repositorio analitico y el contexto de la corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> FinancialMartLoadSummary:
        """Construye dimensiones y hechos del mart financiero."""

        summary = FinancialMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart financiero. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_technician_dimension(extraction_id=self._extraction_id)

        summary.solicitudes_nc = self._mart_repository.load_credit_note_request_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de solicitudes de nota de credito cargado. Registros: %s.",
            summary.solicitudes_nc,
        )

        summary.precios_orden = self._mart_repository.load_order_price_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de precios por orden cargado. Registros: %s.",
            summary.precios_orden,
        )

        summary.notificaciones = self._mart_repository.load_credit_note_notification_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de notificaciones de nota de credito cargado. Registros: %s.",
            summary.notificaciones,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Auditoria de calidad actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)

        logger.info(
            "Mart financiero finalizado. Solicitudes NC: %s | Precios orden: %s | Notificaciones: %s | Hallazgos calidad: %s.",
            summary.solicitudes_nc,
            summary.precios_orden,
            summary.notificaciones,
            summary.hallazgos_calidad,
        )

        return summary
