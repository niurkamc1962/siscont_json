from nicegui import ui

from config import MODULES

# Diccionario global para mantener referencia a los botones del sidebar
sidebar_elements = {}


def create_sidebar(selected_module: str, on_module_select):
    """Crea la barra lateral con los módulos disponibles."""
    sidebar_elements.clear()  # Limpia referencias previas

    with ui.column().classes("w-64 bg-slate-50 border-r border-slate-200 h-full"):
        ui.label("Módulos").classes(
            "text-lg font-bold p-4 text-slate-700 border-b border-slate-200"
        )

        for module_name, icon_name in MODULES.items():
            is_selected = module_name == selected_module
            print(f"modulo seleccionado: {is_selected}")

            # Clases base y condicionales para cada botón del sidebar
            item_classes = (
                "w-full flex items-center gap-3 px-4 py-2.5 "
                "rounded-md cursor-pointer transition-all "
                "duration-150 ease-in-out"
            )
            item_classes += (
                " bg-primary text-white font-semibold shadow-sm"
                if is_selected
                else "text-slate-600 hover:bg-slate-200 hover:text-slate-800"
            )

            # Botón clickeable
            with ui.element("div").classes(item_classes).on(
                "click", lambda _, name=module_name: on_module_select(name)
            ) as btn:
                ui.icon(icon_name).classes("text-xl")
                ui.label(module_name).classes("text-sm")
                sidebar_elements[module_name] = btn  # Guarda referencia


def update_active_module(active_module: str):
    """Actualiza las clases CSS del módulo seleccionado y muestra  el estado
    activo."""
    for module_name, element in sidebar_elements.items():
        base_classes = (
            "w-full flex items-center gap-3 px-4 py-2.5 rounded-md "
            "cursor-pointer transition-all duration-150 "
            "ease-in-out"
        )
        if module_name == active_module:
            element.classes(
                replace=f"{base_classes} bg-primary text-white font-semibold "
                f"shadow-sm"
            )
        else:
            element.classes(
                replace=f"{base_classes} text-slate-600 hover:bg-slate-200 "
                f"hover:text-slate-800"
            )
