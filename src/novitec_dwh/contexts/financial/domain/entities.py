"""Entidades del dominio financiero."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(slots=True)
class SolicitudNotaCredito:
    """Representa una solicitud de nota de credito en el dominio."""

    id: int
    nro_solicitud: str
    orden_id: int
    nro_orden: str | None
    fecha_solicitud: date
    asunto: str
    detalles: str
    nombre_admin: str | None
    motivo_rechazo: str | None
    tecnico_nombre: str
    tecnico_id: int
    estado: str
    creado_en: datetime | None
    created_at: datetime | None


@dataclass(slots=True)
class PrecioOrden:
    """Representa un cargo facturado asociado a una orden."""

    id: int
    orden_id: int
    nro_orden: str | None
    precio_estandar_id: int | None
    servicio: str
    precio: Decimal
    descripcion: str | None
    creado_en: datetime | None
    servicio_estandar: str | None
    precio_estandar: Decimal | None


@dataclass(slots=True)
class NotificacionNotaCredito:
    """Representa una notificacion relacionada con notas de credito."""

    id: int
    usuario_id: int
    usuario_nombre: str | None
    tipo: str
    mensaje: str
    nc_id: int | None
    orden_id: int | None
    nro_orden: str | None
    leida: bool
    created_at: datetime
