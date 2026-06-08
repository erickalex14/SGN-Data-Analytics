"""Pruebas del caso de uso de extraccion organizacional."""

from collections.abc import Iterator
from datetime import datetime

from novitec_dwh.contexts.organizational.application.use_cases.extract_organizational_domain import (
    ExtractOrganizationalDomainUseCase,
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
from novitec_dwh.contexts.organizational.infrastructure.filesystem_organizational_extraction_sink import (
    FilesystemOrganizationalExtractionSink,
)


class FakeOrganizationalExtractionRepository:
    """Doblez de pruebas para validar flujo organizacional."""

    def extract_branches(self, chunk_size: int) -> Iterator[list[SucursalPropia]]:
        """Devuelve lote simulado de sucursales."""

        _ = chunk_size
        yield [
            SucursalPropia(
                id=1,
                nro_sucursal=1,
                ciudad="Quito",
                secuencial="001",
                nro_base="100",
            )
        ]

    def extract_roles(self, chunk_size: int) -> Iterator[list[RolUsuario]]:
        """Devuelve lote simulado de roles."""

        _ = chunk_size
        yield [RolUsuario(id=1, rol="admin")]

    def extract_access_groups(self, chunk_size: int) -> Iterator[list[GrupoAcceso]]:
        """Devuelve lote simulado de grupos."""

        _ = chunk_size
        yield [
            GrupoAcceso(
                id=1,
                nombre="Administradores",
                descripcion="Acceso total",
                es_superadmin=True,
                created_at=datetime(2026, 6, 8, 10, 0, 0),
            )
        ]

    def extract_users(self, chunk_size: int) -> Iterator[list[UsuarioInterno]]:
        """Devuelve lote simulado de usuarios."""

        _ = chunk_size
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

    def extract_user_branches(self, chunk_size: int) -> Iterator[list[UsuarioSucursal]]:
        """Devuelve lote simulado de asignaciones usuario sucursal."""

        _ = chunk_size
        yield [UsuarioSucursal(id=1, usuario_id=1, sucursal_id=1)]

    def extract_group_permissions(self, chunk_size: int) -> Iterator[list[PermisoGrupo]]:
        """Devuelve lote simulado de permisos de grupo."""

        _ = chunk_size
        yield [
            PermisoGrupo(
                id=1,
                grupo_id=1,
                modulo="ordenes",
                accion="ver",
                permitido=True,
            )
        ]

    def extract_user_permissions(self, chunk_size: int) -> Iterator[list[PermisoUsuario]]:
        """Devuelve lote simulado de permisos de usuario."""

        _ = chunk_size
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


def test_execute_resume_correctamente_registros_organizacionales(tmp_path) -> None:
    """Valida que caso de uso acumule volumen total por entidad."""

    repository = FakeOrganizationalExtractionRepository()
    sink = FilesystemOrganizationalExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractOrganizationalDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.sucursales == 1
    assert summary.roles == 1
    assert summary.gruposacceso == 1
    assert summary.usuarios == 1
    assert summary.usuariosucursales == 1
    assert summary.permisosgrupo == 1
    assert summary.permisosusuario == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
