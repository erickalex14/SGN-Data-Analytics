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

## 6. Validaciones minimas

- `GET /api/v1/health`
- `GET /api/v1/financial/summary`
- `GET /api/v1/operational/summary`
- `GET /api/v1/technical/summary`
- `GET /api/v1/inventory/summary`
- `GET /api/v1/dashboard/executive`

## 7. Archivos de interes

- logs API: `logs/api.log`
- logs ETL: `logs/`
- raw financiero: `data/raw/financial/`
- raw operativo: `data/raw/operational/`
- raw tecnico: `data/raw/technical/`
- raw inventario: `data/raw/inventory/`

## 8. Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest tests\api -q
```
