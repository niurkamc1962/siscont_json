# ui/pages/modules/cobros y pagos.py
from nicegui import ui


def show():
    ui.label("Bienvenido").classes("text-2xl font-bold mb-1 text-gray-700")
    ui.label(
        "Con este proyecto podra hacer la exportacion de los "
        "datos de SISCONT para archivos JSON."
    ).classes("text-sm text-gray-500 mb-6")
    ui.separator().classes("mb-6")
