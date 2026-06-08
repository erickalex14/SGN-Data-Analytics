"""Pruebas del caso de uso de carga organizacional a staging."""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from novitec_dwh.contexts.organizational.application.use_cases.load_organizational_to_staging import (
    LoadOrganizationalToStagingUseCase,
)
from novitec_dwh.contexts.organizational.domain.entities import (
    GrupoAcceso,
    PermisoGrupo,
    PermisoUsuario,
    RolUsuario,
    SucursalPropia,
    UsuarioInterno,
    UsuarioSucursal,
)


class FakeOrganizationalRawReader:
    """Doblez de lectura raw para validar orquestacion organizacional a staging."""

    def __init__(self) -> None:
        """Inicializa estado simulado de corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone identificador simulado de corrida."""

        return "organizational_20260608_180000"

    @property
    def run_directory(self) -> Path:
        """Expone ruta raw simulada."""

        return Path("data/raw/organizational/organizational_20260608_180000")

    def prepare(self) -> None:
        """Marca corrida como preparada."""

        self._prepared = True

    def read_branches(self) -> Iterator[list[SucursalPropia]]:
        """Entrega lote simulado de sucursales."""

        assert self._prepared is True
        yield [SucursalPropia(id=1, nro_sucursal=1, ciudad="Quito", secuencial="001", nro_base="100")]

    def read_roles(self) -> Iterator[list[RolUsuario]]:
        """Entrega lote simulado de roles."""

        assert self._prepared is True
        yield [RolUsuario(id=1, rol="admin")]

    def read_access_groups(self) -> Iterator[list[GrupoAcceso]]:
        """Entrega lote simulado de grupos."""

        assert self._prepared is True
        yield [
            GrupoAcceso(
                id=1,
                nombre="Administradores",
                descripcion="Acceso total",
                es_superadmin=True,
                created_at=datetime(2026, 6, 8, 10, 0, 0),
            )
        ]

    def read_users(self) -> Iterator[list[UsuarioInterno]]:
        """Entrega lote simulado de usuarios."""

        assert self._prepared is True
        yield [
            UsuarioInterno(
                id=1,
                usuario="aperez",
                nombre_tecnico="Andrea Perez",
                telefono="0999999999",
                correo_tec="andrea@novitec.com",
                acceso_nc=True,
                rol_id=1,
                sucursal_id=1,
                activo=True,
                grupo_id=1,
            )
        ]

    def read_user_branches(self) -> Iterator[list[UsuarioSucursal]]:
        """Entrega lote simulado de usuario sucursal."""

        assert self._prepared is True
        yield [UsuarioSucursal(id=1, usuario_id=1, sucursal_id=1)]

    def read_group_permissions(self) -> Iterator[list[PermisoGrupo]]:
        """Entrega lote simulado de permisos de grupo."""

        assert self._prepared is True
        yield [PermisoGrupo(id=1, grupo_id=1, modulo="ordenes", accion="ver", permitido=True)]

    def read_user_permissions(self) -> Iterator[list[PermisoUsuario]]:
        """Entrega lote simulado de permisos de usuario."""

        assert self._prepared is True
        yield [
            PermisoUsuario(
                id=1,
                usuario_id=1,
                modulo="informes",
                accion="editar",
                permitido=True,
                created_at=datetime(2026, 6, 8, 11, 0, 0),
            )
        ]


class FakeOrganizationalStagingRepository:
    """Doblez de persistencia staging para validar flujo organizacional."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "sucursales": 0,
            "roles": 0,
            "gruposacceso": 0,
            "usuarios": 0,
            "usuariosucursales": 0,
            "permisosgrupo": 0,
            "permisosusuario": 0,
        }

    def prepare_schema(self) -> None:
        """Marca schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_branches(self, extraction_id: str, records: list[SucursalPropia]) -> None:
        """Cuenta sucursales cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["sucursales"] += len(records)

    def load_roles(self, extraction_id: str, records: list[RolUsuario]) -> None:
        """Cuenta roles cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["roles"] += len(records)

    def load_access_groups(self, extraction_id: str, records: list[GrupoAcceso]) -> None:
        """Cuenta grupos cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["gruposacceso"] += len(records)

    def load_users(self, extraction_id: str, records: list[UsuarioInterno]) -> None:
        """Cuenta usuarios cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["usuarios"] += len(records)

    def load_user_branches(self, extraction_id: str, records: list[UsuarioSucursal]) -> None:
        """Cuenta asignaciones usuario sucursal cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["usuariosucursales"] += len(records)

    def load_group_permissions(self, extraction_id: str, records: list[PermisoGrupo]) -> None:
        """Cuenta permisos de grupo cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["permisosgrupo"] += len(records)

    def load_user_permissions(self, extraction_id: str, records: list[PermisoUsuario]) -> None:
        """Cuenta permisos de usuario cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["permisosusuario"] += len(records)


def test_execute_carga_correctamente_dominio_organizacional_en_staging() -> None:
    """Valida orquestacion completa de carga organizacional a staging."""

    raw_reader = FakeOrganizationalRawReader()
    staging_repository = FakeOrganizationalStagingRepository()
    use_case = LoadOrganizationalToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_organizational",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "organizational_20260608_180000"
    assert staging_repository.loaded_counts["sucursales"] == 1
    assert staging_repository.loaded_counts["roles"] == 1
    assert staging_repository.loaded_counts["gruposacceso"] == 1
    assert staging_repository.loaded_counts["usuarios"] == 1
    assert staging_repository.loaded_counts["usuariosucursales"] == 1
    assert staging_repository.loaded_counts["permisosgrupo"] == 1
    assert staging_repository.loaded_counts["permisosusuario"] == 1
    assert summary.schema_name == "stg_organizational"
    assert summary.sucursales == 1
    assert summary.roles == 1
    assert summary.gruposacceso == 1
    assert summary.usuarios == 1
    assert summary.usuariosucursales == 1
    assert summary.permisosgrupo == 1
    assert summary.permisosusuario == 1
