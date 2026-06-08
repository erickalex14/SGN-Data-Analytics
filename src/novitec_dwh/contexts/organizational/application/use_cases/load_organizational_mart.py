"""Caso de uso para construir mart organizacional desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.organizational.application.dto_mart import (
    OrganizationalMartLoadSummary,
)
from novitec_dwh.contexts.organizational.application.mart_contracts import (
    OrganizationalMartRepository,
)

logger = logging.getLogger(__name__)


class LoadOrganizationalMartUseCase:
    """Orquesta construccion del mart organizacional desde staging."""

    def __init__(
        self,
        mart_repository: OrganizationalMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe repositorio analitico y contexto de corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> OrganizationalMartLoadSummary:
        """Construye dimensiones, hechos y auditoria del mart organizacional."""

        summary = OrganizationalMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart organizacional. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_branch_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_role_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_access_group_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_user_dimension(extraction_id=self._extraction_id)

        summary.usuarios = self._mart_repository.load_user_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de usuarios cargado. Registros: %s.", summary.usuarios)

        summary.usuarios_sucursales = self._mart_repository.load_user_branch_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de asignaciones usuario sucursal cargado. Registros: %s.",
            summary.usuarios_sucursales,
        )

        summary.permisos_grupo = self._mart_repository.load_group_permission_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de permisos de grupo cargado. Registros: %s.",
            summary.permisos_grupo,
        )

        summary.permisos_usuario = self._mart_repository.load_user_permission_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de permisos de usuario cargado. Registros: %s.",
            summary.permisos_usuario,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(extraction_id=self._extraction_id)
        logger.info(
            "Auditoria de calidad organizacional actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Mart organizacional finalizado. Usuarios: %s | Usuario sucursal: %s | Permisos grupo: %s | Permisos usuario: %s | Hallazgos calidad: %s.",
            summary.usuarios,
            summary.usuarios_sucursales,
            summary.permisos_grupo,
            summary.permisos_usuario,
            summary.hallazgos_calidad,
        )
        return summary
