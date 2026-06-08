"""Contratos de aplicacion para el mart organizacional."""

from typing import Protocol


class OrganizationalMartRepository(Protocol):
    """Contrato para construir mart organizacional desde staging."""

    def prepare_schema(self) -> None:
        """Crea o actualiza estructura analitica requerida."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia hechos de corrida previa del mismo identificador."""

    def resolve_latest_extraction_id(self) -> str:
        """Obtiene corrida organizacional mas reciente disponible en staging."""

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga dimension de fechas necesaria para corrida."""

    def load_branch_dimension(self, extraction_id: str) -> None:
        """Carga dimension de sucursales propias."""

    def load_role_dimension(self, extraction_id: str) -> None:
        """Carga dimension de roles."""

    def load_access_group_dimension(self, extraction_id: str) -> None:
        """Carga dimension de grupos de acceso."""

    def load_user_dimension(self, extraction_id: str) -> None:
        """Carga dimension de usuarios."""

    def load_user_fact(self, extraction_id: str) -> int:
        """Carga hecho principal de usuarios."""

    def load_user_branch_fact(self, extraction_id: str) -> int:
        """Carga hecho de asignaciones usuario sucursal."""

    def load_group_permission_fact(self, extraction_id: str) -> int:
        """Carga hecho de permisos de grupo."""

    def load_user_permission_fact(self, extraction_id: str) -> int:
        """Carga hecho de permisos de usuario."""

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Actualiza auditoria de calidad y devuelve reglas y hallazgos."""
