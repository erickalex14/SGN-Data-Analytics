"""Script de arranque para cargar el dominio tecnico a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.technical.application.use_cases.load_technical_to_staging import (
    LoadTechnicalToStagingUseCase,
)
from novitec_dwh.contexts.technical.infrastructure.filesystem_technical_raw_reader import (
    FilesystemTechnicalRawReader,
)
from novitec_dwh.contexts.technical.infrastructure.postgresql_technical_staging_repository import (
    PostgreSQLTechnicalStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga tecnica a staging."""

    configure_logging(log_file_name="etl_technical_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemTechnicalRawReader(
        base_path=settings.etl_raw_base_path / "technical",
        extraction_id=settings.etl_technical_extraction_id,
    )
    staging_repository = PostgreSQLTechnicalStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_technical_staging_schema,
    )
    use_case = LoadTechnicalToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_technical_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga tecnica a staging. Corrida: %s | Schema: %s | Informes: %s | Fotos: %s | Equipos: %s | Series: %s | Tipos dispositivo: %s | Tipos servicio: %s | Marcas: %s | Credenciales: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.informes,
        summary.informefotos,
        summary.equipos,
        summary.equiposseries,
        summary.tiposdispositivo,
        summary.tiposservicio,
        summary.marcas,
        summary.credencialesequipo,
    )
