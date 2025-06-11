# ui/pages/modules/api_nomina.py
import asyncio

from nicegui import ui

from services.nomina_client import TABLAS_NOMINA, obtener_datos_tabla


# Muestra ventana modal con los datos de la tabla especificada
async def mostrar_tabla(nombre_logico: str):
    try:
        data = await obtener_datos_tabla(nombre_logico)
        ui.notify(f"{nombre_logico} consultado correctamente.")

        if not data:
            ui.notify("No se encontraron datos para mostrar.", type="info")
            return

        columns = [{"name": key, "label": key, "field": key, "align": "left"}
                   for key in data[0].keys()]

        # Configuración de paginación dinámica
        data_length = len(data)
        pagination = {
            "rows_per_page": min(10, data_length)
        } if data_length > 10 else {"rows_per_page": data_length}

        # Determinar ancho según cantidad de columnas
        column_count = len(columns)
        card_classes = "w-full h-full max-h-screen "
        if column_count > 8:
            card_classes += "min-w-[90vw] max-w-none"
        else:
            card_classes += "max-w-screen-xl"

        with ui.dialog() as dialog:
            with ui.card().classes(card_classes):
                ui.label(f"Datos de {nombre_logico}").classes(
                    "text-lg font-bold")

                ui.table(
                    columns=columns,
                    rows=data,
                    pagination=pagination
                ).classes("w-full h-full overflow-x-auto")

                ui.button("Cerrar", on_click=dialog.close)
        dialog.open()

    except Exception as e:
        ui.notify(f"Error al consultar {nombre_logico}: {e}", type="negative")
        print(f"Error al consultar {nombre_logico}: {e}")

# funcion que obtiene los datos de la tabla especificada
async def procesar_tabla_individual(nombre_logico: str):
    try:
        ui.notify(f"Preparando exportación de {nombre_logico}...")
        data = await obtener_datos_tabla(nombre_logico)

        if not data:
            ui.notify(f"No hay datos para exportar en {nombre_logico}.",
                      type="warning")
            return

        file_name = f"{nombre_logico.replace(' ', '_').lower()}.json"  #

        ui.notify(
            f"Datos de {nombre_logico} exportados a '{file_name}' "
            f"correctamente.",
            type="positive")

    except Exception as e:
        ui.notify(f"Error desde nomina_view al exportar {nombre_logico}: {e}",
                  type="negative")
        print(f"Error al exportar {nombre_logico}: {e}")


async def procesar_todas_tablas():
    with ui.dialog() as dialog, ui.card():
        ui.label("Exportando todas las tablas...").classes(
            "text-lg font-semibold")
        ui.spinner(size='lg', color='green')

    dialog.open()

    try:
        for nombre_logico in TABLAS_NOMINA.keys():
            await procesar_tabla_individual(
                nombre_logico)  # suponiendo que exportar_json es async
            await asyncio.sleep(0.1)  # pequeña pausa para permitir feedback UI

        dialog.close()
        ui.notify("✅ Todas las tablas fueron exportadas exitosamente",
                  type="positive")
    except Exception as e:
        dialog.close()
        ui.notify(f"❌ Error al exportar: {str(e)}", type="negative")


def show():
    ui.label("Nómina").classes("text-2xl font-bold mb-1")
    ui.label("Consulta y genera los JSON de las tablas de Nomina").classes(
        "text-sm mb-4")
    ui.separator()

    # Botón para exportar todas las tablas de NOMINA
    ui.button(
        "Exportar todas las tablas a JSON",
        on_click=lambda: procesar_todas_tablas()
        # ¡Aquí pasas TABLAS_NOMINA!
    ).props("color=blue size=md icon=cloud_download").classes("mt-4 mb-6")

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
                        "Visualizar datos",
                        on_click=lambda n=nombre_logico: mostrar_tabla(n)
                    ).props(
                        "color=primary outline size=sm")  # Added size for
                    # smaller buttons

                    ui.button(
                        "Exportar a JSON",
                        on_click=lambda
                            n=nombre_logico: procesar_tabla_individual(n)
                    ).props(
                        "color=green outline size=sm icon=cloud_download")
