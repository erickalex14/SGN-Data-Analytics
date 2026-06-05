"""Entidades del dominio de inventario."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(slots=True)
class Repuesto:
    """Representa el catalogo maestro de repuestos del taller."""

    id: int
    codigo: str
    nro_parte: str | None
    nombre: str
    descripcion: str | None
    marca_id: str | None
    tipo_dispositivo_id: str | None
    creado_en: datetime | None
    modificado_en: datetime | None
    stock: int
    costo: Decimal
    bodega: int


@dataclass(slots=True)
class ProductoInventario:
    """Representa un producto general clasificado en inventario."""

    id: int
    codigo: str
    descripcion: str
    marca_id: int
    tipo_dispositivo_id: int | None
    tipo_dispositivo_codigo: str | None


@dataclass(slots=True)
class OrdenRepuesto:
    """Representa un repuesto efectivamente instalado en una orden."""

    id: int
    orden_id: int
    repuesto_id: int
    cantidad: int
    fecha: datetime | None
    usuario_id: int | None


@dataclass(slots=True)
class SolicitudRepuesto:
    """Representa una solicitud operativa de abastecimiento de repuesto."""

    id: int
    nro_solicitud: str
    orden_id: int
    tecnico_id: int
    tecnico_nombre: str
    repuesto_nombre: str
    nro_parte: str | None
    nro_parte_inv_id: int | None
    repuesto_codigo: str | None
    repuesto_inv_id: int | None
    link_compra: str | None
    cantidad: int
    descripcion: str | None
    estado: str
    motivo_rechazo: str | None
    aprobado_por: str | None
    repuesto_id: int | None
    lista_compra_id: int | None
    fecha_solicitud: date
    fecha_gestion: datetime | None
    created_at: datetime


@dataclass(slots=True)
class ListaCompra:
    """Representa una agrupacion de solicitudes para compra en bloque."""

    id: int
    nro_lista: str
    creado_por: str
    creado_por_id: int | None
    fecha_creacion: date
    estado: str
    observacion: str | None
    created_at: datetime
