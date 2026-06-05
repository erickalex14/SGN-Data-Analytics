"""Caso de uso para construir el mart tecnico desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.technical.application.dto_mart import TechnicalMartLoadSummary
from novitec_dwh.contexts.technical.application.mart_contracts import TechnicalMartRepository

logger = logging.getLogger(__name__)


class LoadTechnicalMartUseCase:
    """Orquesta la construccion del mart tecnico desde staging."""

    def __init__(
        self,
        mart_repository: TechnicalMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe el repositorio analitico y el contexto de la corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> TechnicalMartLoadSummary:
        """Construye dimensiones y hechos del mart tecnico."""

        summary = TechnicalMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart tecnico. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_technician_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_service_type_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_brand_dimension(extraction_id=self._extraction_id)

        summary.informes = self._mart_repository.load_report_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de informes tecnicos cargado. Registros: %s.", summary.informes)

        summary.fotos_informes = self._mart_repository.load_report_photo_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de evidencia fotografica cargado. Registros: %s.",
            summary.fotos_informes,
        )

        summary.equipos = self._mart_repository.load_equipment_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de equipos tecnicos cargado. Registros: %s.", summary.equipos)

        summary.accesos_equipos = self._mart_repository.load_equipment_access_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de accesos de equipos cargado. Registros: %s.",
            summary.accesos_equipos,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(extraction_id=self._extraction_id)
        logger.info(
            "Auditoria de calidad tecnica actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Mart tecnico finalizado. Informes: %s | Fotos: %s | Equipos: %s | Accesos: %s | Hallazgos calidad: %s.",
            summary.informes,
            summary.fotos_informes,
            summary.equipos,
            summary.accesos_equipos,
            summary.hallazgos_calidad,
        )
        return summary
