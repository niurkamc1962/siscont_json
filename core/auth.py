# core/auth.py
from nicegui import app, ui

from config import (CORRECT_PASSWORD, CORRECT_SERVER_IP, CORRECT_USERNAME,
                    DEFAULT_MODULE)


def attempt_login(server_ip: str, username: str, password: str):
    if (
        server_ip == CORRECT_SERVER_IP
        and username == CORRECT_USERNAME
        and password == CORRECT_PASSWORD
    ):
        app.storage.user.update(
            {
                "logged_in": True,
                "server_ip_display": server_ip,  # para mostrar la ip en la vista
                "current_view": DEFAULT_MODULE,
                "server_ip": server_ip,  # guradar la ip para las conexiones
                "username": username,  # guardar el usuario
            }
        )
        ui.navigate.to("/")
    else:
        ui.notify("Credenciales incorrectas", type="negative")
