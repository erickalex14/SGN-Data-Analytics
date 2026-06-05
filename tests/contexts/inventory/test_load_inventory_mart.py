"""Pruebas del caso de uso de construccion del mart de inventario."""

from novitec_dwh.contexts.inventory.application.use_cases.load_inventory_mart import (
    LoadInventoryMartUseCase,
)


class FakeInventoryMartRepository:
    """Doblez de repositorio para validar la orquestacion del mart de inventario."""

    def __init__(self) -> None:
        """Inicializa el estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.technician_dimension_loaded = False
        self.spare_part_dimension_loaded = False

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

    def load_spare_part_dimension(self, extraction_id: str) -> None:
        """Marca la dimension de repuestos como cargada."""

        assert extraction_id == self.extraction_prepared
        self.spare_part_dimension_loaded = True

    def load_spare_part_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de repuestos."""

        assert extraction_id == self.extraction_prepared
        return 2086

    def load_order_consumption_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de consumos por orden."""

        assert extraction_id == self.extraction_prepared
        return 16

    def load_spare_part_request_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de solicitudes."""

        assert extraction_id == self.extraction_prepared
        return 12

    def load_purchase_list_fact(self, extraction_id: str) -> int:
        """Devuelve un total simulado de listas de compra."""

        assert extraction_id == self.extraction_prepared
        return 4

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve un resumen simulado de calidad de datos."""

        assert extraction_id == self.extraction_prepared
        return 7, 23


def test_execute_construye_el_mart_de_inventario_completo() -> None:
    """Valida la orquestacion del mart de inventario desde staging."""

    repository = FakeInventoryMartRepository()
    use_case = LoadInventoryMartUseCase(
        mart_repository=repository,
        staging_schema="stg_inventory",
        mart_schema="dwh_inventory",
        extraction_id="inventory_20260605_110000",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "inventory_20260605_110000"
    assert repository.date_dimension_loaded is True
    assert repository.technician_dimension_loaded is True
    assert repository.spare_part_dimension_loaded is True
    assert summary.repuestos == 2086
    assert summary.consumos_orden == 16
    assert summary.solicitudes_repuesto == 12
    assert summary.listas_compra == 4
    assert summary.reglas_calidad_ejecutadas == 7
    assert summary.hallazgos_calidad == 23
