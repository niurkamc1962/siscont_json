# ui/pages/modules/inicio_view.py
from nicegui import ui


def show():
    ui.label("Bienvenido").classes("text-2xl font-bold mb-1 text-gray-700")
    ui.label(
        "Proyecto para la exportacion de los datos de SISCONT hacia archivos "
        "JSON."
    ).classes("text-sm text-gray-500 mb-6")
    ui.separator().classes("mb-6")
