"""Pruebas del caso de uso de extraccion de garantias."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal

from novitec_dwh.contexts.warranty.application.use_cases.extract_warranty_domain import (
    ExtractWarrantyDomainUseCase,
)
from novitec_dwh.contexts.warranty.domain.entities import (
    CentroAutorizadoServicio,
    OrdenGarantiaEmpresa,
    OrdenGarantiaPersonal,
    UsuarioCasAsignacion,
)
from novitec_dwh.contexts.warranty.infrastructure.filesystem_warranty_extraction_sink import (
    FilesystemWarrantyExtractionSink,
)


class FakeWarrantyExtractionRepository:
    """Doblez de pruebas para validar el flujo del caso de uso de garantias."""

    def extract_service_centers(
        self,
        chunk_size: int,
    ) -> Iterator[list[CentroAutorizadoServicio]]:
        """Devuelve un unico lote simulado de CAS."""

        _ = chunk_size
        yield [
            CentroAutorizadoServicio(
                id=1,
                nombre="CAS Demo",
                prefijo="CAS",
                marca="HP",
                telefono="022000000",
                correo="cas@demo.com",
                direccion="Av. Central",
                ciudad="Quito",
                contacto="Soporte",
                notas="Centro de prueba",
                activo=True,
                creado_en=datetime(2026, 6, 8, 8, 0, 0),
                actualizado_en=datetime(2026, 6, 8, 9, 0, 0),
            )
        ]

    def extract_user_assignments(
        self,
        chunk_size: int,
    ) -> Iterator[list[UsuarioCasAsignacion]]:
        """Devuelve un unico lote simulado de asignaciones usuario CAS."""

        _ = chunk_size
        yield [
            UsuarioCasAsignacion(
                id=1,
                usuario_id=7,
                usuario_login="1726664749",
                usuario_nombre="Tecnico Master",
                cas_id=1,
            )
        ]

    def extract_personal_warranty_orders(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenGarantiaPersonal]]:
        """Devuelve un unico lote simulado de ordenes personales con garantia."""

        _ = chunk_size
        yield [
            OrdenGarantiaPersonal(
                id=10,
                nro_orden="ORD-001",
                cliente_id=1,
                equipo_id=5,
                tecnico_id=7,
                sucursal_id=2,
                fecha_de_ingreso=datetime(2026, 6, 8, 10, 0, 0),
                estado_orden="Pendiente",
                estado_garantia="Enviado",
                garantia_tipo="externa",
                garantia_cas="CAS Demo",
                cas_id=1,
                cas_fecha_envio=date(2026, 6, 9),
                cas_fecha_retorno=None,
                cas_numero_caso="CAS-100",
                fecha_prometido=date(2026, 6, 15),
                fecha_entrega=None,
                fecha_finalizacion=None,
            )
        ]

    def extract_company_warranty_orders(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenGarantiaEmpresa]]:
        """Devuelve un unico lote simulado de ordenes empresariales con CAS."""

        _ = chunk_size
        yield [
            OrdenGarantiaEmpresa(
                id=20,
                nro_orden="EMP-001",
                empresa_id=3,
                equipo_id=5,
                tecnico_id=7,
                sucursal_id=2,
                cas_id=1,
                fecha_ingreso=datetime(2026, 6, 8, 11, 0, 0),
                fecha_prometido=date(2026, 6, 16),
                estado="Abierta",
                valor_hora=Decimal("25.00"),
                horas_trabajadas=Decimal("2.50"),
                nro_ticket="TK-001",
            )
        ]


def test_execute_resume_correctamente_los_registros(tmp_path) -> None:
    """Valida que el caso de uso de garantias acumule el volumen total por entidad."""

    repository = FakeWarrantyExtractionRepository()
    sink = FilesystemWarrantyExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractWarrantyDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.cas == 1
    assert summary.cas_chunks == 1
    assert summary.usuariocas == 1
    assert summary.usuariocas_chunks == 1
    assert summary.ordenes_garantia == 1
    assert summary.ordenes_garantia_chunks == 1
    assert summary.ordenesempresas_garantia == 1
    assert summary.ordenesempresas_garantia_chunks == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
