# ui/pages/modules/api_nomina.py
from nicegui import ui


def show():
    ui.label("Módulo: Inventario").classes("text-2xl font-bold mb-1 text-gray-700")
    ui.label("Bienvenido al módulo de Inventario.").classes(
        "text-sm text-gray-500 mb-6"
    )
    ui.separator().classes("mb-6")

    ui.label("Aquí se procesaran todos los datos Inventarios.")
