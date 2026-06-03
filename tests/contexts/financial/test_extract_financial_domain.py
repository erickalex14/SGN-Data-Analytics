"""Pruebas del caso de uso de extraccion financiera."""

from collections.abc import Iterator

from novitec_dwh.contexts.financial.application.use_cases.extract_financial_domain import (
    ExtractFinancialDomainUseCase,
)
from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)
from novitec_dwh.contexts.financial.infrastructure.filesystem_financial_extraction_sink import (
    FilesystemFinancialExtractionSink,
)


class FakeFinancialExtractionRepository:
    """Doblez de pruebas para validar el flujo del caso de uso."""

    def extract_credit_note_requests(
        self,
        chunk_size: int,
    ) -> Iterator[list[SolicitudNotaCredito]]:
        """Devuelve un unico lote simulado de solicitudes NC."""

        _ = chunk_size

        yield [
            SolicitudNotaCredito(
                id=1,
                nro_solicitud="NC-001",
                orden_id=10,
                nro_orden="ORD-001",
                fecha_solicitud=__import__("datetime").date(2026, 6, 3),
                asunto="Solicitud de prueba",
                detalles="Detalle de prueba",
                nombre_admin=None,
                motivo_rechazo=None,
                tecnico_nombre="Tecnico 1",
                tecnico_id=1,
                estado="Pendiente",
                creado_en=None,
                created_at=None,
            )
        ]

    def extract_order_prices(self, chunk_size: int) -> Iterator[list[PrecioOrden]]:
        """Devuelve un unico lote simulado de precios por orden."""

        _ = chunk_size

        yield [
            PrecioOrden(
                id=1,
                orden_id=10,
                nro_orden="ORD-001",
                precio_estandar_id=None,
                servicio="Revision",
                precio=__import__("decimal").Decimal("15.00"),
                descripcion=None,
                creado_en=None,
                servicio_estandar=None,
                precio_estandar=None,
            )
        ]

    def extract_credit_note_notifications(
        self,
        chunk_size: int,
    ) -> Iterator[list[NotificacionNotaCredito]]:
        """Devuelve un unico lote simulado de notificaciones."""

        _ = chunk_size

        yield [
            NotificacionNotaCredito(
                id=1,
                usuario_id=1,
                usuario_nombre="Tecnico 1",
                tipo="nc_solicitud",
                mensaje="Notificacion de prueba",
                nc_id=1,
                orden_id=10,
                nro_orden="ORD-001",
                leida=False,
                created_at=__import__("datetime").datetime(2026, 6, 3, 12, 0, 0),
            )
        ]


def test_execute_resume_correctamente_los_registros(tmp_path) -> None:
    """Valida que el caso de uso acumule el volumen total por entidad."""

    repository = FakeFinancialExtractionRepository()
    sink = FilesystemFinancialExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractFinancialDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.solicitudes_nc == 1
    assert summary.solicitudes_nc_chunks == 1
    assert summary.precios_orden == 1
    assert summary.precios_orden_chunks == 1
    assert summary.notificaciones == 1
    assert summary.notificaciones_chunks == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
