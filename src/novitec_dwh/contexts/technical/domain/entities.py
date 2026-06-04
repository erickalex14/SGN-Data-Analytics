"""Entidades del dominio tecnico."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(slots=True)
class InformeTecnico:
    """Representa un informe tecnico emitido sobre una orden."""

    id: int
    orden_id: int
    tecnico_id: int
    antecedentes: str | None
    proceso: str | None
    conclusion: str | None
    recomendaciones: str | None
    estado_equipo: str | None
    fecha_informe: date
    fecha_creacion: datetime | None
    presupuesto_json: str | None


@dataclass(slots=True)
class InformeFotoMetadata:
    """Representa solo los metadatos auditables de una foto de informe."""

    id: int
    informe_id: int
    caption: str | None
    nombre_archivo: str | None
    tipo_mime: str | None
    orden_foto: int | None
    tiene_foto: bool


@dataclass(slots=True)
class EquipoTecnico:
    """Representa el maestro tecnico de equipos atendidos."""

    id: int
    tipo: str
    tipo_servicio_id: int | None
    tipo_servicio_texto: str | None
    marca: str
    modelo: str
    serie: str
    contrasena_equipo: str | None
    falla: str | None
    observacion: str | None
    fecha_facturacion: date | None
    producto_inventario_codigo: str | None


@dataclass(slots=True)
class EquipoSerie:
    """Representa una serie adicional asociada a un equipo."""

    id: int
    equipo_id: int
    serie: str
    orden: int
    created_at: datetime | None


@dataclass(slots=True)
class TipoDispositivo:
    """Representa el catalogo de tipos de dispositivo."""

    id: int
    codigo: str
    nombre: str


@dataclass(slots=True)
class TipoServicio:
    """Representa el catalogo maestro de servicios tecnicos."""

    id: int
    nombre: str
    descripcion: str | None
    precio: Decimal
    activo: bool
    created_at: datetime


@dataclass(slots=True)
class Marca:
    """Representa el catalogo maestro de marcas."""

    id: int
    nombre: str


@dataclass(slots=True)
class CredencialEquipoMetadata:
    """Representa solo metadatos de acceso sin exponer contrasenas."""

    id: int
    equipo_id: int
    usuario: str | None
    es_patron: bool
