"""Caso de uso para construir el mart CRM desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.crm.application.dto_mart import CrmMartLoadSummary
from novitec_dwh.contexts.crm.application.mart_contracts import CrmMartRepository

logger = logging.getLogger(__name__)


class LoadCrmMartUseCase:
    """Orquesta la construccion del mart CRM desde staging."""

    def __init__(
        self,
        mart_repository: CrmMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe el repositorio analitico y el contexto de la corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> CrmMartLoadSummary:
        """Construye dimensiones y hechos del mart CRM."""

        summary = CrmMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart CRM. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_customer_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_company_dimension(extraction_id=self._extraction_id)

        summary.clientes = self._mart_repository.load_customer_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de clientes cargado. Registros: %s.", summary.clientes)

        summary.empresas = self._mart_repository.load_company_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de empresas cargado. Registros: %s.", summary.empresas)

        summary.sucursalescliente = self._mart_repository.load_customer_branch_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de sucursales cliente cargado. Registros: %s.",
            summary.sucursalescliente,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(extraction_id=self._extraction_id)
        logger.info(
            "Auditoria de calidad CRM actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Mart CRM finalizado. Clientes: %s | Empresas: %s | Sucursales cliente: %s | Hallazgos calidad: %s.",
            summary.clientes,
            summary.empresas,
            summary.sucursalescliente,
            summary.hallazgos_calidad,
        )
        return summary
