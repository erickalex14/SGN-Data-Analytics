"""Pruebas del caso de uso de carga de inventario a staging."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from novitec_dwh.contexts.inventory.application.use_cases.load_inventory_to_staging import (
    LoadInventoryToStagingUseCase,
)
from novitec_dwh.contexts.inventory.domain.entities import (
    ListaCompra,
    OrdenRepuesto,
    ProductoInventario,
    Repuesto,
    SolicitudRepuesto,
)


class FakeInventoryRawReader:
    """Doblez de lectura raw para validar la orquestacion de inventario a staging."""

    def __init__(self) -> None:
        """Inicializa el estado simulado de la corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone el identificador simulado de la corrida."""

        return "inventory_20260605_110000"

    @property
    def run_directory(self) -> Path:
        """Expone una ruta raw simulada."""

        return Path("data/raw/inventory/inventory_20260605_110000")

    def prepare(self) -> None:
        """Marca la corrida como preparada."""

        self._prepared = True

    def read_spare_parts(self) -> Iterator[list[Repuesto]]:
        """Entrega un lote simulado de repuestos."""

        assert self._prepared is True
        yield [
            Repuesto(
                id=1,
                codigo="REP-001",
                nro_parte="NP-001",
                nombre="Pantalla 15 pulgadas",
                descripcion="Pantalla de reemplazo",
                marca_id="12",
                tipo_dispositivo_id="3",
                creado_en=datetime(2026, 6, 5, 9, 0, 0),
                modificado_en=datetime(2026, 6, 5, 10, 0, 0),
                stock=8,
                costo=Decimal("45.50"),
                bodega=1,
            )
        ]

    def read_inventory_products(self) -> Iterator[list[ProductoInventario]]:
        """Entrega un lote simulado de productos de inventario."""

        assert self._prepared is True
        yield [
            ProductoInventario(
                id=1,
                codigo="INV-001",
                descripcion="Laptop Dell",
                marca_id=12,
                tipo_dispositivo_id=3,
                tipo_dispositivo_codigo="LAP",
            )
        ]

    def read_order_spare_parts(self) -> Iterator[list[OrdenRepuesto]]:
        """Entrega un lote simulado de consumo por orden."""

        assert self._prepared is True
        yield [
            OrdenRepuesto(
                id=1,
                orden_id=10,
                repuesto_id=1,
                cantidad=2,
                fecha=datetime(2026, 6, 5, 11, 0, 0),
                usuario_id=7,
            )
        ]

    def read_spare_part_requests(self) -> Iterator[list[SolicitudRepuesto]]:
        """Entrega un lote simulado de solicitudes de repuesto."""

        assert self._prepared is True
        yield [
            SolicitudRepuesto(
                id=1,
                nro_solicitud="SR-001",
                orden_id=10,
                tecnico_id=7,
                tecnico_nombre="Tecnico 1",
                repuesto_nombre="Pantalla 15 pulgadas",
                nro_parte="NP-001",
                nro_parte_inv_id=15,
                repuesto_codigo="REP-001",
                repuesto_inv_id=1,
                link_compra="https://proveedor.local/repuesto",
                cantidad=2,
                descripcion="Equipo necesita cambio de pantalla",
                estado="Pendiente",
                motivo_rechazo=None,
                aprobado_por=None,
                repuesto_id=1,
                lista_compra_id=None,
                fecha_solicitud=date(2026, 6, 5),
                fecha_gestion=None,
                created_at=datetime(2026, 6, 5, 12, 0, 0),
            )
        ]

    def read_purchase_lists(self) -> Iterator[list[ListaCompra]]:
        """Entrega un lote simulado de listas de compra."""

        assert self._prepared is True
        yield [
            ListaCompra(
                id=1,
                nro_lista="LC-001",
                creado_por="Supervisor",
                creado_por_id=5,
                fecha_creacion=date(2026, 6, 5),
                estado="Pendiente",
                observacion="Compra semanal",
                created_at=datetime(2026, 6, 5, 13, 0, 0),
            )
        ]


class FakeInventoryStagingRepository:
    """Doblez de persistencia staging para validar el flujo de inventario."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "repuestos": 0,
            "productosinventario": 0,
            "orden_repuestos": 0,
            "solicitudesrepuesto": 0,
            "listascompra": 0,
        }

    def prepare_schema(self) -> None:
        """Marca el schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra la corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_spare_parts(self, extraction_id: str, records: list[Repuesto]) -> None:
        """Cuenta repuestos cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["repuestos"] += len(records)

    def load_inventory_products(
        self,
        extraction_id: str,
        records: list[ProductoInventario],
    ) -> None:
        """Cuenta productos de inventario cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["productosinventario"] += len(records)

    def load_order_spare_parts(
        self,
        extraction_id: str,
        records: list[OrdenRepuesto],
    ) -> None:
        """Cuenta repuestos por orden cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["orden_repuestos"] += len(records)

    def load_spare_part_requests(
        self,
        extraction_id: str,
        records: list[SolicitudRepuesto],
    ) -> None:
        """Cuenta solicitudes de repuesto cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["solicitudesrepuesto"] += len(records)

    def load_purchase_lists(self, extraction_id: str, records: list[ListaCompra]) -> None:
        """Cuenta listas de compra cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["listascompra"] += len(records)


def test_execute_carga_correctamente_el_dominio_de_inventario_en_staging() -> None:
    """Valida la orquestacion completa de la carga de inventario a staging."""

    raw_reader = FakeInventoryRawReader()
    staging_repository = FakeInventoryStagingRepository()
    use_case = LoadInventoryToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_inventory",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "inventory_20260605_110000"
    assert staging_repository.loaded_counts["repuestos"] == 1
    assert staging_repository.loaded_counts["productosinventario"] == 1
    assert staging_repository.loaded_counts["orden_repuestos"] == 1
    assert staging_repository.loaded_counts["solicitudesrepuesto"] == 1
    assert staging_repository.loaded_counts["listascompra"] == 1
    assert summary.schema_name == "stg_inventory"
    assert summary.repuestos == 1
    assert summary.productosinventario == 1
    assert summary.orden_repuestos == 1
    assert summary.solicitudesrepuesto == 1
    assert summary.listascompra == 1
