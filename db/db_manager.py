# db/db_manager
# estructura de los modelos y estados de la aplicacion

from typing import List, Optional

from pydantic import BaseModel


class ConexionParams(BaseModel):
    host: str
    database: str
    password: str


class DBParams(BaseModel):
    host: str
    user: str
    password: str
    database: str
    port: str


class AppState:
    def __init__(self):
        self.connected: bool = False
        self.db_params: Optional[DBParams] = None
        self.db_manager: Optional[object] = None
        self.selected_module: Optional[str] = None
        self.ip_server: Optional[str] = None
        self.last_activity: Optional[str] = None
        self.reset()  # Esto asegura que los valores iniciales se apliquen

    def reset(self):
        """Reinicia todos los estados a sus valores por defecto"""
        self.connected = False
        self.db_params = None
        self.db_manager = None
        self.selected_module = None
        self.ip_server = None
        self.last_activity = None


class Relacion(BaseModel):
    tabla_padre: str
    columna_padre: str
    tabla_hija: str
    columna_hija: str


class Campo(BaseModel):
    nombre_campo: str
    tipo_campo: str
    obligatorio: bool
    nombre_campo_erp: str  # nombre del campo en el doctype
    tipo_campo_erp: str  # tipo de campo en el doctype


class TablaSQL(BaseModel):
    nombre_tabla: str  # nombre descriptivo de la tabla SQL
    nombre_tabla_sql: str  # Nombre real en la tabla SQL
    campos: List[Campo]
    nombre_doctype: str  # nombre del Doctype


class Payload(BaseModel):
    params: ConexionParams
    fields: List[Campo]


# Modelo para el endpoint de generar Doctype JSON
class GenerateDoctype(BaseModel):
    params: ConexionParams
    fields: List[Campo]
    module: Optional[str] = "Custom"
    is_child_table: Optional[bool] = False
    # custom_fields: Optional[List[Dict[str, Any]]] = None
