"""Pruebas del lector de corridas financieras desde la zona raw."""

from datetime import date, datetime
from decimal import Decimal
import json

from novitec_dwh.contexts.financial.infrastructure.filesystem_financial_raw_reader import (
    FilesystemFinancialRawReader,
)
from novitec_dwh.contexts.financial.infrastructure.filesystem_financial_extraction_sink import (
    FilesystemFinancialExtractionSink,
)
from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)


def test_raw_reader_resuelve_la_corrida_mas_reciente(tmp_path) -> None:
    """Valida que el lector use la corrida mas reciente cuando no se especifica una."""

    base_path = tmp_path / "raw" / "financial"
    older_path = base_path / "financial_20260101_100000"
    older_path.mkdir(parents=True)
    (older_path / "manifest.json").write_text(
        json.dumps({"extraction_id": "financial_20260101_100000"}),
        encoding="utf-8",
    )

    sink = FilesystemFinancialExtractionSink(base_path=base_path)
    sink.start(
        extraction_id="financial_20260102_120000",
        started_at=datetime(2026, 1, 2, 12, 0, 0),
    )
    sink.write(
        dataset_name="solicitudes_nc",
        chunk_number=1,
        records=[
            SolicitudNotaCredito(
                id=1,
                nro_solicitud="NC-001",
                orden_id=10,
                nro_orden="ORD-001",
                fecha_solicitud=date(2026, 1, 2),
                asunto="Solicitud",
                detalles="Detalle",
                nombre_admin=None,
                motivo_rechazo=None,
                tecnico_nombre="Tecnico 1",
                tecnico_id=1,
                estado="Pendiente",
                creado_en=None,
                created_at=None,
            )
        ],
    )
    sink.write(
        dataset_name="precios_orden",
        chunk_number=1,
        records=[
            PrecioOrden(
                id=1,
                orden_id=10,
                nro_orden="ORD-001",
                precio_estandar_id=None,
                servicio="Revision",
                precio=Decimal("15.00"),
                descripcion=None,
                creado_en=None,
                servicio_estandar=None,
                precio_estandar=None,
            )
        ],
    )
    sink.write(
        dataset_name="notificaciones",
        chunk_number=1,
        records=[
            NotificacionNotaCredito(
                id=1,
                usuario_id=1,
                usuario_nombre="Tecnico 1",
                tipo="nc_solicitud",
                mensaje="Notificacion",
                nc_id=1,
                orden_id=10,
                nro_orden="ORD-001",
                leida=False,
                created_at=datetime(2026, 1, 2, 12, 0, 0),
            )
        ],
    )
    sink.finalize(
        summary=type(
            "Summary",
            (),
            {
                "finished_at": datetime(2026, 1, 2, 12, 10, 0),
                "solicitudes_nc": 1,
                "solicitudes_nc_chunks": 1,
                "precios_orden": 1,
                "precios_orden_chunks": 1,
                "notificaciones": 1,
                "notificaciones_chunks": 1,
            },
        )(),
    )

    reader = FilesystemFinancialRawReader(base_path=base_path)
    reader.prepare()

    solicitudes = list(reader.read_credit_note_requests())
    precios = list(reader.read_order_prices())
    notificaciones = list(reader.read_credit_note_notifications())

    assert reader.extraction_id == "financial_20260102_120000"
    assert len(solicitudes) == 1
    assert len(precios) == 1
    assert len(notificaciones) == 1
    assert solicitudes[0][0].nro_solicitud == "NC-001"
