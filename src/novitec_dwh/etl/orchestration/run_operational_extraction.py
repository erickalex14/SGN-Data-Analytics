"""Script de arranque para la extraccion del dominio operativo."""

import logging

from novitec_dwh.contexts.operational.application.use_cases.extract_operational_domain import (
    ExtractOperationalDomainUseCase,
)
from novitec_dwh.contexts.operational.infrastructure.filesystem_operational_extraction_sink import (
    FilesystemOperationalExtractionSink,
)
from novitec_dwh.contexts.operational.infrastructure.mysql_operational_extraction_repository import (
    MySQLOperationalExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la extraccion operativa."""

    configure_logging(log_file_name="etl_operational.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    mysql_connection_factory = MySQLConnectionFactory(settings=settings)
    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a MySQL origen.")
    mysql_connection_factory.test_connection()
    logger.info("La conectividad con MySQL origen fue validada correctamente.")

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    repository = MySQLOperationalExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemOperationalExtractionSink(
        base_path=settings.etl_raw_base_path / "operational",
    )
    use_case = ExtractOperationalDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio operativo con tamano de lote %s.",
        settings.etl_chunk_size,
    )
    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de la extraccion operativa. Vista ordenes: %s | Ordenes: %s | Ordenes empresas: %s | Preordenes: %s | Asignaciones tecnicos: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.vista_ordenes,
        summary.ordenes,
        summary.ordenes_empresas,
        summary.preordenes,
        summary.orden_empresa_tecnicos,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
