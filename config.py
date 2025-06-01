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

# UI Modules Config(modulo:icon)
MODULES = {
    "General": "home",
    "Contabilidad": "account_balance_wallet",
    "Nómina": "payments",
    "Recursos Humanos": "people_alt",
    "Cobros y Pagos": "receipt_long",
    "Inventario": "inventory_2",
    "Configuración": "settings",
}

DEFAULT_MODULE = "General"


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

    # # Obtiene la ruta absoluta de la carpeta donde está este archivo (por ejemplo, db/)
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    #
    # # Sube un nivel para llegar a la raíz del proyecto (siscont_json)
    # project_root = os.path.abspath(os.path.join(base_dir, ".."))
    #
    # # Une la ruta del proyecto con la carpeta deseada
    # output_dir = os.path.join(project_root, json_dir)
    #
    # return output_dir
