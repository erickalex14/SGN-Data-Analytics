"""Contratos del dominio de inventario."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.inventory.domain.entities import (
    ListaCompra,
    OrdenRepuesto,
    ProductoInventario,
    Repuesto,
    SolicitudRepuesto,
)


class InventoryExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio de inventario."""

    def extract_spare_parts(self, chunk_size: int) -> Iterator[list[Repuesto]]:
        """Extrae el catalogo de repuestos por lotes."""

    def extract_inventory_products(self, chunk_size: int) -> Iterator[list[ProductoInventario]]:
        """Extrae el catalogo general de inventario por lotes."""

    def extract_order_spare_parts(self, chunk_size: int) -> Iterator[list[OrdenRepuesto]]:
        """Extrae repuestos instalados por orden en lotes."""

    def extract_spare_part_requests(self, chunk_size: int) -> Iterator[list[SolicitudRepuesto]]:
        """Extrae solicitudes de repuestos por lotes."""

    def extract_purchase_lists(self, chunk_size: int) -> Iterator[list[ListaCompra]]:
        """Extrae listas de compra por lotes."""
