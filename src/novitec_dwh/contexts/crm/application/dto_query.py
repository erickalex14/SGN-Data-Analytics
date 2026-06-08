"""DTOs de consulta del dominio CRM."""

from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

ItemType = TypeVar("ItemType")


@dataclass(slots=True)
class CrmSummary:
    """Resume los principales indicadores del dominio CRM."""

    extraction_id: str | None
    total_clientes: int
    clientes_con_correo: int
    clientes_con_direccion: int
    clientes_con_contacto: int
    total_empresas: int
    empresas_con_correo: int
    empresas_con_telefono: int
    total_sucursalescliente: int
    sucursalescliente_activas: int


@dataclass(slots=True)
class CrmCustomerListItem:
    """Representa un registro consultable del hecho de clientes."""

    extraction_id: str
    source_id: int
    full_name: str
    first_name: str
    last_name: str
    identification: str
    phone_number: str
    email: str | None
    address: str | None
    has_email: bool
    has_address: bool
    has_phone: bool


@dataclass(slots=True)
class CrmCompanyListItem:
    """Representa un registro consultable del hecho de empresas."""

    extraction_id: str
    source_id: int
    company_name: str
    ruc: str
    phone_number: str | None
    email: str | None
    address: str | None
    created_date: date | None
    has_phone: bool
    has_email: bool
    has_address: bool


@dataclass(slots=True)
class CrmCustomerBranchListItem:
    """Representa un registro consultable del hecho de sucursales cliente."""

    extraction_id: str
    source_id: int
    created_date: date | None
    branch_code: str
    branch_number: int
    branch_name: str
    province: str | None
    novitec_branch_name: str | None
    is_active: bool


@dataclass(slots=True)
class PaginatedCrmResult(Generic[ItemType]):
    """Envuelve resultados paginados para listados API del dominio CRM."""

    total: int
    limit: int
    offset: int
    items: list[ItemType]
