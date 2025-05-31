# config.py (completo)
from enum import Enum


class Environment(str, Enum):
    PROD = "production"
    DEV = "development"


# App Config
APP_TITLE = "Exportar Siscont"
STORAGE_SECRET = "MI_CLAVE_SECRETA_PARA_STORAGE_12345"
ENVIRONMENT = Environment.DEV

# Auth Config
CORRECT_SERVER_IP = "192.168.1.100"
CORRECT_USERNAME = "admin"
CORRECT_PASSWORD = "password"

# Database Config
DB_CONFIG = {
    "server": "localhost",
    "database": "erp_db",
    "username": "sa",
    "password": "your_password",
    "driver": "{ODBC Driver 17 for SQL Server}",
}

# UI Modules Config
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
