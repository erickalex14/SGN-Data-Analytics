"""Pruebas del caso de uso de extraccion de inventario."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal

from novitec_dwh.contexts.inventory.application.use_cases.extract_inventory_domain import (
    ExtractInventoryDomainUseCase,
)
from novitec_dwh.contexts.inventory.domain.entities import (
    ListaCompra,
    OrdenRepuesto,
    ProductoInventario,
    Repuesto,
    SolicitudRepuesto,
)
from novitec_dwh.contexts.inventory.infrastructure.filesystem_inventory_extraction_sink import (
    FilesystemInventoryExtractionSink,
)


class FakeInventoryExtractionRepository:
    """Doblez de pruebas para validar el flujo del caso de uso de inventario."""

    def extract_spare_parts(self, chunk_size: int) -> Iterator[list[Repuesto]]:
        """Devuelve un unico lote simulado de repuestos."""

        _ = chunk_size
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

    def extract_inventory_products(self, chunk_size: int) -> Iterator[list[ProductoInventario]]:
        """Devuelve un unico lote simulado de productos de inventario."""

        _ = chunk_size
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

    def extract_order_spare_parts(self, chunk_size: int) -> Iterator[list[OrdenRepuesto]]:
        """Devuelve un unico lote simulado de consumo por orden."""

        _ = chunk_size
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

    def extract_spare_part_requests(self, chunk_size: int) -> Iterator[list[SolicitudRepuesto]]:
        """Devuelve un unico lote simulado de solicitudes de repuesto."""

        _ = chunk_size
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

    def extract_purchase_lists(self, chunk_size: int) -> Iterator[list[ListaCompra]]:
        """Devuelve un unico lote simulado de listas de compra."""

        _ = chunk_size
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


def test_execute_resume_correctamente_los_registros(tmp_path) -> None:
    """Valida que el caso de uso de inventario acumule el volumen total por entidad."""

    repository = FakeInventoryExtractionRepository()
    sink = FilesystemInventoryExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractInventoryDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.repuestos == 1
    assert summary.repuestos_chunks == 1
    assert summary.productosinventario == 1
    assert summary.productosinventario_chunks == 1
    assert summary.orden_repuestos == 1
    assert summary.orden_repuestos_chunks == 1
    assert summary.solicitudesrepuesto == 1
    assert summary.solicitudesrepuesto_chunks == 1
    assert summary.listascompra == 1
    assert summary.listascompra_chunks == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
