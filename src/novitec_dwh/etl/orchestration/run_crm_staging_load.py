"""Script de arranque para cargar el dominio CRM a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.crm.application.use_cases.load_crm_to_staging import (
    LoadCrmToStagingUseCase,
)
from novitec_dwh.contexts.crm.infrastructure.filesystem_crm_raw_reader import (
    FilesystemCrmRawReader,
)
from novitec_dwh.contexts.crm.infrastructure.postgresql_crm_staging_repository import (
    PostgreSQLCrmStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga de CRM a staging."""

    configure_logging(log_file_name="etl_crm_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemCrmRawReader(
        base_path=settings.etl_raw_base_path / "crm",
        extraction_id=settings.etl_crm_extraction_id,
    )
    staging_repository = PostgreSQLCrmStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_crm_staging_schema,
    )
    use_case = LoadCrmToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_crm_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga de CRM a staging. Corrida: %s | Schema: %s | Clientes: %s | Empresas: %s | Sucursales cliente: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.clientes,
        summary.empresas,
        summary.sucursalescliente,
    )
