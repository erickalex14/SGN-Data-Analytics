"""Script de arranque para la extraccion del dominio financiero."""

import logging

from novitec_dwh.contexts.financial.infrastructure.filesystem_financial_extraction_sink import (
    FilesystemFinancialExtractionSink,
)
from novitec_dwh.contexts.financial.application.use_cases.extract_financial_domain import (
    ExtractFinancialDomainUseCase,
)
from novitec_dwh.contexts.financial.infrastructure.mysql_financial_extraction_repository import (
    MySQLFinancialExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la extraccion financiera."""

    configure_logging(log_file_name="etl_financial.log")

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

    # Se crea la cadena de dependencias siguiendo las capas del sistema para
    # mantener el caso de uso desacoplado de la tecnologia concreta.
    repository = MySQLFinancialExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemFinancialExtractionSink(
        base_path=settings.etl_raw_base_path / "financial",
    )
    use_case = ExtractFinancialDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio financiero con tamano de lote %s.",
        settings.etl_chunk_size,
    )

    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de la extraccion financiera. Solicitudes NC: %s | Precios orden: %s | Notificaciones: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.solicitudes_nc,
        summary.precios_orden,
        summary.notificaciones,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
