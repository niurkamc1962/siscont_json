# main.py
from fastapi import FastAPI
from nicegui import app, ui
from ui.pages import login, main_page
from api import contabilidad, nomina
import config

# Configuración FastAPI
fastapi_app = FastAPI(title=config.APP_TITLE)

# Integración NiceGUI con FastAPI
ui.run_with(
    fastapi_app,
    storage_secret=config.STORAGE_SECRET,
    title=config.APP_TITLE,
    dark=False,
    language='es'
)

# Montar APIs
fastapi_app.include_router(contabilidad.router)
fastapi_app.include_router(nomina.router)


# Configurar rutas UI
@ui.page('/')
def index():
    if not app.storage.user.get('logged_in'):
        login.show()
    else:
        main_page.show()

# Iniciar con: uvicorn main:fastapi_app --reload