"""Entidades del dominio organizacional y de seguridad."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SucursalPropia:
    """Representa una sucursal propia de Novitec."""

    id: int
    nro_sucursal: int
    ciudad: str
    secuencial: str
    nro_base: str | None


@dataclass(slots=True)
class RolUsuario:
    """Representa un rol funcional del sistema."""

    id: int
    rol: str


@dataclass(slots=True)
class GrupoAcceso:
    """Representa un grupo de acceso administrativo."""

    id: int
    nombre: str
    descripcion: str | None
    es_superadmin: bool
    created_at: datetime


@dataclass(slots=True)
class UsuarioInterno:
    """Representa un usuario interno sin exponer credenciales sensibles."""

    id: int
    usuario: str
    nombre_tecnico: str
    telefono: str | None
    correo_tec: str | None
    acceso_nc: bool
    rol_id: int
    sucursal_id: int
    activo: bool
    grupo_id: int | None


@dataclass(slots=True)
class UsuarioSucursal:
    """Representa la asignacion de usuario a sucursal."""

    id: int
    usuario_id: int
    sucursal_id: int


@dataclass(slots=True)
class PermisoGrupo:
    """Representa un permiso otorgado a un grupo de acceso."""

    id: int
    grupo_id: int
    modulo: str
    accion: str
    permitido: bool


@dataclass(slots=True)
class PermisoUsuario:
    """Representa un permiso otorgado directamente a un usuario."""

    id: int
    usuario_id: int
    modulo: str
    accion: str
    permitido: bool
    created_at: datetime
