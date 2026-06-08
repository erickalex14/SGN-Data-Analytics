"""DTOs del contexto organizacional y de seguridad."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class OrganizationalExtractionSummary:
    """Resume volumen procesado durante extraccion organizacional."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    sucursales: int = 0
    sucursales_chunks: int = 0
    roles: int = 0
    roles_chunks: int = 0
    gruposacceso: int = 0
    gruposacceso_chunks: int = 0
    usuarios: int = 0
    usuarios_chunks: int = 0
    usuariosucursales: int = 0
    usuariosucursales_chunks: int = 0
    permisosgrupo: int = 0
    permisosgrupo_chunks: int = 0
    permisosusuario: int = 0
    permisosusuario_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class OrganizationalStagingLoadSummary:
    """Resume resultado de carga organizacional a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    sucursales: int = 0
    sucursales_chunks: int = 0
    roles: int = 0
    roles_chunks: int = 0
    gruposacceso: int = 0
    gruposacceso_chunks: int = 0
    usuarios: int = 0
    usuarios_chunks: int = 0
    usuariosucursales: int = 0
    usuariosucursales_chunks: int = 0
    permisosgrupo: int = 0
    permisosgrupo_chunks: int = 0
    permisosusuario: int = 0
    permisosusuario_chunks: int = 0
