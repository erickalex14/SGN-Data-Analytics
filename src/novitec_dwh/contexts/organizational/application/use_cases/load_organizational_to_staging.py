"""Caso de uso para cargar dominio organizacional hacia staging PostgreSQL."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.organizational.application.dto import (
    OrganizationalStagingLoadSummary,
)
from novitec_dwh.contexts.organizational.application.staging_contracts import (
    OrganizationalRawReader,
    OrganizationalStagingRepository,
)

logger = logging.getLogger(__name__)


class LoadOrganizationalToStagingUseCase:
    """Orquesta carga de datasets organizacionales desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: OrganizationalRawReader,
        staging_repository: OrganizationalStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe adaptadores necesarios para leer y cargar corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> OrganizationalStagingLoadSummary:
        """Ejecuta carga completa del dominio organizacional en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = OrganizationalStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga organizacional a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_branches(), start=1):
            self._staging_repository.load_branches(extraction_id=extraction_id, records=chunk)
            summary.sucursales += len(chunk)
            summary.sucursales_chunks += 1
            logger.info(
                "Lote %s de sucursales cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_roles(), start=1):
            self._staging_repository.load_roles(extraction_id=extraction_id, records=chunk)
            summary.roles += len(chunk)
            summary.roles_chunks += 1
            logger.info(
                "Lote %s de roles cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_access_groups(), start=1):
            self._staging_repository.load_access_groups(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.gruposacceso += len(chunk)
            summary.gruposacceso_chunks += 1
            logger.info(
                "Lote %s de grupos de acceso cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_users(), start=1):
            self._staging_repository.load_users(extraction_id=extraction_id, records=chunk)
            summary.usuarios += len(chunk)
            summary.usuarios_chunks += 1
            logger.info(
                "Lote %s de usuarios internos cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_user_branches(), start=1):
            self._staging_repository.load_user_branches(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.usuariosucursales += len(chunk)
            summary.usuariosucursales_chunks += 1
            logger.info(
                "Lote %s de asignaciones usuario sucursal cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_group_permissions(), start=1):
            self._staging_repository.load_group_permissions(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.permisosgrupo += len(chunk)
            summary.permisosgrupo_chunks += 1
            logger.info(
                "Lote %s de permisos de grupo cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_user_permissions(), start=1):
            self._staging_repository.load_user_permissions(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.permisosusuario += len(chunk)
            summary.permisosusuario_chunks += 1
            logger.info(
                "Lote %s de permisos de usuario cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Carga organizacional a staging finalizada. Sucursales: %s | Roles: %s | Grupos: %s | Usuarios: %s | Usuario sucursal: %s | Permisos grupo: %s | Permisos usuario: %s.",
            summary.sucursales,
            summary.roles,
            summary.gruposacceso,
            summary.usuarios,
            summary.usuariosucursales,
            summary.permisosgrupo,
            summary.permisosusuario,
        )
        return summary
