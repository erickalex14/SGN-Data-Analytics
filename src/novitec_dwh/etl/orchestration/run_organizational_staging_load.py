"""Script de arranque para cargar dominio organizacional a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.organizational.application.use_cases.load_organizational_to_staging import (
    LoadOrganizationalToStagingUseCase,
)
from novitec_dwh.contexts.organizational.infrastructure.filesystem_organizational_raw_reader import (
    FilesystemOrganizationalRawReader,
)
from novitec_dwh.contexts.organizational.infrastructure.postgresql_organizational_staging_repository import (
    PostgreSQLOrganizationalStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta carga organizacional a staging."""

    configure_logging(log_file_name="etl_organizational_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemOrganizationalRawReader(
        base_path=settings.etl_raw_base_path / "organizational",
        extraction_id=settings.etl_organizational_extraction_id,
    )
    staging_repository = PostgreSQLOrganizationalStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_organizational_staging_schema,
    )
    use_case = LoadOrganizationalToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_organizational_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga organizacional a staging. Corrida: %s | Schema: %s | Sucursales: %s | Roles: %s | Grupos: %s | Usuarios: %s | Usuario sucursal: %s | Permisos grupo: %s | Permisos usuario: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.sucursales,
        summary.roles,
        summary.gruposacceso,
        summary.usuarios,
        summary.usuariosucursales,
        summary.permisosgrupo,
        summary.permisosusuario,
    )
