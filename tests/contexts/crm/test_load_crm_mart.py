"""Pruebas del caso de uso de construccion del mart CRM."""

from novitec_dwh.contexts.crm.application.use_cases.load_crm_mart import (
    LoadCrmMartUseCase,
)


class FakeCrmMartRepository:
    """Doblez de repositorio para validar la orquestacion del mart CRM."""

    def __init__(self) -> None:
        """Inicializa el estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.customer_dimension_loaded = False
        self.company_dimension_loaded = False

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

    def load_customer_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de clientes como cargada."""

        assert extraction_id == self.extraction_prepared
        self.customer_dimension_loaded = True

    def load_company_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de empresas como cargada."""

        assert extraction_id == self.extraction_prepared
        self.company_dimension_loaded = True

    def load_customer_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de clientes."""

        assert extraction_id == self.extraction_prepared
        return 120

    def load_company_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de empresas."""

        assert extraction_id == self.extraction_prepared
        return 24

    def load_customer_branch_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de sucursales."""

        assert extraction_id == self.extraction_prepared
        return 51

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve un resumen simulado de calidad de datos."""

        assert extraction_id == self.extraction_prepared
        return 6, 18


def test_execute_construye_el_mart_crm_completo() -> None:
    """Valida la orquestacion del mart CRM desde staging."""

    repository = FakeCrmMartRepository()
    use_case = LoadCrmMartUseCase(
        mart_repository=repository,
        staging_schema="stg_crm",
        mart_schema="dwh_crm",
        extraction_id="crm_20260605_140000",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "crm_20260605_140000"
    assert repository.date_dimension_loaded is True
    assert repository.customer_dimension_loaded is True
    assert repository.company_dimension_loaded is True
    assert summary.clientes == 120
    assert summary.empresas == 24
    assert summary.sucursalescliente == 51
    assert summary.reglas_calidad_ejecutadas == 6
    assert summary.hallazgos_calidad == 18
