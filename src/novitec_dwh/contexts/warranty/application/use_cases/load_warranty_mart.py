"""Caso de uso para construir el mart de garantias desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.warranty.application.dto_mart import WarrantyMartLoadSummary
from novitec_dwh.contexts.warranty.application.mart_contracts import WarrantyMartRepository

logger = logging.getLogger(__name__)


class LoadWarrantyMartUseCase:
    """Orquesta la construccion del mart del dominio de garantias."""

    def __init__(
        self,
        mart_repository: WarrantyMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe el repositorio analitico y el contexto de la corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> WarrantyMartLoadSummary:
        """Construye dimensiones, hechos y auditoria del mart de garantias."""

        summary = WarrantyMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart de garantias. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_service_center_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_user_dimension(extraction_id=self._extraction_id)

        summary.ordenes_personales = self._mart_repository.load_personal_order_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de ordenes personales de garantia cargado. Registros: %s.",
            summary.ordenes_personales,
        )

        summary.ordenes_empresariales = self._mart_repository.load_company_order_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de ordenes empresariales con CAS cargado. Registros: %s.",
            summary.ordenes_empresariales,
        )

        summary.asignaciones_usuario_cas = self._mart_repository.load_user_assignment_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de asignaciones usuario CAS cargado. Registros: %s.",
            summary.asignaciones_usuario_cas,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(extraction_id=self._extraction_id)
        logger.info(
            "Auditoria de calidad de garantias actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Mart de garantias finalizado. Ordenes personales: %s | Ordenes empresariales: %s | Asignaciones usuario CAS: %s | Hallazgos calidad: %s.",
            summary.ordenes_personales,
            summary.ordenes_empresariales,
            summary.asignaciones_usuario_cas,
            summary.hallazgos_calidad,
        )
        return summary
