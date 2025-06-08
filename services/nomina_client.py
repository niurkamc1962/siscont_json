from typing import Any

import httpx

from config import get_module_api_url
from db.db_manager import ConexionParams
from state.store import \
    store  # Importas la instancia ya inicializada y compartida

# Lista de endpoints disponibles para iterar si quieres hacer algo dinámico
TABLAS_NOMINA = {
    "Trabajadores": "trabajadores",
    # "Relaciones": "relaciones-trabajadores",
    "Categorías Ocupacionales": "categorias-ocupacionales",
    "Cargos": "cargos-trabajadores",
    "Tipos Trabajadores": "tipos-trabajadores",
    "Retenciones": "tipos-retenciones",
    "Pensionados": "pensionados",
    "Tasas Destajos": "tasas_destajos",
    "Colectivos": "colectivos",
    "Departamentos": "departamentos",
    "Submayor Vacaciones": "submayor_vacaciones",
    "Submayor Salarios": "submayor_salarios_no_reclamados",
    "Pagos Trabajadores": "pagos_trabajadores",
}


# Esta función accede a la configuración de conexión global
def get_current_conexion_params() -> ConexionParams:
    print("store en get_current_conexion_params:", store.db_params)
    if not store.db_params:
        raise ValueError("No hay conexión activa configurada")

    return ConexionParams(
        host=store.db_params.host,
        password=store.db_params.password,
        database=store.db_params.database,
    )


## Este helper consulta una tabla segun el endpoint
async def obtener_datos_tabla(nombre_tabla: str,
                              modulo: str | None = None) -> Any:
    modulo = modulo or store.selected_module or 'nomina'
    endpoint = TABLAS_NOMINA[nombre_tabla]
    base_url = get_module_api_url(modulo)
    url = f"{base_url}/{endpoint}"

    conexion_params = get_current_conexion_params()
    payload = conexion_params.model_dump()

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
