# ui/components/header.py
from nicegui import ui


def create_header(server_ip: str, on_logout):
    with ui.header(elevated=True).classes(
        "bg-primary text-white justify-between items-center px-4 h-16 shadow-md"
    ):
        ui.label(f"�️ Servidor: {server_ip if server_ip else 'N/A'}").classes(
            "font-semibold text-sm"
        )
        ui.button("Logout", on_click=on_logout, icon="logout").props(
            "flat color=white text-sm"
        )
