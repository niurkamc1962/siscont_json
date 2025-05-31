# ui/pages/login.py
from nicegui import ui
from core import auth
from config import CORRECT_SERVER_IP, CORRECT_USERNAME, CORRECT_PASSWORD


def show():
    with ui.card().classes(
            'absolute-center w-full max-w-sm p-8 shadow-2xl rounded-xl'):
        ui.label("Iniciar Sesión").classes(
            'text-3xl font-bold self-center mb-8 text-gray-700')
        server_ip_input = ui.input("IP del Servidor",
                                   value=CORRECT_SERVER_IP).props(
            'outlined dense clearable')
        username_input = ui.input("Usuario", value=CORRECT_USERNAME).props(
            'outlined dense clearable')
        password_input = ui.input("Contraseña", value=CORRECT_PASSWORD,
                                  password=True,
                                  password_toggle_button=True).props(
            'outlined dense clearable')

        ui.button("Login", on_click=lambda: auth.attempt_login(
            server_ip_input.value,
            username_input.value,
            password_input.value
        )).props('color=primary size=lg').classes('w-full mt-6')