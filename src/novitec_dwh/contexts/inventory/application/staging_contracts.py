"""Contratos de aplicacion para la carga de inventario a staging."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from novitec_dwh.contexts.inventory.domain.entities import (
    ListaCompra,
    OrdenRepuesto,
    ProductoInventario,
    Repuesto,
    SolicitudRepuesto,
)


class InventoryRawReader(Protocol):
    """Contrato para leer datasets de inventario desde la zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida la corrida raw objetivo."""

    def read_spare_parts(self) -> Iterator[list[Repuesto]]:
        """Lee repuestos desde raw por lotes."""

    def read_inventory_products(self) -> Iterator[list[ProductoInventario]]:
        """Lee productos de inventario desde raw por lotes."""

    def read_order_spare_parts(self) -> Iterator[list[OrdenRepuesto]]:
        """Lee repuestos instalados por orden desde raw por lotes."""

    def read_spare_part_requests(self) -> Iterator[list[SolicitudRepuesto]]:
        """Lee solicitudes de repuesto desde raw por lotes."""

    def read_purchase_lists(self) -> Iterator[list[ListaCompra]]:
        """Lee listas de compra desde raw por lotes."""


class InventoryStagingRepository(Protocol):
    """Contrato para persistir el dominio de inventario en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura de inventario requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa el estado necesario para una corrida concreta."""

    def load_spare_parts(self, extraction_id: str, records: list[Repuesto]) -> None:
        """Carga repuestos en staging."""

    def load_inventory_products(
        self,
        extraction_id: str,
        records: list[ProductoInventario],
    ) -> None:
        """Carga productos de inventario en staging."""

    def load_order_spare_parts(
        self,
        extraction_id: str,
        records: list[OrdenRepuesto],
    ) -> None:
        """Carga repuestos instalados por orden en staging."""

    def load_spare_part_requests(
        self,
        extraction_id: str,
        records: list[SolicitudRepuesto],
    ) -> None:
        """Carga solicitudes de repuesto en staging."""

    def load_purchase_lists(self, extraction_id: str, records: list[ListaCompra]) -> None:
        """Carga listas de compra en staging."""
