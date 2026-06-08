"""Script de arranque para extraccion del dominio organizacional."""

import logging

from novitec_dwh.contexts.organizational.application.use_cases.extract_organizational_domain import (
    ExtractOrganizationalDomainUseCase,
)
from novitec_dwh.contexts.organizational.infrastructure.filesystem_organizational_extraction_sink import (
    FilesystemOrganizationalExtractionSink,
)
from novitec_dwh.contexts.organizational.infrastructure.mysql_organizational_extraction_repository import (
    MySQLOrganizationalExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta extraccion organizacional."""

    configure_logging(log_file_name="etl_organizational.log")

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

    repository = MySQLOrganizationalExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemOrganizationalExtractionSink(
        base_path=settings.etl_raw_base_path / "organizational",
    )
    use_case = ExtractOrganizationalDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio organizacional con tamano de lote %s.",
        settings.etl_chunk_size,
    )
    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de extraccion organizacional. Sucursales: %s | Roles: %s | Grupos: %s | Usuarios: %s | Usuario sucursal: %s | Permisos grupo: %s | Permisos usuario: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.sucursales,
        summary.roles,
        summary.gruposacceso,
        summary.usuarios,
        summary.usuariosucursales,
        summary.permisosgrupo,
        summary.permisosusuario,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
