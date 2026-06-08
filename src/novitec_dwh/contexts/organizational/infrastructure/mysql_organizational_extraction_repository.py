"""Repositorio MySQL para extraccion del dominio organizacional."""

from collections.abc import Iterator

from novitec_dwh.contexts.organizational.domain.entities import (
    GrupoAcceso,
    PermisoGrupo,
    PermisoUsuario,
    RolUsuario,
    SucursalPropia,
    UsuarioInterno,
    UsuarioSucursal,
)
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLOrganizationalExtractionRepository:
    """Implementa extraccion organizacional desde origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_branches(self, chunk_size: int) -> Iterator[list[SucursalPropia]]:
        """Extrae sucursales propias para analitica organizacional."""

        query = """
            SELECT
                id,
                nro_sucursal,
                ciudad,
                secuencial,
                nro_base
            FROM sucursales
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [SucursalPropia(**row) for row in rows]

    def extract_roles(self, chunk_size: int) -> Iterator[list[RolUsuario]]:
        """Extrae roles funcionales del sistema."""

        query = """
            SELECT
                id,
                rol
            FROM roles
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [RolUsuario(**row) for row in rows]

    def extract_access_groups(self, chunk_size: int) -> Iterator[list[GrupoAcceso]]:
        """Extrae grupos de acceso administrativos."""

        query = """
            SELECT
                id,
                nombre,
                descripcion,
                es_superadmin,
                created_at
            FROM gruposacceso
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [GrupoAcceso(**row) for row in rows]

    def extract_users(self, chunk_size: int) -> Iterator[list[UsuarioInterno]]:
        """Extrae usuarios internos sin exponer credenciales sensibles."""

        query = """
            SELECT
                id,
                usuario,
                nombre_tecnico,
                telefono,
                correo_tec,
                acceso_nc,
                rol_id,
                sucursal_id,
                activo,
                grupo_id
            FROM usuarios
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [UsuarioInterno(**row) for row in rows]

    def extract_user_branches(self, chunk_size: int) -> Iterator[list[UsuarioSucursal]]:
        """Extrae asignaciones de usuarios a sucursales."""

        query = """
            SELECT
                id,
                usuario_id,
                sucursal_id
            FROM usuariosucursales
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [UsuarioSucursal(**row) for row in rows]

    def extract_group_permissions(self, chunk_size: int) -> Iterator[list[PermisoGrupo]]:
        """Extrae permisos por grupo de acceso."""

        query = """
            SELECT
                id,
                grupo_id,
                modulo,
                accion,
                permitido
            FROM permisosgrupo
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [PermisoGrupo(**row) for row in rows]

    def extract_user_permissions(self, chunk_size: int) -> Iterator[list[PermisoUsuario]]:
        """Extrae permisos directos por usuario."""

        query = """
            SELECT
                id,
                usuario_id,
                modulo,
                accion,
                permitido,
                created_at
            FROM permisosusuario
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [PermisoUsuario(**row) for row in rows]
