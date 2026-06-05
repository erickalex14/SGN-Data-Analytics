"""Repositorio PostgreSQL para la carga del dominio tecnico a staging."""

from importlib.resources import files
from typing import Final

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
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

INFORMES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "orden_id",
    "tecnico_id",
    "antecedentes",
    "proceso",
    "conclusion",
    "recomendaciones",
    "estado_equipo",
    "fecha_informe",
    "fecha_creacion",
    "presupuesto_json",
]

INFORMEFOTOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "informe_id",
    "caption",
    "nombre_archivo",
    "tipo_mime",
    "orden_foto",
    "tiene_foto",
]

EQUIPOS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "tipo",
    "tipo_servicio_id",
    "tipo_servicio_texto",
    "marca",
    "modelo",
    "serie",
    "contrasena_equipo",
    "falla",
    "observacion",
    "fecha_facturacion",
    "producto_inventario_codigo",
]

EQUIPOSSERIES_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "equipo_id",
    "serie",
    "orden",
    "created_at",
]

TIPOSDISPOSITIVO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "codigo",
    "nombre",
]

TIPOSSERVICIO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nombre",
    "descripcion",
    "precio",
    "activo",
    "created_at",
]

MARCAS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nombre",
]

CREDENCIALESEQUIPO_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "equipo_id",
    "usuario",
    "es_patron",
]


class PostgreSQLTechnicalStagingRepository:
    """Gestiona la persistencia staging del dominio tecnico en PostgreSQL."""

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
            files("novitec_dwh.contexts.technical.infrastructure.sql")
            .joinpath("technical_staging.sql")
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
            "stg_technical_equipment_credentials",
            "stg_technical_brands",
            "stg_technical_service_types",
            "stg_technical_device_types",
            "stg_technical_equipment_series",
            "stg_technical_equipment",
            "stg_technical_report_photos",
            "stg_technical_reports",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._schema_name}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def load_reports(self, extraction_id: str, records: list[InformeTecnico]) -> None:
        """Carga informes tecnicos usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.orden_id,
                record.tecnico_id,
                record.antecedentes,
                record.proceso,
                record.conclusion,
                record.recomendaciones,
                record.estado_equipo,
                record.fecha_informe,
                record.fecha_creacion,
                record.presupuesto_json,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_reports", INFORMES_COLUMNS, rows)

    def load_report_photo_metadata(
        self,
        extraction_id: str,
        records: list[InformeFotoMetadata],
    ) -> None:
        """Carga metadatos de fotos de informes usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.informe_id,
                record.caption,
                record.nombre_archivo,
                record.tipo_mime,
                record.orden_foto,
                record.tiene_foto,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_report_photos", INFORMEFOTOS_COLUMNS, rows)

    def load_equipment(self, extraction_id: str, records: list[EquipoTecnico]) -> None:
        """Carga equipos usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.tipo,
                record.tipo_servicio_id,
                record.tipo_servicio_texto,
                record.marca,
                record.modelo,
                record.serie,
                record.contrasena_equipo,
                record.falla,
                record.observacion,
                record.fecha_facturacion,
                record.producto_inventario_codigo,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_equipment", EQUIPOS_COLUMNS, rows)

    def load_equipment_series(self, extraction_id: str, records: list[EquipoSerie]) -> None:
        """Carga series de equipos usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.equipo_id,
                record.serie,
                record.orden,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_equipment_series", EQUIPOSSERIES_COLUMNS, rows)

    def load_device_types(self, extraction_id: str, records: list[TipoDispositivo]) -> None:
        """Carga tipos de dispositivo usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.codigo,
                record.nombre,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_device_types", TIPOSDISPOSITIVO_COLUMNS, rows)

    def load_service_types(self, extraction_id: str, records: list[TipoServicio]) -> None:
        """Carga tipos de servicio usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nombre,
                record.descripcion,
                record.precio,
                record.activo,
                record.created_at,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_service_types", TIPOSSERVICIO_COLUMNS, rows)

    def load_brands(self, extraction_id: str, records: list[Marca]) -> None:
        """Carga marcas usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nombre,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_brands", MARCAS_COLUMNS, rows)

    def load_equipment_credentials_metadata(
        self,
        extraction_id: str,
        records: list[CredencialEquipoMetadata],
    ) -> None:
        """Carga metadatos de credenciales usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.equipo_id,
                record.usuario,
                record.es_patron,
            )
            for record in records
        ]
        self._copy_rows("stg_technical_equipment_credentials", CREDENCIALESEQUIPO_COLUMNS, rows)

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
