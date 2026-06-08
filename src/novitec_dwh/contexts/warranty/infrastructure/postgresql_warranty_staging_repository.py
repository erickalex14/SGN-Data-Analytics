"""Repositorio PostgreSQL para la carga del dominio de garantias a staging."""

from importlib.resources import files
from typing import Final

from novitec_dwh.contexts.warranty.domain.entities import (
    CentroAutorizadoServicio,
    OrdenGarantiaEmpresa,
    OrdenGarantiaPersonal,
    UsuarioCasAsignacion,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

CAS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nombre",
    "prefijo",
    "marca",
    "telefono",
    "correo",
    "direccion",
    "ciudad",
    "contacto",
    "notas",
    "activo",
    "creado_en",
    "actualizado_en",
]

USUARIOCAS_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "usuario_id",
    "usuario_login",
    "usuario_nombre",
    "cas_id",
]

ORDENES_GARANTIA_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_orden",
    "cliente_id",
    "equipo_id",
    "tecnico_id",
    "sucursal_id",
    "fecha_de_ingreso",
    "estado_orden",
    "estado_garantia",
    "garantia_tipo",
    "garantia_cas",
    "cas_id",
    "cas_fecha_envio",
    "cas_fecha_retorno",
    "cas_numero_caso",
    "fecha_prometido",
    "fecha_entrega",
    "fecha_finalizacion",
]

ORDENESEMPRESAS_GARANTIA_COLUMNS: Final[list[str]] = [
    "extraction_id",
    "source_id",
    "nro_orden",
    "empresa_id",
    "equipo_id",
    "tecnico_id",
    "sucursal_id",
    "cas_id",
    "fecha_ingreso",
    "fecha_prometido",
    "estado",
    "valor_hora",
    "horas_trabajadas",
    "nro_ticket",
]


class PostgreSQLWarrantyStagingRepository:
    """Gestiona la persistencia staging del dominio de garantias en PostgreSQL."""

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
            files("novitec_dwh.contexts.warranty.infrastructure.sql")
            .joinpath("warranty_staging.sql")
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
            "stg_warranty_company_orders",
            "stg_warranty_personal_orders",
            "stg_warranty_user_assignments",
            "stg_warranty_service_centers",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._schema_name}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def load_service_centers(
        self,
        extraction_id: str,
        records: list[CentroAutorizadoServicio],
    ) -> None:
        """Carga centros autorizados de servicio usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nombre,
                record.prefijo,
                record.marca,
                record.telefono,
                record.correo,
                record.direccion,
                record.ciudad,
                record.contacto,
                record.notas,
                record.activo,
                record.creado_en,
                record.actualizado_en,
            )
            for record in records
        ]
        self._copy_rows("stg_warranty_service_centers", CAS_COLUMNS, rows)

    def load_user_assignments(
        self,
        extraction_id: str,
        records: list[UsuarioCasAsignacion],
    ) -> None:
        """Carga asignaciones usuario CAS usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.usuario_id,
                record.usuario_login,
                record.usuario_nombre,
                record.cas_id,
            )
            for record in records
        ]
        self._copy_rows("stg_warranty_user_assignments", USUARIOCAS_COLUMNS, rows)

    def load_personal_warranty_orders(
        self,
        extraction_id: str,
        records: list[OrdenGarantiaPersonal],
    ) -> None:
        """Carga ordenes personales con garantia usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_orden,
                record.cliente_id,
                record.equipo_id,
                record.tecnico_id,
                record.sucursal_id,
                record.fecha_de_ingreso,
                record.estado_orden,
                record.estado_garantia,
                record.garantia_tipo,
                record.garantia_cas,
                record.cas_id,
                record.cas_fecha_envio,
                record.cas_fecha_retorno,
                record.cas_numero_caso,
                record.fecha_prometido,
                record.fecha_entrega,
                record.fecha_finalizacion,
            )
            for record in records
        ]
        self._copy_rows("stg_warranty_personal_orders", ORDENES_GARANTIA_COLUMNS, rows)

    def load_company_warranty_orders(
        self,
        extraction_id: str,
        records: list[OrdenGarantiaEmpresa],
    ) -> None:
        """Carga ordenes empresariales con CAS usando COPY."""

        rows = [
            (
                extraction_id,
                record.id,
                record.nro_orden,
                record.empresa_id,
                record.equipo_id,
                record.tecnico_id,
                record.sucursal_id,
                record.cas_id,
                record.fecha_ingreso,
                record.fecha_prometido,
                record.estado,
                record.valor_hora,
                record.horas_trabajadas,
                record.nro_ticket,
            )
            for record in records
        ]
        self._copy_rows("stg_warranty_company_orders", ORDENESEMPRESAS_GARANTIA_COLUMNS, rows)

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
