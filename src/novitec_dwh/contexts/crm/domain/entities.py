"""Entidades del dominio CRM."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Cliente:
    """Representa un cliente final del negocio."""

    id: int
    nombres: str
    apellidos: str
    identificacion: str
    numero_contacto: str
    correo: str | None
    direccion_clientes: str | None


@dataclass(slots=True)
class Empresa:
    """Representa una empresa cliente del negocio."""

    id: int
    nombre: str
    ruc: str
    telefono: str | None
    correo: str | None
    direccion_empresa: str | None
    created_at: datetime


@dataclass(slots=True)
class SucursalCliente:
    """Representa una sede fisica de una empresa cliente."""

    id: int
    codigo: str
    numero: int
    nombre: str
    provincia: str | None
    novitec_sucursal: str | None
    activa: bool
    created_at: datetime | None
