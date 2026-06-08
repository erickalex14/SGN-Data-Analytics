"""Lector de datasets organizacionales desde zona raw basada en Parquet."""

from collections.abc import Iterator
import json
from pathlib import Path
from typing import TypeVar

import polars as pl

from novitec_dwh.contexts.organizational.domain.entities import (
    GrupoAcceso,
    PermisoGrupo,
    PermisoUsuario,
    RolUsuario,
    SucursalPropia,
    UsuarioInterno,
    UsuarioSucursal,
)

EntityType = TypeVar("EntityType")


class FilesystemOrganizationalRawReader:
    """Lee corrida organizacional ya extraida desde sistema de archivos."""

    def __init__(self, base_path: Path, extraction_id: str | None = None) -> None:
        """Recibe carpeta base raw y corrida opcional a resolver."""

        self._base_path = Path(base_path)
        self._requested_extraction_id = extraction_id
        self._extraction_id: str | None = None
        self._run_directory: Path | None = None
        self._manifest: dict | None = None

    @property
    def extraction_id(self) -> str:
        """Expone identificador de corrida raw seleccionada."""

        if self._extraction_id is None:
            raise RuntimeError("La corrida raw todavia no fue preparada.")
        return self._extraction_id

    @property
    def run_directory(self) -> Path:
        """Expone carpeta de corrida raw seleccionada."""

        if self._run_directory is None:
            raise RuntimeError("La corrida raw todavia no fue preparada.")
        return self._run_directory

    def prepare(self) -> None:
        """Resuelve corrida raw objetivo y valida manifiesto."""

        if self._requested_extraction_id:
            run_directory = self._base_path / self._requested_extraction_id
        else:
            run_directory = self._resolve_latest_run_directory()

        manifest_path = run_directory / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"No se encontro el manifiesto de la corrida organizacional: {manifest_path.as_posix()}",
            )

        self._run_directory = run_directory
        self._manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self._extraction_id = str(self._manifest["extraction_id"])

    def read_branches(self) -> Iterator[list[SucursalPropia]]:
        """Lee sucursales desde archivos Parquet."""

        yield from self._read_dataset("sucursales", SucursalPropia)

    def read_roles(self) -> Iterator[list[RolUsuario]]:
        """Lee roles desde archivos Parquet."""

        yield from self._read_dataset("roles", RolUsuario)

    def read_access_groups(self) -> Iterator[list[GrupoAcceso]]:
        """Lee grupos de acceso desde archivos Parquet."""

        yield from self._read_dataset("gruposacceso", GrupoAcceso)

    def read_users(self) -> Iterator[list[UsuarioInterno]]:
        """Lee usuarios internos desde archivos Parquet."""

        yield from self._read_dataset("usuarios", UsuarioInterno)

    def read_user_branches(self) -> Iterator[list[UsuarioSucursal]]:
        """Lee asignaciones usuario sucursal desde archivos Parquet."""

        yield from self._read_dataset("usuariosucursales", UsuarioSucursal)

    def read_group_permissions(self) -> Iterator[list[PermisoGrupo]]:
        """Lee permisos de grupo desde archivos Parquet."""

        yield from self._read_dataset("permisosgrupo", PermisoGrupo)

    def read_user_permissions(self) -> Iterator[list[PermisoUsuario]]:
        """Lee permisos de usuario desde archivos Parquet."""

        yield from self._read_dataset("permisosusuario", PermisoUsuario)

    def _read_dataset(
        self,
        dataset_name: str,
        entity_class: type[EntityType],
    ) -> Iterator[list[EntityType]]:
        """Carga cada archivo Parquet del dataset como lote independiente."""

        if self._run_directory is None:
            raise RuntimeError("La corrida raw todavia no fue preparada.")

        dataset_directory = self._run_directory / dataset_name
        if not dataset_directory.exists():
            return

        for parquet_file in sorted(dataset_directory.glob("*.parquet")):
            rows = pl.read_parquet(parquet_file).to_dicts()
            yield [entity_class(**row) for row in rows]

    def _resolve_latest_run_directory(self) -> Path:
        """Localiza corrida organizacional mas reciente dentro de zona raw."""

        if not self._base_path.exists():
            raise FileNotFoundError(
                f"La ruta base raw no existe: {self._base_path.as_posix()}",
            )

        candidates = sorted(
            [path for path in self._base_path.iterdir() if path.is_dir()],
            key=lambda path: path.name,
            reverse=True,
        )
        if not candidates:
            raise FileNotFoundError(
                f"No se encontraron corridas organizacionales en raw: {self._base_path.as_posix()}",
            )
        return candidates[0]
