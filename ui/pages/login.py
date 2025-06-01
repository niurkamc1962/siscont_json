# views/connection_view.py
from datetime import datetime

from nicegui import app, ui

from config import get_settings
from db.db_connection import create_db_manager
from db.db_manager import AppState, ConexionParams


def connection_form(store: AppState):
    settings = get_settings()

    with ui.column().classes(
            "w-full h-screen flex items-center justify-center bg-gray-100 p-4"
    ):
        with ui.card().classes("w-full max-w-md p-8 shadow-2xl"):
            ui.label("Conectar a la Base de Datos").classes(
                "text-h5 text-center")

            ip_input = ui.input("IP del servidor").classes("w-full mb-4")
            database_input = ui.input("Base de datos").classes("w-full mb-4")
            password_input = ui.input(
                "Contraseña", password=True, password_toggle_button=True
            ).classes("w-full mb-4")
            error_label = ui.label("").classes("text-red-600 text-sm mb-4")

            async def connect():
                if (
                        not ip_input.value
                        or not password_input.value
                        or not database_input.value
                ):
                    error_label.text = "Todos los campos son requeridos"
                    return

                spinner = ui.spinner(size="lg", color="primary")
                spinner.classes(
                    "fixed top-0 left-0 right-0 bottom-0 m-auto z-50"
                )  # centrar el spinner en pantalla

                try:
                    params = ConexionParams(
                        host=ip_input.value,
                        password=password_input.value,
                        database=database_input.value,
                    )
                    store.db_params = params.model_dump()
                    db_manager = create_db_manager(params)

                    with db_manager.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        if cursor.fetchone()[0] == 1:
                            store.connected = True
                            store.db_manager = db_manager
                            store.ip_server = ip_input.value

                            # ✅ Guardar estado persistente del usuario
                            # Guardar en user storage (persistente durante la
                            # sesión del navegador)
                            app.storage.user["connected"] = True
                            app.storage.user["db_params"] = store.db_params
                            app.storage.user["ip_server"] = store.ip_server
                            app.storage.user["last_activity"] = (
                                datetime.now().isoformat()
                            )

                            ui.notify("Conexión exitosa!", type="positive")
                            ui.navigate.to("/")
                except Exception as e:
                    error_label.text = f"Error de conexión: {str(e)}"
                    store.reset()
                    ui.notify("Error al conectar", type="negative")
                finally:
                    spinner.delete()  # Esto oculta el spinner siempre

            ui.button("Conectar", on_click=connect).classes("mt-4 w-full")
