"""Repositorio MySQL para la extraccion del dominio CRM."""

from collections.abc import Iterator

from novitec_dwh.contexts.crm.domain.entities import Cliente, Empresa, SucursalCliente
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLCrmExtractionRepository:
    """Implementa la extraccion CRM desde el origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe la fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_customers(self, chunk_size: int) -> Iterator[list[Cliente]]:
        """Extrae clientes finales para analitica comercial y de relacion."""

        query = """
            SELECT
                id,
                nombres,
                apellidos,
                identificacion,
                numero_contacto,
                correo,
                direccion_clientes
            FROM clientes
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [Cliente(**row) for row in rows]

    def extract_companies(self, chunk_size: int) -> Iterator[list[Empresa]]:
        """Extrae empresas cliente para analitica B2B."""

        query = """
            SELECT
                id,
                nombre,
                ruc,
                telefono,
                correo,
                direccion_empresa,
                created_at
            FROM empresas
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [Empresa(**row) for row in rows]

    def extract_customer_branches(self, chunk_size: int) -> Iterator[list[SucursalCliente]]:
        """Extrae sucursales cliente para trazabilidad geografica corporativa."""

        query = """
            SELECT
                id,
                codigo,
                numero,
                nombre,
                provincia,
                novitec_sucursal,
                activa,
                created_at
            FROM sucursalescliente
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [SucursalCliente(**row) for row in rows]
