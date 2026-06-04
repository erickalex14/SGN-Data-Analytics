"""Script de arranque para construir el mart financiero en PostgreSQL."""

import logging

from novitec_dwh.contexts.financial.application.use_cases.load_financial_mart import (
    LoadFinancialMartUseCase,
)
from novitec_dwh.contexts.financial.infrastructure.postgresql_financial_mart_repository import (
    PostgreSQLFinancialMartRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga del mart financiero."""

    configure_logging(log_file_name="etl_financial_mart.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    if not settings.etl_financial_extraction_id:
        raise ValueError(
            "Debes definir ETL_FINANCIAL_EXTRACTION_ID en el archivo .env para construir el mart financiero."
        )

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    mart_repository = PostgreSQLFinancialMartRepository(
        connection_factory=postgres_connection_factory,
        staging_schema=settings.postgres_financial_staging_schema,
        mart_schema=settings.postgres_financial_mart_schema,
    )
    use_case = LoadFinancialMartUseCase(
        mart_repository=mart_repository,
        staging_schema=settings.postgres_financial_staging_schema,
        mart_schema=settings.postgres_financial_mart_schema,
        extraction_id=settings.etl_financial_extraction_id,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de mart financiero. Corrida: %s | Mart: %s | Solicitudes NC: %s | Precios orden: %s | Notificaciones: %s | Reglas calidad: %s | Hallazgos: %s.",
        summary.extraction_id,
        summary.mart_schema,
        summary.solicitudes_nc,
        summary.precios_orden,
        summary.notificaciones,
        summary.reglas_calidad_ejecutadas,
        summary.hallazgos_calidad,
    )
