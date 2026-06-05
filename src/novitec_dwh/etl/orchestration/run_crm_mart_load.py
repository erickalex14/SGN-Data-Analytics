"""Script de arranque para construir el mart CRM en PostgreSQL."""

import logging

from novitec_dwh.contexts.crm.application.use_cases.load_crm_mart import (
    LoadCrmMartUseCase,
)
from novitec_dwh.contexts.crm.infrastructure.postgresql_crm_mart_repository import (
    PostgreSQLCrmMartRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga del mart CRM."""

    configure_logging(log_file_name="etl_crm_mart.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    mart_repository = PostgreSQLCrmMartRepository(
        connection_factory=postgres_connection_factory,
        staging_schema=settings.postgres_crm_staging_schema,
        mart_schema=settings.postgres_crm_mart_schema,
    )
    extraction_id = settings.etl_crm_extraction_id
    if not extraction_id:
        extraction_id = mart_repository.resolve_latest_extraction_id()
        logger.info(
            "No se definio ETL_CRM_EXTRACTION_ID. Se usara la corrida mas reciente detectada en staging: %s.",
            extraction_id,
        )

    use_case = LoadCrmMartUseCase(
        mart_repository=mart_repository,
        staging_schema=settings.postgres_crm_staging_schema,
        mart_schema=settings.postgres_crm_mart_schema,
        extraction_id=extraction_id,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de mart CRM. Corrida: %s | Mart: %s | Clientes: %s | Empresas: %s | Sucursales cliente: %s | Reglas calidad: %s | Hallazgos: %s.",
        summary.extraction_id,
        summary.mart_schema,
        summary.clientes,
        summary.empresas,
        summary.sucursalescliente,
        summary.reglas_calidad_ejecutadas,
        summary.hallazgos_calidad,
    )
