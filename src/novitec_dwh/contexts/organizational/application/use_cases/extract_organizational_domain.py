"""Caso de uso para extraer dominio organizacional completo."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.organizational.application.contracts import (
    OrganizationalExtractionSink,
)
from novitec_dwh.contexts.organizational.application.dto import (
    OrganizationalExtractionSummary,
)
from novitec_dwh.contexts.organizational.domain.repositories import (
    OrganizationalExtractionRepository,
)

logger = logging.getLogger(__name__)


class ExtractOrganizationalDomainUseCase:
    """Orquesta extraccion de tablas organizacionales priorizadas."""

    def __init__(
        self,
        repository: OrganizationalExtractionRepository,
        sink: OrganizationalExtractionSink,
    ) -> None:
        """Recibe repositorio concreto y sink de persistencia raw."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> OrganizationalExtractionSummary:
        """Ejecuta extraccion completa y devuelve resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("organizational_%Y%m%d_%H%M%S")
        summary = OrganizationalExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info(
            "Inicio de extraccion del dominio organizacional y seguridad. Corrida: %s.",
            extraction_id,
        )

        self._process_dataset(
            dataset_name="sucursales",
            chunk_iterator=self._repository.extract_branches(chunk_size=chunk_size),
            summary=summary,
            records_field="sucursales",
            chunks_field="sucursales_chunks",
            log_label="sucursales propias",
        )
        self._process_dataset(
            dataset_name="roles",
            chunk_iterator=self._repository.extract_roles(chunk_size=chunk_size),
            summary=summary,
            records_field="roles",
            chunks_field="roles_chunks",
            log_label="roles",
        )
        self._process_dataset(
            dataset_name="gruposacceso",
            chunk_iterator=self._repository.extract_access_groups(chunk_size=chunk_size),
            summary=summary,
            records_field="gruposacceso",
            chunks_field="gruposacceso_chunks",
            log_label="grupos de acceso",
        )
        self._process_dataset(
            dataset_name="usuarios",
            chunk_iterator=self._repository.extract_users(chunk_size=chunk_size),
            summary=summary,
            records_field="usuarios",
            chunks_field="usuarios_chunks",
            log_label="usuarios internos",
        )
        self._process_dataset(
            dataset_name="usuariosucursales",
            chunk_iterator=self._repository.extract_user_branches(chunk_size=chunk_size),
            summary=summary,
            records_field="usuariosucursales",
            chunks_field="usuariosucursales_chunks",
            log_label="asignaciones usuario sucursal",
        )
        self._process_dataset(
            dataset_name="permisosgrupo",
            chunk_iterator=self._repository.extract_group_permissions(chunk_size=chunk_size),
            summary=summary,
            records_field="permisosgrupo",
            chunks_field="permisosgrupo_chunks",
            log_label="permisos de grupo",
        )
        self._process_dataset(
            dataset_name="permisosusuario",
            chunk_iterator=self._repository.extract_user_permissions(chunk_size=chunk_size),
            summary=summary,
            records_field="permisosusuario",
            chunks_field="permisosusuario_chunks",
            log_label="permisos de usuario",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion organizacional finalizada. Sucursales: %s | Roles: %s | Grupos: %s | Usuarios: %s | Usuario sucursal: %s | Permisos grupo: %s | Permisos usuario: %s.",
            summary.sucursales,
            summary.roles,
            summary.gruposacceso,
            summary.usuarios,
            summary.usuariosucursales,
            summary.permisosgrupo,
            summary.permisosusuario,
        )
        return summary

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: OrganizationalExtractionSummary,
        records_field: str,
        chunks_field: str,
        log_label: str,
    ) -> None:
        """Procesa dataset en bloques y lo persiste en zona raw."""

        chunk_number = 0
        for chunk in chunk_iterator:
            chunk_number += 1
            setattr(summary, records_field, getattr(summary, records_field) + len(chunk))
            setattr(summary, chunks_field, getattr(summary, chunks_field) + 1)
            output_file = self._sink.write(
                dataset_name=dataset_name,
                chunk_number=chunk_number,
                records=chunk,
            )
            logger.info(
                "Lote %s de %s extraido y persistido correctamente. Registros: %s. Archivo: %s.",
                chunk_number,
                log_label,
                len(chunk),
                Path(output_file).as_posix(),
            )
