"""Caso de uso para construir el mart operativo desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.operational.application.dto_mart import OperationalMartLoadSummary
from novitec_dwh.contexts.operational.application.mart_contracts import (
    OperationalMartRepository,
)

logger = logging.getLogger(__name__)


class LoadOperationalMartUseCase:
    """Orquesta la construccion del mart operativo desde staging."""

    def __init__(
        self,
        mart_repository: OperationalMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe el repositorio analitico y el contexto de la corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> OperationalMartLoadSummary:
        """Construye dimensiones y hechos del mart operativo."""

        summary = OperationalMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart operativo. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_technician_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_branch_dimension(extraction_id=self._extraction_id)

        summary.ordenes = self._mart_repository.load_order_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de ordenes operativo cargado. Registros: %s.", summary.ordenes)

        summary.preordenes = self._mart_repository.load_preorder_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de preordenes cargado. Registros: %s.", summary.preordenes)

        summary.asignaciones_tecnicos = self._mart_repository.load_company_order_assignment_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de asignaciones tecnico-orden cargado. Registros: %s.",
            summary.asignaciones_tecnicos,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(extraction_id=self._extraction_id)
        logger.info(
            "Auditoria de calidad operativa actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Mart operativo finalizado. Ordenes: %s | Preordenes: %s | Asignaciones: %s | Hallazgos calidad: %s.",
            summary.ordenes,
            summary.preordenes,
            summary.asignaciones_tecnicos,
            summary.hallazgos_calidad,
        )
        return summary
