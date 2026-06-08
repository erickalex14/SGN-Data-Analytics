"""Contratos de aplicacion para la carga de garantias a staging."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from novitec_dwh.contexts.warranty.domain.entities import (
    CentroAutorizadoServicio,
    OrdenGarantiaEmpresa,
    OrdenGarantiaPersonal,
    UsuarioCasAsignacion,
)


class WarrantyRawReader(Protocol):
    """Contrato para leer datasets de garantias desde la zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida la corrida raw objetivo."""

    def read_service_centers(self) -> Iterator[list[CentroAutorizadoServicio]]:
        """Lee centros autorizados de servicio desde raw por lotes."""

    def read_user_assignments(self) -> Iterator[list[UsuarioCasAsignacion]]:
        """Lee asignaciones de usuario CAS desde raw por lotes."""

    def read_personal_warranty_orders(self) -> Iterator[list[OrdenGarantiaPersonal]]:
        """Lee ordenes personales de garantia desde raw por lotes."""

    def read_company_warranty_orders(self) -> Iterator[list[OrdenGarantiaEmpresa]]:
        """Lee ordenes empresariales asociadas a CAS desde raw por lotes."""


class WarrantyStagingRepository(Protocol):
    """Contrato para persistir el dominio de garantias en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura de garantias requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa el estado necesario para una corrida concreta."""

    def load_service_centers(
        self,
        extraction_id: str,
        records: list[CentroAutorizadoServicio],
    ) -> None:
        """Carga centros autorizados de servicio en staging."""

    def load_user_assignments(
        self,
        extraction_id: str,
        records: list[UsuarioCasAsignacion],
    ) -> None:
        """Carga asignaciones usuario CAS en staging."""

    def load_personal_warranty_orders(
        self,
        extraction_id: str,
        records: list[OrdenGarantiaPersonal],
    ) -> None:
        """Carga ordenes personales con garantia en staging."""

    def load_company_warranty_orders(
        self,
        extraction_id: str,
        records: list[OrdenGarantiaEmpresa],
    ) -> None:
        """Carga ordenes empresariales con CAS en staging."""
