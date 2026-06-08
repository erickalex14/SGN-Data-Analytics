# Novitec DWH

Pipeline ETL y API REST para el Data Warehouse del sistema de soporte tecnico de Novitec.

## Estado actual

Dominios implementados:

- `crm`
- `warranty`
- `financial`
- `operational`
- `technical`
- `inventory`
- `organizational`
- `executive` para resumen consolidado de gerencia

## Portal frontend

Se definio una linea de trabajo para un portal ejecutivo web que consumira la API y reemplazara el consumo manual principal en Power BI.

Plan:

- [docs/frontend-portal-plan.md](C:\Users\LENOVO\Desktop\Data Analytics Novitec SGN\docs\frontend-portal-plan.md)

Base tecnica creada en:

- [frontend/novitec-portal](C:\Users\LENOVO\Desktop\Data Analytics Novitec SGN\frontend\novitec-portal)

Comandos del portal:

```powershell
cd frontend\novitec-portal
corepack pnpm dev
corepack pnpm check
corepack pnpm build
```

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
|   |-- crm
|   |-- executive
|   |-- financial
|   |-- inventory
|   |-- operational
|   |-- organizational
|   |-- technical
|   `-- warranty
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
- `stg_technical`
- `dwh_technical`
- `stg_inventory`
- `dwh_inventory`
- `stg_crm`
- `dwh_crm`
- `stg_warranty`
- `dwh_warranty`
- `stg_organizational`
- `dwh_organizational`
- `sem_power_bi`

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

### Tecnico

```powershell
.\.venv\Scripts\novitec-etl-technical.exe
.\.venv\Scripts\novitec-load-technical-staging.exe
.\.venv\Scripts\novitec-load-technical-mart.exe
```

### Inventario

```powershell
.\.venv\Scripts\novitec-etl-inventory.exe
.\.venv\Scripts\novitec-load-inventory-staging.exe
.\.venv\Scripts\novitec-load-inventory-mart.exe
```

### CRM

```powershell
.\.venv\Scripts\novitec-etl-crm.exe
.\.venv\Scripts\novitec-load-crm-staging.exe
.\.venv\Scripts\novitec-load-crm-mart.exe
```

### Garantias

```powershell
.\.venv\Scripts\novitec-etl-warranty.exe
.\.venv\Scripts\novitec-load-warranty-staging.exe
.\.venv\Scripts\novitec-load-warranty-mart.exe
```

### Organizacional

```powershell
.\.venv\Scripts\novitec-etl-organizational.exe
.\.venv\Scripts\novitec-load-organizational-staging.exe
.\.venv\Scripts\novitec-load-organizational-mart.exe
```

### Vistas semanticas Power BI

```powershell
.\.venv\Scripts\novitec-build-powerbi-semantic.exe
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

### Tecnico

- `GET /api/v1/technical/summary`
- `GET /api/v1/technical/reports`
- `GET /api/v1/technical/report-photos`
- `GET /api/v1/technical/equipment`
- `GET /api/v1/technical/equipment-access`

### Inventario

- `GET /api/v1/inventory/summary`
- `GET /api/v1/inventory/spare-parts`
- `GET /api/v1/inventory/order-spare-parts`
- `GET /api/v1/inventory/spare-part-requests`
- `GET /api/v1/inventory/purchase-lists`

### CRM

- `GET /api/v1/crm/summary`
- `GET /api/v1/crm/customers`
- `GET /api/v1/crm/companies`
- `GET /api/v1/crm/customer-branches`

### Garantias

- `GET /api/v1/warranty/summary`
- `GET /api/v1/warranty/service-centers`
- `GET /api/v1/warranty/personal-orders`
- `GET /api/v1/warranty/company-orders`
- `GET /api/v1/warranty/user-assignments`

### Organizacional

- `GET /api/v1/organizational/summary`
- `GET /api/v1/organizational/users`
- `GET /api/v1/organizational/user-branches`
- `GET /api/v1/organizational/group-permissions`
- `GET /api/v1/organizational/user-permissions`

## Resumen ejecutivo

El endpoint ejecutivo consolida:

- resumen financiero
- resumen operativo
- resumen tecnico
- resumen de inventario
- resumen CRM
- resumen de garantias
- resumen organizacional
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
- auditoria de calidad en mart financiero, operativo, tecnico, inventario, CRM, garantias y organizacional

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Siguiente expansion recomendada

- vistas semanticas finales para Power BI
