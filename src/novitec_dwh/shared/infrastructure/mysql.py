"""Adaptadores de conexion y lectura desde MySQL."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import mysql.connector
from mysql.connector import MySQLConnection

from novitec_dwh.core.config import Settings


class MySQLConnectionFactory:
    """Crea conexiones al origen transaccional MySQL."""

    def __init__(self, settings: Settings) -> None:
        """Recibe la configuracion necesaria para abrir conexiones."""

        self._settings = settings

    def create_connection(self) -> MySQLConnection:
        """Abre una nueva conexion al origen MySQL."""

        return mysql.connector.connect(
            host=self._settings.mysql_host,
            port=self._settings.mysql_port,
            database=self._settings.mysql_database,
            user=self._settings.mysql_user,
            password=self._settings.mysql_password,
        )

    @contextmanager
    def connection_scope(self) -> Iterator[MySQLConnection]:
        """Entrega una conexion administrada con cierre garantizado."""

        connection = self.create_connection()
        try:
            yield connection
        finally:
            connection.close()

    def fetch_query_in_chunks(
        self,
        query: str,
        chunk_size: int,
        params: tuple[Any, ...] | None = None,
    ) -> Iterator[list[dict[str, Any]]]:
        """Ejecuta una consulta y devuelve filas en lotes de tamano fijo."""

        with self.connection_scope() as connection:
            cursor = connection.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())

                while True:
                    rows = cursor.fetchmany(size=chunk_size)
                    if not rows:
                        break

                    # Se devuelve cada lote completo para que la capa superior
                    # procese o persista sin retener todo el resultado en RAM.
                    yield rows
            finally:
                cursor.close()

    def test_connection(self) -> None:
        """Valida la conectividad minima contra el origen MySQL."""

        with self.connection_scope() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            finally:
                cursor.close()
