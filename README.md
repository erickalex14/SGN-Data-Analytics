# Novitec DWH

Pipeline ETL y API REST para el Data Warehouse del sistema de soporte tecnico de Novitec.

## Estado actual

Dominios implementados:

- `financial`
- `operational`
- `executive` para resumen consolidado de gerencia

Capas disponibles:

- extraccion `MySQL -> raw`
- carga `raw -> staging`
- transformacion y carga `staging -> mart`
- API REST sobre PostgreSQL

## Arquitectura

Se adopta arquitectura por capas con enfoque DDD ligero:

- `contexts/`: contextos por dominio analitico
- `domain/`: entidades y contratos
- `application/`: casos de uso, DTOs y servicios
- `infrastructure/`: repositorios, conectores y SQL
- `api/`: FastAPI y contratos HTTP
- `etl/`: runners batch
- `core/`: configuracion y logging
- `shared/`: componentes reutilizables

## Estructura

```text
src/novitec_dwh
|-- api
|   |-- routers
|   `-- schemas
|-- contexts
|   |-- executive
|   |-- financial
|   `-- operational
|-- core
|-- etl
`-- shared
```

## Requisitos

- Python 3.11 o superior
- `.venv` creado dentro del proyecto
- MySQL origen con acceso al sistema transaccional
- PostgreSQL destino mediante `POSTGRES_DSN`

## Configuracion

Partir de `.env.example` y completar:

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `POSTGRES_DSN`
- `API_AUTH_ENABLED`
- `API_AUTH_TOKEN`

Schemas usados actualmente:

- `stg_financial`
- `dwh_financial`
- `stg_operational`
- `dwh_operational`

## Flujo ETL

### Financiero

```powershell
.\.venv\Scripts\novitec-etl-financial.exe
.\.venv\Scripts\novitec-load-financial-staging.exe
.\.venv\Scripts\novitec-load-financial-mart.exe
```

### Operativo

```powershell
.\.venv\Scripts\novitec-etl-operational.exe
.\.venv\Scripts\novitec-load-operational-staging.exe
.\.venv\Scripts\novitec-load-operational-mart.exe
```

## API

Levantar la API:

```powershell
.\.venv\Scripts\novitec-api.exe
```

Documentacion interactiva:

- `http://127.0.0.1:8000/docs`

Autenticacion:

- si `API_AUTH_ENABLED=true`, enviar header `Authorization: Bearer <token>`

## Endpoints principales

### Salud

- `GET /api/v1/health`

### Financiero

- `GET /api/v1/financial/summary`
- `GET /api/v1/financial/credit-note-requests`
- `GET /api/v1/financial/order-prices`
- `GET /api/v1/financial/notifications`

### Operativo

- `GET /api/v1/operational/summary`
- `GET /api/v1/operational/orders`
- `GET /api/v1/operational/preorders`
- `GET /api/v1/operational/company-order-assignments`

### Ejecutivo

- `GET /api/v1/dashboard/executive`

## Resumen ejecutivo

El endpoint ejecutivo consolida:

- resumen financiero
- resumen operativo
- KPIs derivados para gerencia
- filtros aplicados en la consulta

Filtros globales disponibles:

- `date_from`
- `date_to`
- `technician_name`
- `branch_name`
- `admin_name`
- `status_name`
- `order_type`

## Calidad y observabilidad

- logs en `logs/`
- errores HTTP uniformes con `request_id`
- paginacion uniforme en listados
- auditoria de calidad en mart financiero y operativo

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Siguiente expansion recomendada

- dominio tecnico e informes
- dominio inventario y repuestos
- vistas semanticas finales para Power BI
