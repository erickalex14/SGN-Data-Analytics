"""Pruebas del caso de uso de vistas semanticas."""

from novitec_dwh.contexts.executive.application.use_cases.build_semantic_views import (
    BuildSemanticViewsUseCase,
)


class FakeSemanticViewsRepository:
    """Doblez simple del repositorio de vistas semanticas."""

    def __init__(self) -> None:
        """Inicializa contadores para verificar la ejecucion."""

        self.called = 0

    def publish_views(self) -> int:
        """Simula la publicacion de vistas y devuelve el total generado."""

        self.called += 1
        return 15


def test_build_semantic_views_returns_summary() -> None:
    """Valida que el caso de uso devuelva un resumen consistente."""

    repository = FakeSemanticViewsRepository()
    use_case = BuildSemanticViewsUseCase(
        repository=repository,
        semantic_schema="sem_power_bi",
    )

    summary = use_case.execute()

    assert repository.called == 1
    assert summary.semantic_schema == "sem_power_bi"
    assert summary.published_views == 15
    assert summary.finished_at is not None
