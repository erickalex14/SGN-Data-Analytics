"""Contratos del dominio de garantias."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.warranty.domain.entities import (
    CentroAutorizadoServicio,
    OrdenGarantiaEmpresa,
    OrdenGarantiaPersonal,
    UsuarioCasAsignacion,
)


class WarrantyExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio de garantias."""

    def extract_service_centers(
        self,
        chunk_size: int,
    ) -> Iterator[list[CentroAutorizadoServicio]]:
        """Extrae centros autorizados de servicio por lotes."""

    def extract_user_assignments(self, chunk_size: int) -> Iterator[list[UsuarioCasAsignacion]]:
        """Extrae asignaciones de usuarios internos a CAS por lotes."""

    def extract_personal_warranty_orders(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenGarantiaPersonal]]:
        """Extrae ordenes personales vinculadas a garantia o CAS por lotes."""

    def extract_company_warranty_orders(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenGarantiaEmpresa]]:
        """Extrae ordenes empresariales vinculadas a CAS por lotes."""
