"""Script de arranque para cargar el dominio operativo a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.operational.application.use_cases.load_operational_to_staging import (
    LoadOperationalToStagingUseCase,
)
from novitec_dwh.contexts.operational.infrastructure.filesystem_operational_raw_reader import (
    FilesystemOperationalRawReader,
)
from novitec_dwh.contexts.operational.infrastructure.postgresql_operational_staging_repository import (
    PostgreSQLOperationalStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga operativa a staging."""

    configure_logging(log_file_name="etl_operational_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemOperationalRawReader(
        base_path=settings.etl_raw_base_path / "operational",
        extraction_id=settings.etl_operational_extraction_id,
    )
    staging_repository = PostgreSQLOperationalStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_operational_staging_schema,
    )
    use_case = LoadOperationalToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_operational_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga operativa a staging. Corrida: %s | Schema: %s | Vista ordenes: %s | Ordenes: %s | Ordenes empresas: %s | Preordenes: %s | Asignaciones tecnicos: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.vista_ordenes,
        summary.ordenes,
        summary.ordenes_empresas,
        summary.preordenes,
        summary.orden_empresa_tecnicos,
    )
