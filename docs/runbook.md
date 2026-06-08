# Runbook Operativo

## 1. Preparar entorno

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .[dev]
```

## 2. Configurar variables

Completar `.env` con:

- credenciales MySQL
- `POSTGRES_DSN`
- token API si aplica

## 3. Ejecutar ETL financiero

```powershell
.\.venv\Scripts\novitec-etl-financial.exe
.\.venv\Scripts\novitec-load-financial-staging.exe
.\.venv\Scripts\novitec-load-financial-mart.exe
```

## 4. Ejecutar ETL operativo

```powershell
.\.venv\Scripts\novitec-etl-operational.exe
.\.venv\Scripts\novitec-load-operational-staging.exe
.\.venv\Scripts\novitec-load-operational-mart.exe
```

## 5. Levantar API

```powershell
.\.venv\Scripts\novitec-api.exe
```

## 5.1. Ejecutar ETL tecnico

```powershell
.\.venv\Scripts\novitec-etl-technical.exe
.\.venv\Scripts\novitec-load-technical-staging.exe
.\.venv\Scripts\novitec-load-technical-mart.exe
```

## 5.2. Ejecutar ETL inventario

```powershell
.\.venv\Scripts\novitec-etl-inventory.exe
.\.venv\Scripts\novitec-load-inventory-staging.exe
.\.venv\Scripts\novitec-load-inventory-mart.exe
```

## 5.3. Ejecutar ETL CRM

```powershell
.\.venv\Scripts\novitec-etl-crm.exe
.\.venv\Scripts\novitec-load-crm-staging.exe
.\.venv\Scripts\novitec-load-crm-mart.exe
```

## 5.4. Ejecutar ETL garantias

```powershell
.\.venv\Scripts\novitec-etl-warranty.exe
.\.venv\Scripts\novitec-load-warranty-staging.exe
.\.venv\Scripts\novitec-load-warranty-mart.exe
```

## 5.5. Ejecutar ETL organizacional

```powershell
.\.venv\Scripts\novitec-etl-organizational.exe
.\.venv\Scripts\novitec-load-organizational-staging.exe
.\.venv\Scripts\novitec-load-organizational-mart.exe
```

## 5.6. Publicar vistas semanticas para Power BI

```powershell
.\.venv\Scripts\novitec-build-powerbi-semantic.exe
```

## 6. Validaciones minimas

- `GET /api/v1/health`
- `GET /api/v1/financial/summary`
- `GET /api/v1/operational/summary`
- `GET /api/v1/technical/summary`
- `GET /api/v1/inventory/summary`
- `GET /api/v1/crm/summary`
- `GET /api/v1/warranty/summary`
- `GET /api/v1/organizational/summary`
- `GET /api/v1/dashboard/executive`

## 7. Archivos de interes

- logs API: `logs/api.log`
- logs ETL: `logs/`
- raw financiero: `data/raw/financial/`
- raw operativo: `data/raw/operational/`
- raw tecnico: `data/raw/technical/`
- raw inventario: `data/raw/inventory/`
- raw CRM: `data/raw/crm/`
- raw garantias: `data/raw/warranty/`
- raw organizacional: `data/raw/organizational/`
- schema semantico Power BI: `sem_power_bi`

## 8. Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests\api -q
```
