"""Pruebas del caso de uso de construccion del mart de garantias."""

from novitec_dwh.contexts.warranty.application.use_cases.load_warranty_mart import (
    LoadWarrantyMartUseCase,
)


class FakeWarrantyMartRepository:
    """Doblez de repositorio para validar la orquestacion del mart de garantias."""

    def __init__(self) -> None:
        """Inicializa el estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.service_center_dimension_loaded = False
        self.user_dimension_loaded = False

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

    def load_service_center_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de CAS como cargada."""

        assert extraction_id == self.extraction_prepared
        self.service_center_dimension_loaded = True

    def load_user_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de usuarios como cargada."""

        assert extraction_id == self.extraction_prepared
        self.user_dimension_loaded = True

    def load_personal_order_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de ordenes personales."""

        assert extraction_id == self.extraction_prepared
        return 85

    def load_company_order_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de ordenes empresariales."""

        assert extraction_id == self.extraction_prepared
        return 19

    def load_user_assignment_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de asignaciones."""

        assert extraction_id == self.extraction_prepared
        return 11

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve un resumen simulado de calidad de datos."""

        assert extraction_id == self.extraction_prepared
        return 6, 14


def test_execute_construye_el_mart_de_garantias_completo() -> None:
    """Valida la orquestacion del mart de garantias desde staging."""

    repository = FakeWarrantyMartRepository()
    use_case = LoadWarrantyMartUseCase(
        mart_repository=repository,
        staging_schema="stg_warranty",
        mart_schema="dwh_warranty",
        extraction_id="warranty_20260608_150000",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "warranty_20260608_150000"
    assert repository.date_dimension_loaded is True
    assert repository.service_center_dimension_loaded is True
    assert repository.user_dimension_loaded is True
    assert summary.ordenes_personales == 85
    assert summary.ordenes_empresariales == 19
    assert summary.asignaciones_usuario_cas == 11
    assert summary.reglas_calidad_ejecutadas == 6
    assert summary.hallazgos_calidad == 14
