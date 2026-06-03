"""Pruebas del caso de uso de carga financiera a staging."""

from collections.abc import Iterator
from pathlib import Path

from novitec_dwh.contexts.financial.application.use_cases.load_financial_to_staging import (
    LoadFinancialToStagingUseCase,
)
from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)


class FakeFinancialRawReader:
    """Doblez de lectura raw para validar la orquestacion de staging."""

    def __init__(self) -> None:
        """Inicializa el estado simulado de la corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone el identificador simulado de la corrida."""

        return "financial_20260603_140000"

    @property
    def run_directory(self) -> Path:
        """Expone una ruta raw simulada."""

        return Path("data/raw/financial/financial_20260603_140000")

    def prepare(self) -> None:
        """Marca la corrida como preparada."""

        self._prepared = True

    def read_credit_note_requests(self) -> Iterator[list[SolicitudNotaCredito]]:
        """Entrega un lote simulado de solicitudes."""

        assert self._prepared is True
        yield [
            SolicitudNotaCredito(
                id=1,
                nro_solicitud="NC-001",
                orden_id=10,
                nro_orden="ORD-001",
                fecha_solicitud=__import__("datetime").date(2026, 6, 3),
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
        ]

    def read_order_prices(self) -> Iterator[list[PrecioOrden]]:
        """Entrega un lote simulado de precios."""

        assert self._prepared is True
        yield [
            PrecioOrden(
                id=1,
                orden_id=10,
                nro_orden="ORD-001",
                precio_estandar_id=None,
                servicio="Revision",
                precio=__import__("decimal").Decimal("12.00"),
                descripcion=None,
                creado_en=None,
                servicio_estandar=None,
                precio_estandar=None,
            )
        ]

    def read_credit_note_notifications(self) -> Iterator[list[NotificacionNotaCredito]]:
        """Entrega un lote simulado de notificaciones."""

        assert self._prepared is True
        yield [
            NotificacionNotaCredito(
                id=1,
                usuario_id=1,
                usuario_nombre="Tecnico 1",
                tipo="nc_solicitud",
                mensaje="Mensaje",
                nc_id=1,
                orden_id=10,
                nro_orden="ORD-001",
                leida=False,
                created_at=__import__("datetime").datetime(2026, 6, 3, 14, 0, 0),
            )
        ]


class FakeFinancialStagingRepository:
    """Doblez de persistencia staging para validar el flujo."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "solicitudes_nc": 0,
            "precios_orden": 0,
            "notificaciones": 0,
        }

    def prepare_schema(self) -> None:
        """Marca el schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra la corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_credit_note_requests(
        self,
        extraction_id: str,
        records: list[SolicitudNotaCredito],
    ) -> None:
        """Cuenta solicitudes cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["solicitudes_nc"] += len(records)

    def load_order_prices(self, extraction_id: str, records: list[PrecioOrden]) -> None:
        """Cuenta precios cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["precios_orden"] += len(records)

    def load_credit_note_notifications(
        self,
        extraction_id: str,
        records: list[NotificacionNotaCredito],
    ) -> None:
        """Cuenta notificaciones cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["notificaciones"] += len(records)


def test_execute_carga_correctamente_el_dominio_financiero_en_staging() -> None:
    """Valida la orquestacion completa de la carga financiera a staging."""

    raw_reader = FakeFinancialRawReader()
    staging_repository = FakeFinancialStagingRepository()
    use_case = LoadFinancialToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_financial",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "financial_20260603_140000"
    assert staging_repository.loaded_counts["solicitudes_nc"] == 1
    assert staging_repository.loaded_counts["precios_orden"] == 1
    assert staging_repository.loaded_counts["notificaciones"] == 1
    assert summary.schema_name == "stg_financial"
    assert summary.solicitudes_nc == 1
    assert summary.precios_orden == 1
    assert summary.notificaciones == 1
