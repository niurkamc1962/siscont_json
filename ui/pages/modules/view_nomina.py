# ui/pages/modules/api_nomina.py

from nicegui import ui

TABLAS_NOMINA = {
    "Trabajadores": "empleados",
    "Contratos": "contratos",
    "Deducciones": "deducciones",
    "Pagos": "pagos",
    "Historial de Nómina": "historial_nomina",
}

# def show():
#     ui.label("Módulo: Nomina").classes("text-2xl font-bold mb-1 text-gray-700")
#     ui.label("Bienvenido al módulo de Nomina.").classes("text-sm text-gray-500 mb-6")
#     ui.separator().classes("mb-6")
#
#     ui.label("Aquí se gestionan todo lo relacionado con la nomina.")
#     with ui.row().classes("gap-2 mt-4"):
#         ui.button("Ver todas las tablas", icon="analytics").props(
#             "color=secondary outline"
#         )
#         ui.button("Generar todos los json", icon="add_circle_outline").props(
#             "color=secondary"
#         )


from services.nomina_client import TABLAS_NOMINA, obtener_datos_tabla


def show():
    ui.label("Nómina").classes("text-2xl font-bold mb-1")
    ui.label("Consulta y genera los datos por tabla").classes("text-sm mb-4")
    ui.separator()

    async def mostrar_tabla(nombre_logico: str, endpoint: str):
        data = await obtener_datos_tabla(endpoint)
        ui.notify(f"{nombre_logico} consultado correctamente.")
        with ui.dialog() as dialog:
            with ui.card():
                ui.label(f"Datos de {nombre_logico}").classes(
                    "text-lg font-bold")
                ui.label(
                    str(data)[0:1000])  # Puedes mejorar esto usando ui.table
                ui.button("Cerrar", on_click=dialog.close)
        dialog.open()

    with ui.column().classes("mt-6 gap-2"):
        for nombre_logico, endpoint in TABLAS_NOMINA.items():
            ui.button(
                f"Consultar {nombre_logico}",
                on_click=lambda n=nombre_logico, e=endpoint: mostrar_tabla(n, e)
            ).props("color=primary outline")
