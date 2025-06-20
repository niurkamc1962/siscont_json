# config.py
# Utilizando pydantic_settings.BaseSettings para cargar .env una sola vez
import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# cargando el archivo .env
load_dotenv()

# App Config
APP_TITLE = "Exportar Siscont"
STORAGE_SECRET = os.getenv("STORAGE_SECRET", "siscont-json")

PAGINATION_THRESHOLD = (
    5000  # Número de registros a partir del cual se activa la paginación
)
DEFAULT_PAGE_SIZE = 1000

# UI Modules Config(modulo:icon)
MODULES = {
    "Inicio": "home",
    "General": "dashboard",
    "Contabilidad General": "account_balance_wallet",
    "Inventarios" : "inventory_2",
    "Activos Fijos" : "precision_manufacturing",
    "Nómina": "payments",
    "Cobros y Pagos": "receipt_long",
    "Gestion Comercial Ventas": "sell",
    "Gestion Comercial Compras": "shopping_cart",
    "Recursos Humanos": "people_alt",
}

DEFAULT_MODULE = "Inicio"


class Settings(BaseSettings):
    API_BASE_URL: str
    SQL_USER: str
    SQL_PORT: int
    PORT: int
    STORAGE_SECRET: str
    JSON_OUTPUT_DIR: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Funcion para crear el directorio de los archivos JSON
def get_output_dir():
    # Intenta obtener desde la variable de entorno
    json_dir = os.getenv("JSON_OUTPUT_DIR")

    if json_dir:
        return json_dir

    # Si no está definida, se usa la ruta por defecto relativa al archivo actual
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_dir = os.path.join(base_dir, "archivos_json")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir


# funcion utilitaria para obtener la url segun el modulo
def get_module_api_url(module_name: str) -> str:
    settings = get_settings()
    base = settings.API_BASE_URL.rstrip("/")  # viene del .env como API_BASE
    return f"{base}/{module_name.lower()}"
