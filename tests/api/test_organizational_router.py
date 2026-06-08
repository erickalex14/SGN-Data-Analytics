"""Pruebas de endpoints organizacionales de la API."""

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_organizational_query_service
from novitec_dwh.api.main import app
from novitec_dwh.contexts.organizational.application.dto_query import (
    OrganizationalGroupPermissionListItem,
    OrganizationalSummary,
    OrganizationalUserBranchListItem,
    OrganizationalUserListItem,
    OrganizationalUserPermissionListItem,
    PaginatedOrganizationalResult,
)


class FakeOrganizationalQueryService:
    """Doblez de servicio para probar endpoints organizacionales."""

    def __init__(self) -> None:
        """Inicializa contenedores para capturar filtros recibidos."""

        self.last_summary_filters: dict | None = None
        self.last_user_filters: dict | None = None
        self.last_user_branch_filters: dict | None = None
        self.last_group_permission_filters: dict | None = None
        self.last_user_permission_filters: dict | None = None

    def get_summary(self, **kwargs) -> OrganizationalSummary:
        """Devuelve un resumen fijo del dominio organizacional."""

        self.last_summary_filters = kwargs
        return OrganizationalSummary(
            extraction_id="organizational_20260608_220000",
            total_usuarios=24,
            usuarios_activos=20,
            usuarios_con_correo=18,
            usuarios_con_telefono=16,
            usuarios_con_acceso_nc=7,
            usuarios_con_grupo_acceso=19,
            total_asignaciones_sucursal=30,
            total_permisos_grupo=80,
            permisos_grupo_permitidos=65,
            total_permisos_usuario=12,
            permisos_usuario_permitidos=9,
        )

    def list_users(self, **kwargs) -> PaginatedOrganizationalResult[OrganizationalUserListItem]:
        """Devuelve una pagina fija de usuarios internos."""

        self.last_user_filters = kwargs
        return PaginatedOrganizationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OrganizationalUserListItem(
                    extraction_id="organizational_20260608_220000",
                    source_id=10,
                    user_login="aperez",
                    user_name="Andrea Perez",
                    role_name="Administradora",
                    city_name="Quito",
                    access_group_name="Administracion",
                    has_phone=True,
                    has_email=True,
                    can_access_nc=True,
                    is_active=True,
                    has_access_group=True,
                )
            ],
        )

    def list_user_branches(
        self, **kwargs
    ) -> PaginatedOrganizationalResult[OrganizationalUserBranchListItem]:
        """Devuelve una pagina fija de asignaciones usuario-sucursal."""

        self.last_user_branch_filters = kwargs
        return PaginatedOrganizationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OrganizationalUserBranchListItem(
                    extraction_id="organizational_20260608_220000",
                    source_id=5,
                    user_id=10,
                    user_login="aperez",
                    user_name="Andrea Perez",
                    branch_id=3,
                    branch_number=3,
                    city_name="Quito",
                    sequential_code="001-003",
                )
            ],
        )

    def list_group_permissions(
        self, **kwargs
    ) -> PaginatedOrganizationalResult[OrganizationalGroupPermissionListItem]:
        """Devuelve una pagina fija de permisos de grupo."""

        self.last_group_permission_filters = kwargs
        return PaginatedOrganizationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OrganizationalGroupPermissionListItem(
                    extraction_id="organizational_20260608_220000",
                    source_id=20,
                    group_id=4,
                    group_name="Administracion",
                    module_name="notas_credito",
                    action_name="aprobar",
                    is_allowed=True,
                    is_superadmin=False,
                )
            ],
        )

    def list_user_permissions(
        self, **kwargs
    ) -> PaginatedOrganizationalResult[OrganizationalUserPermissionListItem]:
        """Devuelve una pagina fija de permisos de usuario."""

        self.last_user_permission_filters = kwargs
        return PaginatedOrganizationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OrganizationalUserPermissionListItem(
                    extraction_id="organizational_20260608_220000",
                    source_id=30,
                    created_date=None,
                    user_id=10,
                    user_login="aperez",
                    user_name="Andrea Perez",
                    module_name="dashboard",
                    action_name="ver",
                    is_allowed=True,
                )
            ],
        )


def test_get_organizational_summary() -> None:
    """Valida la respuesta del endpoint de resumen organizacional."""

    app.dependency_overrides[get_organizational_query_service] = (
        lambda: FakeOrganizationalQueryService()
    )
    client = TestClient(app)

    response = client.get("/api/v1/organizational/summary")

    assert response.status_code == 200
    assert response.json()["total_usuarios"] == 24

    app.dependency_overrides.clear()


def test_list_organizational_users_with_filters() -> None:
    """Valida filtros y respuesta del listado de usuarios."""

    fake_service = FakeOrganizationalQueryService()
    app.dependency_overrides[get_organizational_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/organizational/users",
        params={
            "limit": 10,
            "offset": 5,
            "search": "Andrea",
            "role_name": "Admin",
            "branch_city": "Quito",
            "access_group_name": "Administracion",
            "is_active": "true",
            "can_access_nc": "true",
            "has_email": "true",
            "has_phone": "true",
            "sort_by": "user_login",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["user_login"] == "aperez"
    assert fake_service.last_user_filters == {
        "limit": 10,
        "offset": 5,
        "search": "Andrea",
        "role_name": "Admin",
        "branch_city": "Quito",
        "access_group_name": "Administracion",
        "is_active": True,
        "can_access_nc": True,
        "has_email": True,
        "has_phone": True,
        "sort_by": "user_login",
        "sort_dir": "desc",
    }

    app.dependency_overrides.clear()


def test_list_organizational_group_permissions_with_filters() -> None:
    """Valida filtros y respuesta del listado de permisos de grupo."""

    fake_service = FakeOrganizationalQueryService()
    app.dependency_overrides[get_organizational_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/organizational/group-permissions",
        params={
            "limit": 12,
            "offset": 2,
            "group_name": "Admin",
            "module_name": "notas",
            "action_name": "aprobar",
            "is_allowed": "true",
            "is_superadmin": "false",
            "sort_by": "module_name",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["module_name"] == "notas_credito"
    assert fake_service.last_group_permission_filters == {
        "limit": 12,
        "offset": 2,
        "group_name": "Admin",
        "module_name": "notas",
        "action_name": "aprobar",
        "is_allowed": True,
        "is_superadmin": False,
        "sort_by": "module_name",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_organizational_user_permissions_with_filters() -> None:
    """Valida filtros y respuesta del listado de permisos de usuario."""

    fake_service = FakeOrganizationalQueryService()
    app.dependency_overrides[get_organizational_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/organizational/user-permissions",
        params={
            "limit": 8,
            "offset": 1,
            "user_id": 10,
            "user_login": "aperez",
            "module_name": "dash",
            "action_name": "ver",
            "is_allowed": "true",
            "sort_by": "user_name",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["user_login"] == "aperez"
    assert fake_service.last_user_permission_filters == {
        "limit": 8,
        "offset": 1,
        "user_id": 10,
        "user_login": "aperez",
        "module_name": "dash",
        "action_name": "ver",
        "is_allowed": True,
        "sort_by": "user_name",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()
