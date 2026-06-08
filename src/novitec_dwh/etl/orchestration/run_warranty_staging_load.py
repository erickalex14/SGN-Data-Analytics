"""Script de arranque para cargar el dominio de garantias a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.warranty.application.use_cases.load_warranty_to_staging import (
    LoadWarrantyToStagingUseCase,
)
from novitec_dwh.contexts.warranty.infrastructure.filesystem_warranty_raw_reader import (
    FilesystemWarrantyRawReader,
)
from novitec_dwh.contexts.warranty.infrastructure.postgresql_warranty_staging_repository import (
    PostgreSQLWarrantyStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga de garantias a staging."""

    configure_logging(log_file_name="etl_warranty_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemWarrantyRawReader(
        base_path=settings.etl_raw_base_path / "warranty",
        extraction_id=settings.etl_warranty_extraction_id,
    )
    staging_repository = PostgreSQLWarrantyStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_warranty_staging_schema,
    )
    use_case = LoadWarrantyToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_warranty_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga de garantias a staging. Corrida: %s | Schema: %s | CAS: %s | Usuario CAS: %s | Ordenes personales garantia: %s | Ordenes empresa CAS: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.cas,
        summary.usuariocas,
        summary.ordenes_garantia,
        summary.ordenesempresas_garantia,
    )
