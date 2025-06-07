# ui/pages/modules/contabilidad_view.py
from nicegui import ui


def show():
    ui.label("Módulo: Contabilidad").classes("text-2xl font-bold mb-1 text-gray-700")
    ui.label("Bienvenido al módulo de contabilidad.").classes(
        "text-sm text-gray-500 mb-6"
    )
    ui.separator().classes("mb-6")

    ui.label("Aquí se gestionan asientos contables, balances, y reportes financieros.")
    with ui.row().classes("gap-2 mt-4"):
        ui.button("Ver Balance General", icon="analytics").props(
            "color=secondary outline"
        )
        ui.button("Registrar Asiento", icon="add_circle_outline").props(
            "color=secondary"
        )
