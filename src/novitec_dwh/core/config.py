"""Configuracion centralizada de la aplicacion."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Define las variables de entorno requeridas por el sistema."""

    # Se agrupan las propiedades de aplicacion para estandarizar el despliegue.
    app_name: str = Field(default="Novitec DWH", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    api_auth_enabled: bool = Field(default=False, alias="API_AUTH_ENABLED")
    api_auth_token: str = Field(default="", alias="API_AUTH_TOKEN")
    log_directory: Path = Field(default=Path("logs"), alias="LOG_DIRECTORY")

    # Se controla el tamano de lote para proteger memoria en tablas pesadas.
    etl_chunk_size: int = Field(default=1000, alias="ETL_CHUNK_SIZE")
    etl_raw_base_path: Path = Field(default=Path("data/raw"), alias="ETL_RAW_BASE_PATH")
    etl_financial_extraction_id: str | None = Field(
        default=None,
        alias="ETL_FINANCIAL_EXTRACTION_ID",
    )
    etl_operational_extraction_id: str | None = Field(
        default=None,
        alias="ETL_OPERATIONAL_EXTRACTION_ID",
    )

    # Se parametriza la conexion del origen transaccional MySQL.
    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_database: str = Field(default="railway", alias="MYSQL_DATABASE")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")

    # Se parametriza la conexion del destino analitico PostgreSQL mediante DSN
    # para soportar proveedores gestionados y poolers externos.
    postgres_dsn: str = Field(default="", alias="POSTGRES_DSN")
    postgres_financial_staging_schema: str = Field(
        default="stg_financial",
        alias="POSTGRES_FINANCIAL_STAGING_SCHEMA",
    )
    postgres_financial_mart_schema: str = Field(
        default="dwh_financial",
        alias="POSTGRES_FINANCIAL_MART_SCHEMA",
    )
    postgres_operational_staging_schema: str = Field(
        default="stg_operational",
        alias="POSTGRES_OPERATIONAL_STAGING_SCHEMA",
    )
    postgres_operational_mart_schema: str = Field(
        default="dwh_operational",
        alias="POSTGRES_OPERATIONAL_MART_SCHEMA",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Entrega una instancia cacheada de configuracion."""

    return Settings()
