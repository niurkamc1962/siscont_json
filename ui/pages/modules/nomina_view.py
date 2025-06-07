# ui/pages/modules/api_nomina.py
from nicegui import ui
from services.nomina_client import TABLAS_NOMINA, obtener_datos_tabla


async def mostrar_tabla(nombre_logico: str):
    """
    Shows the data of a specified table in a NiceGUI dialog.
    """
    try:
        data = await obtener_datos_tabla(nombre_logico)
        ui.notify(f"{nombre_logico} consultado correctamente.")

        if not data:
            ui.notify("No se encontraron datos para mostrar.", type="info")
            return

        columns = [{"name": key, "label": key, "field": key} for key in
                   data[0].keys()]

        with ui.dialog() as dialog:
            with ui.card().classes("w-full h-full"):
                ui.label(f"Datos de {nombre_logico}").classes(
                    "text-lg font-bold")
                ui.table(columns=columns, rows=data).classes("w-full h-full")
                ui.button("Cerrar", on_click=dialog.close)
        dialog.open()

    except Exception as e:
        ui.notify(f"Error al consultar {nombre_logico}: {e}", type="negative")
        print(f"Error al consultar {nombre_logico}: {e}")


async def exportar_json(nombre_logico: str):
    """
    Fetches data for a specified table and triggers a JSON file download.
    """
    try:
        ui.notify(f"Preparando exportación de {nombre_logico}...")
        data = await obtener_datos_tabla(nombre_logico)

        if not data:
            ui.notify(f"No hay datos para exportar en {nombre_logico}.",
                      type="warning")
            return

        json_data = json.dumps(data, indent=4,
                               ensure_ascii=False)  # Convert data to JSON
        # string

        file_name = f"{nombre_logico.replace(' ', '_').lower()}.json"  #
        # Create a clean filename

        ui.download(json_data.encode('utf-8'),
                    file_name)  # Download the JSON data
        ui.notify(
            f"Datos de {nombre_logico} exportados a '{file_name}' "
            f"correctamente.",
            type="positive")

    except Exception as e:
        ui.notify(f"Error al exportar {nombre_logico}: {e}", type="negative")
        print(f"Error al exportar {nombre_logico}: {e}")


def show():
    """
    Defines the main UI for the Nómina section, allowing users to consult and
    export table data.
    """
    ui.label("Nómina").classes("text-2xl font-bold mb-1")
    ui.label("Consulta y genera los datos por tabla").classes("text-sm mb-4")
    ui.separator()

    # Display table names and buttons
    with ui.column().classes("mt-6 gap-2 w-full"):  # Use w-full for full width
        for nombre_logico in TABLAS_NOMINA.keys():
            with ui.row().classes(
                    "items-center justify-between w-full"):  # Row for table
                # name and buttons
                ui.label(nombre_logico).classes(
                    "text-md font-semibold")  # Display the table name

                with ui.row():  # Group the buttons together
                    ui.button(
                        "Consultar",
                        on_click=lambda n=nombre_logico: mostrar_tabla(n)
                    ).props(
                        "color=primary outline size=sm")  # Added size for
                    # smaller buttons

                    ui.button(
                        "Exportar a JSON",
                        on_click=lambda n=nombre_logico: exportar_json(n)
                    ).props(
                        "color=green outline size=sm icon=cloud_download")
