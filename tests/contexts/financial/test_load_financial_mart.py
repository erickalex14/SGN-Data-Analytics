"""Pruebas del caso de uso de construccion del mart financiero."""

from novitec_dwh.contexts.financial.application.use_cases.load_financial_mart import (
    LoadFinancialMartUseCase,
)


class FakeFinancialMartRepository:
    """Doblez de repositorio para validar la orquestacion del mart."""

    def __init__(self) -> None:
        """Inicializa el estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.technician_dimension_loaded = False

    def prepare_schema(self) -> None:
        """Marca la estructura como preparada."""

        self.schema_prepared = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Marca la corrida como preparada."""

        self.extraction_prepared = extraction_id

    def load_date_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de fechas como cargada."""

        assert extraction_id == self.extraction_prepared
        self.date_dimension_loaded = True

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de tecnicos como cargada."""

        assert extraction_id == self.extraction_prepared
        self.technician_dimension_loaded = True

    def load_credit_note_request_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de solicitudes."""

        assert extraction_id == self.extraction_prepared
        return 226

    def load_order_price_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de ingresos."""

        assert extraction_id == self.extraction_prepared
        return 39

    def load_credit_note_notification_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de notificaciones."""

        assert extraction_id == self.extraction_prepared
        return 831

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve un resumen simulado de calidad de datos."""

        assert extraction_id == self.extraction_prepared
        return 7, 12


def test_execute_construye_el_mart_financiero_completo() -> None:
    """Valida la orquestacion del mart financiero desde staging."""

    repository = FakeFinancialMartRepository()
    use_case = LoadFinancialMartUseCase(
        mart_repository=repository,
        staging_schema="stg_financial",
        mart_schema="dwh_financial",
        extraction_id="financial_20260603_204252",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "financial_20260603_204252"
    assert repository.date_dimension_loaded is True
    assert repository.technician_dimension_loaded is True
    assert summary.solicitudes_nc == 226
    assert summary.precios_orden == 39
    assert summary.notificaciones == 831
    assert summary.reglas_calidad_ejecutadas == 7
    assert summary.hallazgos_calidad == 12
