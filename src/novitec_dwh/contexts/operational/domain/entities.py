"""Entidades del dominio operativo."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(slots=True)
class VistaOrden:
    """Representa un registro consolidado de la vista operativa de ordenes."""

    orden_id: int
    nro_orden: str
    tipo_orden: str
    estado_orden: str | None
    estado_repuesto: str | None
    estado_garantia: str | None
    motivo_ingreso: str | None
    fecha_de_ingreso: datetime | None
    fecha_prometido: date | None
    fecha_entrega: datetime | None
    nro_factura: str | None
    nro_factura_2: str | None
    nro_sucursal_cliente: str | None
    tecnico_id: int | None
    sucursal_id: int | None
    ingresado_por: int | None
    cliente_id: int | None
    empresa_id: int | None
    equipo_id: int | None
    cliente: str | None
    nombres: str | None
    apellidos: str | None
    identificacion: str | None
    numero_contacto: str | None
    correo: str | None
    direccion: str | None
    tipo: str | None
    marca: str | None
    modelo: str | None
    serie: str | None
    falla: str | None
    observacion: str | None
    fecha_facturacion: str | None
    tecnico: str | None
    sucursal: str | None
    fecha_de_ingreso_fmt: str | None
    fecha_prometido_fmt: str | None
    fecha_entrega_fmt: str | None


@dataclass(slots=True)
class OrdenPersonal:
    """Representa una orden personal transaccional."""

    id: int
    nro_orden: str | None
    nro_factura: str | None
    nro_factura_2: str | None
    motivo_ingreso: str
    nro_sucursal_cliente: str | None
    cliente_id: int
    equipo_id: int
    tecnico_id: int
    sucursal_id: int
    fecha_de_ingreso: datetime | None
    estado_orden: str | None
    estado_repuesto: str | None
    estado_garantia: str | None
    garantia_tipo: str | None
    garantia_cas: str | None
    cas_id: int | None
    cas_fecha_envio: date | None
    cas_fecha_retorno: date | None
    cas_numero_caso: str | None
    ingresado_por: int | None
    fecha_prometido: date | None
    modificado_por: int | None
    fecha_modificacion: datetime | None
    fecha_entrega: datetime | None
    fecha_finalizacion: datetime | None
    valor_estandar_id: int | None
    repuesto_inventario_id: int | None
    observacion: str | None
    tipo_servicio_id: int | None
    tipo_servicio_texto: str | None
    fecha_facturacion: date | None


@dataclass(slots=True)
class OrdenEmpresa:
    """Representa una orden empresarial transaccional."""

    id: int
    nro_orden: str
    empresa_id: int
    subtipo: str
    nro_sucursal_cliente: str | None
    equipo_id: int | None
    tipo_servicio: str | None
    nro_ticket: str | None
    descripcion: str | None
    tecnico_id: int
    sucursal_id: int
    cas_id: int | None
    ingresado_por: int | None
    fecha_prometido: date | None
    estado: str
    valor_hora: Decimal | None
    horas_trabajadas: Decimal | None
    fecha_ingreso: datetime


@dataclass(slots=True)
class PreOrden:
    """Representa una preorden previa a la formalizacion de una orden."""

    id: int
    orden_id: int | None
    fecha_registro: datetime | None
    nro_preorden: str
    sucursal_id: int
    nombres: str
    apellidos: str
    identificacion: str | None
    telefono: str
    correo: str
    nro_factura: str | None
    codigo_producto: str | None
    desc_producto: str | None
    marca_producto: str | None
    tipo_producto: str | None
    detalle_equipo: str | None
    foto_1: str | None
    foto_2: str | None
    foto_3: str | None
    foto_4: str | None
    estado: str | None
    created_at: datetime | None
    nro_sucursal_cliente: int | None
    ciudad_procedencia: str | None
    fecha_facturacion: date | None


@dataclass(slots=True)
class OrdenEmpresaTecnico:
    """Representa la asignacion de multiples tecnicos a ordenes empresariales."""

    id: int
    orden_empresa_id: int
    tecnico_id: int
