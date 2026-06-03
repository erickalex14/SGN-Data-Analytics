# Novitec DWH

Base inicial del proyecto para construir el pipeline ETL y la API REST del Data Warehouse de soporte tecnico.

## Arquitectura propuesta

Se adopta una arquitectura por capas con enfoque DDD ligero:

- `contexts/`: contextos de negocio independientes por dominio analitico.
- `domain/`: entidades y contratos del dominio.
- `application/`: casos de uso y orquestacion de reglas.
- `infrastructure/`: conectores, repositorios y adaptadores tecnicos.
- `api/`: capa de presentacion HTTP con FastAPI.
- `etl/`: puntos de entrada para ejecuciones batch del pipeline.
- `core/`: configuracion, logging y ensamblado transversal.
- `shared/`: contratos y componentes reutilizables.

## Estructura base

```text
src/novitec_dwh
|-- api
|-- contexts
|   `-- financial
|       |-- application
|       |-- domain
|       `-- infrastructure
|-- core
|-- etl
`-- shared
```

## Primer alcance

El primer dominio implementado es `financial`, enfocado en:

- `solicitudesnc`
- `preciosorden`
- `notificaciones`

La extraccion inicial genera una zona `raw` en archivos Parquet por lotes y un
manifiesto JSON por corrida.

## Comandos esperados

```bash
uvicorn novitec_dwh.api.main:app --reload
python -m novitec_dwh.etl.orchestration.run_financial_extraction
python -m novitec_dwh.etl.orchestration.run_financial_staging_load
pytest
```
