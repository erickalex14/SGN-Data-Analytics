"""Entidades del dominio de garantias."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(slots=True)
class CentroAutorizadoServicio:
    """Representa un centro autorizado de servicio externo."""

    id: int
    nombre: str
    prefijo: str | None
    marca: str | None
    telefono: str | None
    correo: str | None
    direccion: str | None
    ciudad: str | None
    contacto: str | None
    notas: str | None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


@dataclass(slots=True)
class UsuarioCasAsignacion:
    """Representa la asignacion de un usuario interno a un CAS."""

    id: int
    usuario_id: int
    usuario_login: str
    usuario_nombre: str
    cas_id: int


@dataclass(slots=True)
class OrdenGarantiaPersonal:
    """Representa una orden personal asociada a garantia o CAS."""

    id: int
    nro_orden: str | None
    cliente_id: int
    equipo_id: int
    tecnico_id: int
    sucursal_id: int
    fecha_de_ingreso: datetime | None
    estado_orden: str | None
    estado_garantia: str | None
    garantia_tipo: str | None
    garantia_cas: str | None
    cas_id: int | None
    cas_fecha_envio: date | None
    cas_fecha_retorno: date | None
    cas_numero_caso: str | None
    fecha_prometido: date | None
    fecha_entrega: datetime | None
    fecha_finalizacion: datetime | None


@dataclass(slots=True)
class OrdenGarantiaEmpresa:
    """Representa una orden empresarial asociada a un CAS."""

    id: int
    nro_orden: str
    empresa_id: int
    equipo_id: int | None
    tecnico_id: int
    sucursal_id: int
    cas_id: int | None
    fecha_ingreso: datetime
    fecha_prometido: date | None
    estado: str
    valor_hora: Decimal | None
    horas_trabajadas: Decimal | None
    nro_ticket: str | None
