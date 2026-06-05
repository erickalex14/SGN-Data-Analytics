"""Pruebas del caso de uso de construccion del mart tecnico."""

from novitec_dwh.contexts.technical.application.use_cases.load_technical_mart import (
    LoadTechnicalMartUseCase,
)


class FakeTechnicalMartRepository:
    """Doblez de repositorio para validar la orquestacion del mart tecnico."""

    def __init__(self) -> None:
        """Inicializa el estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.technician_dimension_loaded = False
        self.service_type_dimension_loaded = False
        self.brand_dimension_loaded = False

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

    def load_service_type_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de tipos de servicio como cargada."""

        assert extraction_id == self.extraction_prepared
        self.service_type_dimension_loaded = True

    def load_brand_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de marcas como cargada."""

        assert extraction_id == self.extraction_prepared
        self.brand_dimension_loaded = True

    def load_report_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de informes."""

        assert extraction_id == self.extraction_prepared
        return 1170

    def load_report_photo_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de fotos."""

        assert extraction_id == self.extraction_prepared
        return 362

    def load_equipment_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de equipos."""

        assert extraction_id == self.extraction_prepared
        return 1643

    def load_equipment_access_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de accesos."""

        assert extraction_id == self.extraction_prepared
        return 39

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve un resumen simulado de calidad de datos."""

        assert extraction_id == self.extraction_prepared
        return 7, 18


def test_execute_construye_el_mart_tecnico_completo() -> None:
    """Valida la orquestacion del mart tecnico desde staging."""

    repository = FakeTechnicalMartRepository()
    use_case = LoadTechnicalMartUseCase(
        mart_repository=repository,
        staging_schema="stg_technical",
        mart_schema="dwh_technical",
        extraction_id="technical_20260605_090000",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "technical_20260605_090000"
    assert repository.date_dimension_loaded is True
    assert repository.technician_dimension_loaded is True
    assert repository.service_type_dimension_loaded is True
    assert repository.brand_dimension_loaded is True
    assert summary.informes == 1170
    assert summary.fotos_informes == 362
    assert summary.equipos == 1643
    assert summary.accesos_equipos == 39
    assert summary.reglas_calidad_ejecutadas == 7
    assert summary.hallazgos_calidad == 18
