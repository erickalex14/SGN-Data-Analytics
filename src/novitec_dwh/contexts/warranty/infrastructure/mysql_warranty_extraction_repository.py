"""Repositorio MySQL para la extraccion del dominio de garantias."""

from collections.abc import Iterator

from novitec_dwh.contexts.warranty.domain.entities import (
    CentroAutorizadoServicio,
    OrdenGarantiaEmpresa,
    OrdenGarantiaPersonal,
    UsuarioCasAsignacion,
)
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLWarrantyExtractionRepository:
    """Implementa la extraccion de garantias desde el origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe la fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_service_centers(
        self,
        chunk_size: int,
    ) -> Iterator[list[CentroAutorizadoServicio]]:
        """Extrae centros autorizados de servicio para analitica CAS."""

        query = """
            SELECT
                id,
                nombre,
                prefijo,
                marca,
                telefono,
                correo,
                direccion,
                ciudad,
                contacto,
                notas,
                activo,
                creado_en,
                actualizado_en
            FROM cas
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [CentroAutorizadoServicio(**row) for row in rows]

    def extract_user_assignments(self, chunk_size: int) -> Iterator[list[UsuarioCasAsignacion]]:
        """Extrae usuarios internos autorizados por CAS."""

        query = """
            SELECT
                uc.id,
                uc.usuario_id,
                u.usuario AS usuario_login,
                u.nombre_tecnico AS usuario_nombre,
                uc.cas_id
            FROM usuariocas uc
            INNER JOIN usuarios u
                ON u.id = uc.usuario_id
            ORDER BY uc.id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [UsuarioCasAsignacion(**row) for row in rows]

    def extract_personal_warranty_orders(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenGarantiaPersonal]]:
        """Extrae ordenes personales vinculadas a garantia o CAS."""

        query = """
            SELECT
                id,
                nro_orden,
                cliente_id,
                equipo_id,
                tecnico_id,
                sucursal_id,
                fecha_de_ingreso,
                estado_orden,
                estado_garantia,
                garantia_tipo,
                garantia_cas,
                cas_id,
                cas_fecha_envio,
                cas_fecha_retorno,
                cas_numero_caso,
                fecha_prometido,
                fecha_entrega,
                fecha_finalizacion
            FROM ordenes
            WHERE garantia_tipo IS NOT NULL
               OR estado_garantia IS NOT NULL
               OR cas_id IS NOT NULL
               OR cas_numero_caso IS NOT NULL
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [OrdenGarantiaPersonal(**row) for row in rows]

    def extract_company_warranty_orders(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenGarantiaEmpresa]]:
        """Extrae ordenes empresariales vinculadas a CAS."""

        query = """
            SELECT
                id,
                nro_orden,
                empresa_id,
                equipo_id,
                tecnico_id,
                sucursal_id,
                cas_id,
                fecha_ingreso,
                fecha_prometido,
                estado,
                valor_hora,
                horas_trabajadas,
                nro_ticket
            FROM ordenesempresas
            WHERE cas_id IS NOT NULL
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [OrdenGarantiaEmpresa(**row) for row in rows]
