"""Pruebas del caso de uso de construccion del mart operativo."""

from novitec_dwh.contexts.operational.application.use_cases.load_operational_mart import (
    LoadOperationalMartUseCase,
)


class FakeOperationalMartRepository:
    """Doblez de repositorio para validar la orquestacion del mart operativo."""

    def __init__(self) -> None:
        """Inicializa el estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.technician_dimension_loaded = False
        self.branch_dimension_loaded = False

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

    def load_branch_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de sucursales como cargada."""

        assert extraction_id == self.extraction_prepared
        self.branch_dimension_loaded = True

    def load_order_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de ordenes."""

        assert extraction_id == self.extraction_prepared
        return 1500

    def load_preorder_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de preordenes."""

        assert extraction_id == self.extraction_prepared
        return 60

    def load_company_order_assignment_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de asignaciones."""

        assert extraction_id == self.extraction_prepared
        return 12

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve un resumen simulado de calidad de datos."""

        assert extraction_id == self.extraction_prepared
        return 6, 21


def test_execute_construye_el_mart_operativo_completo() -> None:
    """Valida la orquestacion del mart operativo desde staging."""

    repository = FakeOperationalMartRepository()
    use_case = LoadOperationalMartUseCase(
        mart_repository=repository,
        staging_schema="stg_operational",
        mart_schema="dwh_operational",
        extraction_id="operational_20260604_150000",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "operational_20260604_150000"
    assert repository.date_dimension_loaded is True
    assert repository.technician_dimension_loaded is True
    assert repository.branch_dimension_loaded is True
    assert summary.ordenes == 1500
    assert summary.preordenes == 60
    assert summary.asignaciones_tecnicos == 12
    assert summary.reglas_calidad_ejecutadas == 6
    assert summary.hallazgos_calidad == 21
