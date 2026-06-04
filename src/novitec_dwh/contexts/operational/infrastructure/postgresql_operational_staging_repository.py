"""Repositorio PostgreSQL para la carga del dominio operativo a staging."""

from importlib.resources import files
from typing import Final

from novitec_dwh.contexts.operational.domain.entities import (
    OrdenEmpresa,
    OrdenEmpresaTecnico,
    OrdenPersonal,
    PreOrden,
    VistaOrden,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

VISTA_ORDENES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "orden_id",
    "nro_orden",
    "tipo_orden",
    "estado_orden",
    "estado_repuesto",
    "estado_garantia",
    "motivo_ingreso",
    "fecha_de_ingreso",
    "fecha_prometido",
    "fecha_entrega",
    "nro_factura",
    "nro_factura_2",
    "nro_sucursal_cliente",
    "tecnico_id",
    "sucursal_id",
    "ingresado_por",
    "cliente_id",
    "empresa_id",
    "equipo_id",
    "cliente",
    "nombres",
    "apellidos",
    "identificacion",
    "numero_contacto",
    "correo",
    "direccion",
    "tipo",
    "marca",
    "modelo",
    "serie",
    "falla",
    "observacion",
    "fecha_facturacion",
    "tecnico",
    "sucursal",
    "fecha_de_ingreso_fmt",
    "fecha_prometido_fmt",
    "fecha_entrega_fmt",
]

ORDENES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_orden",
    "nro_factura",
    "nro_factura_2",
    "motivo_ingreso",
    "nro_sucursal_cliente",
    "cliente_id",
    "equipo_id",
    "tecnico_id",
    "sucursal_id",
    "fecha_de_ingreso",
    "estado_orden",
    "estado_repuesto",
    "estado_garantia",
    "garantia_tipo",
    "garantia_cas",
    "cas_id",
    "cas_fecha_envio",
    "cas_fecha_retorno",
    "cas_numero_caso",
    "ingresado_por",
    "fecha_prometido",
    "modificado_por",
    "fecha_modificacion",
    "fecha_entrega",
    "fecha_finalizacion",
    "valor_estandar_id",
    "repuesto_inventario_id",
    "observacion",
    "tipo_servicio_id",
    "tipo_servicio_texto",
    "fecha_facturacion",
]

ORDENES_EMPRESAS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_orden",
    "empresa_id",
    "subtipo",
    "nro_sucursal_cliente",
    "equipo_id",
    "tipo_servicio",
    "nro_ticket",
    "descripcion",
    "tecnico_id",
    "sucursal_id",
    "cas_id",
    "ingresado_por",
    "fecha_prometido",
    "estado",
    "valor_hora",
    "horas_trabajadas",
    "fecha_ingreso",
]

PREORDENES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "orden_id",
    "fecha_registro",
    "nro_preorden",
    "sucursal_id",
    "nombres",
    "apellidos",
    "identificacion",
    "telefono",
    "correo",
    "nro_factura",
    "codigo_producto",
    "desc_producto",
    "marca_producto",
    "tipo_producto",
    "detalle_equipo",
    "foto_1",
    "foto_2",
    "foto_3",
    "foto_4",
    "estado",
    "created_at",
    "nro_sucursal_cliente",
    "ciudad_procedencia",
    "fecha_facturacion",
]

ORDEN_EMPRESA_TECNICOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "orden_empresa_id",
    "tecnico_id",
]


class PostgreSQLOperationalStagingRepository:
    """Gestiona la persistencia staging del dominio operativo en PostgreSQL."""

    def __init__(
        self,
        connection_factory: PostgreSQLConnectionFactory,
        schema_name: str,
    ) -> None:
        """Recibe la fabrica de conexiones y el schema objetivo."""

        self._connection_factory = connection_factory
        self._schema_name = schema_name

    def prepare_schema(self) -> None:
        """Crea el schema y las tablas staging requeridas si no existen."""

        ddl_template = (
            files("novitec_dwh.contexts.operational.infrastructure.sql")
            .joinpath("operational_staging.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{schema_name}", self._schema_name)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de la misma corrida antes de recargarla."""

        tables = [
            "stg_operational_order_company_technicians",
            "stg_operational_preorders",
            "stg_operational_company_orders",
            "stg_operational_personal_orders",
            "stg_operational_order_view",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._schema_name}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def load_order_view(self, extraction_id: str, records: list[VistaOrden]) -> None:
        """Carga la vista consolidada de ordenes usando COPY."""

        rows = [
            (
                extraction_id,
                record.orden_id,
                record.nro_orden,
                record.tipo_orden,
                record.estado_orden,
                record.estado_repuesto,
                record.estado_garantia,
                record.motivo_ingreso,
                record.fecha_de_ingreso,
                record.fecha_prometido,
                record.fecha_entrega,
                record.nro_factura,
                record.nro_factura_2,
                record.nro_sucursal_cliente,
                record.tecnico_id,
                record.sucursal_id,
                record.ingresado_por,
                record.cliente_id,
                record.empresa_id,
                record.equipo_id,
                record.cliente,
                record.nombres,
                record.apellidos,
                record.identificacion,
                record.numero_contacto,
                record.correo,
                record.direccion,
                record.tipo,
                record.marca,
                record.modelo,
                record.serie,
                record.falla,
                record.observacion,
                record.fecha_facturacion,
                record.tecnico,
                record.sucursal,
                record.fecha_de_ingreso_fmt,
                record.fecha_prometido_fmt,
                record.fecha_entrega_fmt,
            )
            for record in records
        ]
        self._copy_rows("stg_operational_order_view", VISTA_ORDENES_COLUMNS, rows)

    def load_personal_orders(self, extraction_id: str, records: list[OrdenPersonal]) -> None:
        """Carga ordenes personales usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_orden,
                record.nro_factura,
                record.nro_factura_2,
                record.motivo_ingreso,
                record.nro_sucursal_cliente,
                record.cliente_id,
                record.equipo_id,
                record.tecnico_id,
                record.sucursal_id,
                record.fecha_de_ingreso,
                record.estado_orden,
                record.estado_repuesto,
                record.estado_garantia,
                record.garantia_tipo,
                record.garantia_cas,
                record.cas_id,
                record.cas_fecha_envio,
                record.cas_fecha_retorno,
                record.cas_numero_caso,
                record.ingresado_por,
                record.fecha_prometido,
                record.modificado_por,
                record.fecha_modificacion,
                record.fecha_entrega,
                record.fecha_finalizacion,
                record.valor_estandar_id,
                record.repuesto_inventario_id,
                record.observacion,
                record.tipo_servicio_id,
                record.tipo_servicio_texto,
                record.fecha_facturacion,
            )
            for record in records
        ]
        self._copy_rows("stg_operational_personal_orders", ORDENES_COLUMNS, rows)

    def load_company_orders(self, extraction_id: str, records: list[OrdenEmpresa]) -> None:
        """Carga ordenes empresariales usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_orden,
                record.empresa_id,
                record.subtipo,
                record.nro_sucursal_cliente,
                record.equipo_id,
                record.tipo_servicio,
                record.nro_ticket,
                record.descripcion,
                record.tecnico_id,
                record.sucursal_id,
                record.cas_id,
                record.ingresado_por,
                record.fecha_prometido,
                record.estado,
                record.valor_hora,
                record.horas_trabajadas,
                record.fecha_ingreso,
            )
            for record in records
        ]
        self._copy_rows("stg_operational_company_orders", ORDENES_EMPRESAS_COLUMNS, rows)

    def load_preorders(self, extraction_id: str, records: list[PreOrden]) -> None:
        """Carga preordenes usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.orden_id,
                record.fecha_registro,
                record.nro_preorden,
                record.sucursal_id,
                record.nombres,
                record.apellidos,
                record.identificacion,
                record.telefono,
                record.correo,
                record.nro_factura,
                record.codigo_producto,
                record.desc_producto,
                record.marca_producto,
                record.tipo_producto,
                record.detalle_equipo,
                record.foto_1,
                record.foto_2,
                record.foto_3,
                record.foto_4,
                record.estado,
                record.created_at,
                record.nro_sucursal_cliente,
                record.ciudad_procedencia,
                record.fecha_facturacion,
            )
            for record in records
        ]
        self._copy_rows("stg_operational_preorders", PREORDENES_COLUMNS, rows)

    def load_company_order_technicians(
        self,
        extraction_id: str,
        records: list[OrdenEmpresaTecnico],
    ) -> None:
        """Carga asignaciones tecnico-orden empresarial usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.orden_empresa_id,
                record.tecnico_id,
            )
            for record in records
        ]
        self._copy_rows(
            "stg_operational_order_company_technicians",
            ORDEN_EMPRESA_TECNICOS_COLUMNS,
            rows,
        )

    def _copy_rows(self, table_name: str, columns: list[str], rows: list[tuple]) -> None:
        """Ejecuta una carga masiva eficiente hacia PostgreSQL."""

        if not rows:
            return

        columns_sql = ", ".join(columns)
        copy_sql = f"COPY {self._schema_name}.{table_name} ({columns_sql}) FROM STDIN"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                with cursor.copy(copy_sql) as copy:
                    for row in rows:
                        copy.write_row(row)
            connection.commit()
