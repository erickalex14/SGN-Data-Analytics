"""Contratos del dominio organizacional y de seguridad."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.organizational.domain.entities import (
    GrupoAcceso,
    PermisoGrupo,
    PermisoUsuario,
    RolUsuario,
    SucursalPropia,
    UsuarioInterno,
    UsuarioSucursal,
)


class OrganizationalExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio organizacional."""

    def extract_branches(self, chunk_size: int) -> Iterator[list[SucursalPropia]]:
        """Extrae sucursales propias por lotes."""

    def extract_roles(self, chunk_size: int) -> Iterator[list[RolUsuario]]:
        """Extrae roles funcionales por lotes."""

    def extract_access_groups(self, chunk_size: int) -> Iterator[list[GrupoAcceso]]:
        """Extrae grupos de acceso por lotes."""

    def extract_users(self, chunk_size: int) -> Iterator[list[UsuarioInterno]]:
        """Extrae usuarios internos por lotes."""

    def extract_user_branches(self, chunk_size: int) -> Iterator[list[UsuarioSucursal]]:
        """Extrae asignaciones de usuarios a sucursales por lotes."""

    def extract_group_permissions(self, chunk_size: int) -> Iterator[list[PermisoGrupo]]:
        """Extrae permisos de grupos por lotes."""

    def extract_user_permissions(self, chunk_size: int) -> Iterator[list[PermisoUsuario]]:
        """Extrae permisos de usuarios por lotes."""
