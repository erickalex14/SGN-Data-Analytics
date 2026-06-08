"""Pruebas del caso de uso de construccion del mart organizacional."""

from novitec_dwh.contexts.organizational.application.use_cases.load_organizational_mart import (
    LoadOrganizationalMartUseCase,
)


class FakeOrganizationalMartRepository:
    """Doblez de repositorio para validar orquestacion del mart organizacional."""

    def __init__(self) -> None:
        """Inicializa estado de ejecucion simulado."""

        self.schema_prepared = False
        self.extraction_prepared: str | None = None
        self.date_dimension_loaded = False
        self.branch_dimension_loaded = False
        self.role_dimension_loaded = False
        self.access_group_dimension_loaded = False
        self.user_dimension_loaded = False

    def prepare_schema(self) -> None:
        """Marca estructura como preparada."""

        self.schema_prepared = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Marca corrida como preparada."""

        self.extraction_prepared = extraction_id

    def load_date_dimension(self, extraction_id: str) -> None:
        """Marca dimension de fechas como cargada."""

        assert extraction_id == self.extraction_prepared
        self.date_dimension_loaded = True

    def load_branch_dimension(self, extraction_id: str) -> None:
        """Marca dimension de sucursales como cargada."""

        assert extraction_id == self.extraction_prepared
        self.branch_dimension_loaded = True

    def load_role_dimension(self, extraction_id: str) -> None:
        """Marca dimension de roles como cargada."""

        assert extraction_id == self.extraction_prepared
        self.role_dimension_loaded = True

    def load_access_group_dimension(self, extraction_id: str) -> None:
        """Marca dimension de grupos como cargada."""

        assert extraction_id == self.extraction_prepared
        self.access_group_dimension_loaded = True

    def load_user_dimension(self, extraction_id: str) -> None:
        """Marca dimension de usuarios como cargada."""

        assert extraction_id == self.extraction_prepared
        self.user_dimension_loaded = True

    def load_user_fact(self, extraction_id: str) -> int:
        """Devuelve total simulado de usuarios."""

        assert extraction_id == self.extraction_prepared
        return 28

    def load_user_branch_fact(self, extraction_id: str) -> int:
        """Devuelve total simulado de usuario sucursal."""

        assert extraction_id == self.extraction_prepared
        return 59

    def load_group_permission_fact(self, extraction_id: str) -> int:
        """Devuelve total simulado de permisos de grupo."""

        assert extraction_id == self.extraction_prepared
        return 718

    def load_user_permission_fact(self, extraction_id: str) -> int:
        """Devuelve total simulado de permisos de usuario."""

        assert extraction_id == self.extraction_prepared
        return 39

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Devuelve resumen simulado de calidad."""

        assert extraction_id == self.extraction_prepared
        return 6, 12


def test_execute_construye_mart_organizacional_completo() -> None:
    """Valida orquestacion del mart organizacional desde staging."""

    repository = FakeOrganizationalMartRepository()
    use_case = LoadOrganizationalMartUseCase(
        mart_repository=repository,
        staging_schema="stg_organizational",
        mart_schema="dwh_organizational",
        extraction_id="organizational_20260608_180000",
    )

    summary = use_case.execute()

    assert repository.schema_prepared is True
    assert repository.extraction_prepared == "organizational_20260608_180000"
    assert repository.date_dimension_loaded is True
    assert repository.branch_dimension_loaded is True
    assert repository.role_dimension_loaded is True
    assert repository.access_group_dimension_loaded is True
    assert repository.user_dimension_loaded is True
    assert summary.usuarios == 28
    assert summary.usuarios_sucursales == 59
    assert summary.permisos_grupo == 718
    assert summary.permisos_usuario == 39
    assert summary.reglas_calidad_ejecutadas == 6
    assert summary.hallazgos_calidad == 12
