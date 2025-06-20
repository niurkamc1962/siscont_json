# main.py
import uvicorn
from fastapi import FastAPI
from nicegui import app, ui

import config
from api import api_db, api_nomina, api_general
# from middleware.auth_middleware import AuthMiddleware
from ui.pages import login, main_page

# from db.db_manager import AppState
# store = AppState()

from state.store import store

# Configuración FastAPI
fastapi_app = FastAPI(title=config.APP_TITLE)

# Montar APIs antes de la integracion de NiceGUI con FastAPI
# porque sino no reconoce swagguer para los endpoints
# y muestra html en lugar de formatos JSON
fastapi_app.include_router(api_db.router, prefix="/api")
fastapi_app.include_router(api_nomina.router, prefix="/api/nomina")
fastapi_app.include_router(api_general.router, prefix="/api/general")

# ⛔ Agregar middleware de autenticación
# fastapi_app.add_middleware(AuthMiddleware)

# Integración NiceGUI con FastAPI pero no se inicia el servidor
ui.run_with(
    fastapi_app,
    storage_secret=config.STORAGE_SECRET,
    title=config.APP_TITLE,
    dark=False,
    language="es",
    mount_path="/",
)


# Configurar rutas UI
@ui.page("/")
async def index(client):
    if not app.storage.user.get("connected"):
        login.connection_form(store)
    else:
        main_page.show()


# Iniciar con: uvicorn main:fastapi_app --reload
# Punto de entrada que inicial el proyecto combinando FastAPI con NiceGui
if __name__ == "__main__":
    settings = config.get_settings()
    uvicorn.run("main:fastapi_app", host="0.0.0.0", port=settings.PORT,
                reload=True)
