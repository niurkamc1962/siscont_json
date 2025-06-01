# main.py
import uvicorn
from fastapi import FastAPI
from nicegui import app, ui

import config
from api import api_db, api_nomina
from ui.pages import login, main_page

from db.db_manager import AppState
store = AppState()

# Configuración FastAPI
fastapi_app = FastAPI(title=config.APP_TITLE)

# Montar APIs antes de la integracion de NiceGUI con FastAPI
# porque sino no reconoce swagguer para los endpoints
# y muestra html en lugar de formatos JSON
fastapi_app.include_router(api_db.router, prefix="/api")
fastapi_app.include_router(api_nomina.router, prefix="/nomina")

# Integración NiceGUI con FastAPI
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
def index():
    if not app.storage.user.get("connected"):
        login.connection_form(store)
    else:
        main_page.show()


# Iniciar con: uvicorn main:fastapi_app --reload

if __name__ == "__main__":
    settings = config.get_settings()
    uvicorn.run("main:fastapi_app", host="0.0.0.0", port=settings.PORT, reload=True)
