"""Repositorio MySQL para la extraccion del dominio operativo."""

from collections.abc import Iterator

from novitec_dwh.contexts.operational.domain.entities import (
    OrdenEmpresa,
    OrdenEmpresaTecnico,
    OrdenPersonal,
    PreOrden,
    VistaOrden,
)
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLOperationalExtractionRepository:
    """Implementa la extraccion operativa desde el origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe la fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_order_view(self, chunk_size: int) -> Iterator[list[VistaOrden]]:
        """Extrae la vista unificada de ordenes para analitica operativa."""

        query = """
            SELECT
                orden_id,
                nro_orden,
                tipo_orden,
                estado_orden,
                estado_repuesto,
                estado_garantia,
                motivo_ingreso,
                fecha_de_ingreso,
                fecha_prometido,
                fecha_entrega,
                nro_factura,
                nro_factura_2,
                nro_sucursal_cliente,
                tecnico_id,
                sucursal_id,
                ingresado_por,
                cliente_id,
                empresa_id,
                equipo_id,
                cliente,
                nombres,
                apellidos,
                identificacion,
                numero_contacto,
                correo,
                direccion,
                tipo,
                marca,
                modelo,
                serie,
                falla,
                observacion,
                fecha_facturacion,
                tecnico,
                sucursal,
                fecha_de_ingreso_fmt,
                fecha_prometido_fmt,
                fecha_entrega_fmt
            FROM vista_ordenes
            ORDER BY orden_id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [VistaOrden(**row) for row in rows]

    def extract_personal_orders(self, chunk_size: int) -> Iterator[list[OrdenPersonal]]:
        """Extrae el detalle transaccional de ordenes personales."""

        query = """
            SELECT
                id,
                nro_orden,
                nro_factura,
                nro_factura_2,
                motivo_ingreso,
                nro_sucursal_cliente,
                cliente_id,
                equipo_id,
                tecnico_id,
                sucursal_id,
                fecha_de_ingreso,
                estado_orden,
                estado_repuesto,
                estado_garantia,
                garantia_tipo,
                garantia_cas,
                cas_id,
                cas_fecha_envio,
                cas_fecha_retorno,
                cas_numero_caso,
                ingresado_por,
                fecha_prometido,
                modificado_por,
                fecha_modificacion,
                fecha_entrega,
                fecha_finalizacion,
                valor_estandar_id,
                repuesto_inventario_id,
                observacion,
                tipo_servicio_id,
                tipo_servicio_texto,
                fecha_facturacion
            FROM ordenes
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [OrdenPersonal(**row) for row in rows]

    def extract_company_orders(self, chunk_size: int) -> Iterator[list[OrdenEmpresa]]:
        """Extrae el detalle transaccional de ordenes empresariales."""

        query = """
            SELECT
                id,
                nro_orden,
                empresa_id,
                subtipo,
                nro_sucursal_cliente,
                equipo_id,
                tipo_servicio,
                nro_ticket,
                descripcion,
                tecnico_id,
                sucursal_id,
                cas_id,
                ingresado_por,
                fecha_prometido,
                estado,
                valor_hora,
                horas_trabajadas,
                fecha_ingreso
            FROM ordenesempresas
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [OrdenEmpresa(**row) for row in rows]

    def extract_preorders(self, chunk_size: int) -> Iterator[list[PreOrden]]:
        """Extrae preordenes operativas generadas antes de la orden formal."""

        query = """
            SELECT
                id,
                orden_id,
                fecha_registro,
                nro_preorden,
                sucursal_id,
                nombres,
                apellidos,
                identificacion,
                telefono,
                correo,
                nro_factura,
                codigo_producto,
                desc_producto,
                marca_producto,
                tipo_producto,
                detalle_equipo,
                foto_1,
                foto_2,
                foto_3,
                foto_4,
                estado,
                created_at,
                nro_sucursal_cliente,
                ciudad_procedencia,
                fecha_facturacion
            FROM preordenes
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [PreOrden(**row) for row in rows]

    def extract_company_order_technicians(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenEmpresaTecnico]]:
        """Extrae la relacion muchos a muchos entre ordenes empresariales y tecnicos."""

        query = """
            SELECT
                id,
                orden_empresa_id,
                tecnico_id
            FROM orden_empresa_tecnicos
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [OrdenEmpresaTecnico(**row) for row in rows]
