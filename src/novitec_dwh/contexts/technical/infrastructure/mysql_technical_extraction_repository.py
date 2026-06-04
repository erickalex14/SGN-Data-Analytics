"""Repositorio MySQL para la extraccion del dominio tecnico."""

from collections.abc import Iterator

from novitec_dwh.contexts.technical.domain.entities import (
    CredencialEquipoMetadata,
    EquipoSerie,
    EquipoTecnico,
    InformeFotoMetadata,
    InformeTecnico,
    Marca,
    TipoDispositivo,
    TipoServicio,
)
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory


class MySQLTechnicalExtractionRepository:
    """Implementa la extraccion tecnica desde el origen MySQL."""

    def __init__(self, connection_factory: MySQLConnectionFactory) -> None:
        """Recibe la fabrica de conexiones reutilizable del origen."""

        self._connection_factory = connection_factory

    def extract_reports(self, chunk_size: int) -> Iterator[list[InformeTecnico]]:
        """Extrae informes tecnicos completos para analitica de calidad."""

        query = """
            SELECT
                id,
                orden_id,
                tecnico_id,
                antecedentes,
                proceso,
                conclusion,
                recomendaciones,
                estado_equipo,
                fecha_informe,
                fecha_creacion,
                presupuesto_json
            FROM informes
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [InformeTecnico(**row) for row in rows]

    def extract_report_photo_metadata(
        self,
        chunk_size: int,
    ) -> Iterator[list[InformeFotoMetadata]]:
        """Extrae solo metadatos de fotos sin mover blobs pesados al raw."""

        query = """
            SELECT
                id,
                informe_id,
                caption,
                nombre_archivo,
                tipo_mime,
                orden_foto,
                CASE WHEN foto_data IS NULL THEN FALSE ELSE TRUE END AS tiene_foto
            FROM informefotos
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [InformeFotoMetadata(**row) for row in rows]

    def extract_equipment(self, chunk_size: int) -> Iterator[list[EquipoTecnico]]:
        """Extrae el maestro de equipos atendidos por el taller."""

        query = """
            SELECT
                id,
                tipo,
                tipo_servicio_id,
                tipo_servicio_texto,
                marca,
                modelo,
                serie,
                contrasena_equipo,
                falla,
                observacion,
                fecha_facturacion,
                producto_inventario_codigo
            FROM equipos
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [EquipoTecnico(**row) for row in rows]

    def extract_equipment_series(self, chunk_size: int) -> Iterator[list[EquipoSerie]]:
        """Extrae series adicionales asociadas a equipos."""

        query = """
            SELECT
                id,
                equipo_id,
                serie,
                orden,
                created_at
            FROM equiposseries
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [EquipoSerie(**row) for row in rows]

    def extract_device_types(self, chunk_size: int) -> Iterator[list[TipoDispositivo]]:
        """Extrae el catalogo maestro de tipos de dispositivo."""

        query = """
            SELECT
                id,
                codigo,
                nombre
            FROM tiposdispositivo
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [TipoDispositivo(**row) for row in rows]

    def extract_service_types(self, chunk_size: int) -> Iterator[list[TipoServicio]]:
        """Extrae el catalogo de tipos de servicio tecnico."""

        query = """
            SELECT
                id,
                nombre,
                descripcion,
                precio,
                activo,
                created_at
            FROM tiposservicio
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [TipoServicio(**row) for row in rows]

    def extract_brands(self, chunk_size: int) -> Iterator[list[Marca]]:
        """Extrae el catalogo maestro de marcas."""

        query = """
            SELECT
                id,
                nombre
            FROM marcas
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [Marca(**row) for row in rows]

    def extract_equipment_credentials_metadata(
        self,
        chunk_size: int,
    ) -> Iterator[list[CredencialEquipoMetadata]]:
        """Extrae metadatos de acceso omitiendo el secreto sensible."""

        query = """
            SELECT
                id,
                equipo_id,
                usuario,
                es_patron
            FROM credencialesequipo
            ORDER BY id
        """

        for rows in self._connection_factory.fetch_query_in_chunks(query, chunk_size):
            yield [CredencialEquipoMetadata(**row) for row in rows]
