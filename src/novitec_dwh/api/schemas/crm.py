"""Esquemas Pydantic del dominio CRM para FastAPI."""

from datetime import date

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import PaginationMetadataResponse


class CrmSummaryResponse(BaseModel):
    """Representa el resumen principal del dominio CRM."""

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


class CrmCustomerResponse(BaseModel):
    """Representa un cliente expuesto por API."""

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


class CrmCompanyResponse(BaseModel):
    """Representa una empresa expuesta por API."""

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


class CrmCustomerBranchResponse(BaseModel):
    """Representa una sucursal cliente expuesta por API."""

    extraction_id: str
    source_id: int
    created_date: date | None
    branch_code: str
    branch_number: int
    branch_name: str
    province: str | None
    novitec_branch_name: str | None
    is_active: bool


class CrmCustomerListResponse(BaseModel):
    """Envuelve el listado paginado de clientes."""

    meta: PaginationMetadataResponse
    items: list[CrmCustomerResponse]


class CrmCompanyListResponse(BaseModel):
    """Envuelve el listado paginado de empresas."""

    meta: PaginationMetadataResponse
    items: list[CrmCompanyResponse]


class CrmCustomerBranchListResponse(BaseModel):
    """Envuelve el listado paginado de sucursales cliente."""

    meta: PaginationMetadataResponse
    items: list[CrmCustomerBranchResponse]
