"""Adaptador base de conexion hacia PostgreSQL."""

from contextlib import contextmanager
from typing import Iterator

import psycopg
from psycopg import Connection

from novitec_dwh.core.config import Settings


class PostgreSQLConnectionFactory:
    """Crea conexiones hacia el Data Warehouse en PostgreSQL."""

    def __init__(self, settings: Settings) -> None:
        """Guarda la configuracion para reutilizarla al abrir conexiones."""

        self._settings = settings

    def create_connection(self) -> Connection:
        """Abre una conexion al destino PostgreSQL."""

        return psycopg.connect(
            host=self._settings.postgres_host,
            port=self._settings.postgres_port,
            dbname=self._settings.postgres_database,
            user=self._settings.postgres_user,
            password=self._settings.postgres_password,
        )

    @contextmanager
    def connection_scope(self) -> Iterator[Connection]:
        """Administra el ciclo de vida de una conexion PostgreSQL."""

        connection = self.create_connection()
        try:
            yield connection
        finally:
            connection.close()

    def test_connection(self) -> None:
        """Valida la conectividad minima contra PostgreSQL."""

        with self.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
