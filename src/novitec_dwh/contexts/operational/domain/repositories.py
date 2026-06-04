"""Contratos del dominio operativo."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.operational.domain.entities import (
    OrdenEmpresa,
    OrdenEmpresaTecnico,
    OrdenPersonal,
    PreOrden,
    VistaOrden,
)


class OperationalExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio operativo."""

    def extract_order_view(self, chunk_size: int) -> Iterator[list[VistaOrden]]:
        """Extrae la vista consolidada de ordenes por lotes."""

    def extract_personal_orders(self, chunk_size: int) -> Iterator[list[OrdenPersonal]]:
        """Extrae ordenes personales por lotes."""

    def extract_company_orders(self, chunk_size: int) -> Iterator[list[OrdenEmpresa]]:
        """Extrae ordenes empresariales por lotes."""

    def extract_preorders(self, chunk_size: int) -> Iterator[list[PreOrden]]:
        """Extrae preordenes por lotes."""

    def extract_company_order_technicians(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenEmpresaTecnico]]:
        """Extrae asignaciones de tecnicos a ordenes empresariales."""
