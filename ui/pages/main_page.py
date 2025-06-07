# ui/pages/main_page.py
from nicegui import app, ui

from config import DEFAULT_MODULE
from ui.components import header, sidebar
from ui.pages.modules import (cobros_pagos_view, contabilidad_view,
                              general_view, inventario_view,
                              nomina_view, recursos_humanos_view)


# Definimos la función show_module_content como "refrescable"
# Esto significa que podemos llamarla con .refresh() para que NiceGUI la redibuje
@ui.refreshable
def show_module_content(module_name: str):
    """
    Renderiza el contenido del módulo seleccionado.
    Esta función es refrescable, lo que permite actualizar solo esta sección.
    """
    # print(f"DEBUG: Renderizando contenido para: {module_name}")

    # Limpiamos el contenido existente dentro de este contenedor refrescable
    # NiceGUI lo maneja automáticamente con @ui.refreshable,
    # pero a veces es útil tenerlo explícito o para depuración.
    # No necesitamos un div con ID aquí, NiceGUI gestiona el contenedor.

    if module_name == "General":
        general_view.show()
    elif module_name == "Contabilidad":
        contabilidad_view.show()
    elif module_name == "Nómina":
        nomina_view.show()
    elif module_name == "Recursos Humanos":
        recursos_humanos_view.show()
    elif module_name == "Cobros y Pagos":
        cobros_pagos_view.show()
    elif module_name == "Inventario":
        inventario_view.show()
    else:
        ui.label(f"Módulo '{module_name}' no encontrado.").classes(
            "text-red-500 text-lg"
        )


def show():
    """
    Función principal que construye la interfaz de usuario de la página principal.
    """
    # Obtiene el módulo actual del almacenamiento de usuario'
    current_module = app.storage.user.get("current_view", DEFAULT_MODULE)

    # Crea el encabezado de la aplicación
    header.create_header(
        server_ip=app.storage.user.get("server_ip_display", ""),
        on_logout=handle_logout
    )

    # Área principal de contenido (barra lateral + contenido del módulo)
    with ui.row().classes("w-full h-[calc(100vh-4rem)]"):
        # Crea la barra lateral
        sidebar.create_sidebar(
            selected_module=current_module, on_module_select=change_module
        )

        # Contenedor para el contenido del módulo
        with ui.column().classes("flex-grow p-6 bg-slate-100 overflow-auto"):
            # Llama la función refrescable para mostrar el contenido del módulo
            show_module_content(current_module)


def handle_logout():
    """
    Maneja el cierre de sesión del usuario.
    """
    # Actualiza el estado de inicio de sesión y limpia el IP del servidor
    app.storage.user.update(
        {
            "connected": False,
            "server_ip_display": "",
            "current_view": "General",
            # Restablece la vista actual al cerrar sesión
        }
    )
    # Redirige al usuario a la página de inicio de sesión
    ui.navigate.to("/")


def change_module(module_name: str):
    """
    Cambia el módulo activo y actualiza la interfaz de usuario.
    """
    print(f"DEBUG: Intentando cambiar a módulo: {module_name}")
    # Actualiza el módulo actual en el almacenamiento de usuario
    app.storage.user["current_view"] = module_name

    # Llama al método .refresh() de la función refrescable para redibujar solo el contenido del módulo
    show_module_content.refresh(
        module_name
    )  # Pasamos el nuevo module_name a la función refrescable
    sidebar.update_active_module(module_name)
    print(f"DEBUG: Módulo cambiado a: {app.storage.user.get('current_view')}")
