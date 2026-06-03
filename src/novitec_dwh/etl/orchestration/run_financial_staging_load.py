"""Script de arranque para cargar el dominio financiero a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.financial.application.use_cases.load_financial_to_staging import (
    LoadFinancialToStagingUseCase,
)
from novitec_dwh.contexts.financial.infrastructure.filesystem_financial_raw_reader import (
    FilesystemFinancialRawReader,
)
from novitec_dwh.contexts.financial.infrastructure.postgresql_financial_staging_repository import (
    PostgreSQLFinancialStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga financiera a staging."""

    configure_logging(log_file_name="etl_financial_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemFinancialRawReader(
        base_path=settings.etl_raw_base_path / "financial",
        extraction_id=settings.etl_financial_extraction_id,
    )
    staging_repository = PostgreSQLFinancialStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_financial_staging_schema,
    )
    use_case = LoadFinancialToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_financial_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga staging. Corrida: %s | Schema: %s | Solicitudes NC: %s | Precios orden: %s | Notificaciones: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.solicitudes_nc,
        summary.precios_orden,
        summary.notificaciones,
    )
