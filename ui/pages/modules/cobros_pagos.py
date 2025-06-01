# ui/pages/modules/cobros y pagos.py
from nicegui import ui


def show():
    ui.label("Módulo: cobros y pagos").classes("text-2xl font-bold mb-1 text-gray-700")
    ui.label("Bienvenido al módulo de cobros y pagos.").classes(
        "text-sm text-gray-500 mb-6"
    )
    ui.separator().classes("mb-6")

    ui.label("Aquí se gestionan todo lo relacionado con la cobros y pagos.")
    with ui.row().classes("gap-2 mt-4"):
        ui.button("Ver todas las tablas", icon="analytics").props(
            "color=secondary outline"
        )
        ui.button("Generar todos los json", icon="add_circle_outline").props(
            "color=secondary"
        )
