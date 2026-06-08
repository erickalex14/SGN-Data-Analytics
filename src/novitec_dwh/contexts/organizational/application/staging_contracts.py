"""Contratos de aplicacion para carga organizacional a staging."""

from collections.abc import Iterator
from pathlib import Path
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


class OrganizationalRawReader(Protocol):
    """Contrato para leer datasets organizacionales desde zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone identificador de corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone carpeta de corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida corrida raw objetivo."""

    def read_branches(self) -> Iterator[list[SucursalPropia]]:
        """Lee sucursales desde raw por lotes."""

    def read_roles(self) -> Iterator[list[RolUsuario]]:
        """Lee roles desde raw por lotes."""

    def read_access_groups(self) -> Iterator[list[GrupoAcceso]]:
        """Lee grupos de acceso desde raw por lotes."""

    def read_users(self) -> Iterator[list[UsuarioInterno]]:
        """Lee usuarios internos desde raw por lotes."""

    def read_user_branches(self) -> Iterator[list[UsuarioSucursal]]:
        """Lee asignaciones usuario sucursal desde raw por lotes."""

    def read_group_permissions(self) -> Iterator[list[PermisoGrupo]]:
        """Lee permisos de grupo desde raw por lotes."""

    def read_user_permissions(self) -> Iterator[list[PermisoUsuario]]:
        """Lee permisos de usuario desde raw por lotes."""


class OrganizationalStagingRepository(Protocol):
    """Contrato para persistir dominio organizacional en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta estructura organizacional requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa estado necesario para corrida concreta."""

    def load_branches(self, extraction_id: str, records: list[SucursalPropia]) -> None:
        """Carga sucursales en staging."""

    def load_roles(self, extraction_id: str, records: list[RolUsuario]) -> None:
        """Carga roles en staging."""

    def load_access_groups(self, extraction_id: str, records: list[GrupoAcceso]) -> None:
        """Carga grupos de acceso en staging."""

    def load_users(self, extraction_id: str, records: list[UsuarioInterno]) -> None:
        """Carga usuarios internos en staging."""

    def load_user_branches(self, extraction_id: str, records: list[UsuarioSucursal]) -> None:
        """Carga asignaciones usuario sucursal en staging."""

    def load_group_permissions(self, extraction_id: str, records: list[PermisoGrupo]) -> None:
        """Carga permisos de grupo en staging."""

    def load_user_permissions(self, extraction_id: str, records: list[PermisoUsuario]) -> None:
        """Carga permisos de usuario en staging."""
