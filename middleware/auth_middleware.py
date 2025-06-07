# middleware/auth_middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse

from nicegui import app

# Rutas que no requieren autenticación
UNRESTRICTED_ROUTES = {"/", "/login",
                       "/favicon.ico"}  # '/' es donde muestras el form si no
# está conectado


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Permitir rutas internas de NiceGUI o rutas no protegidas
        if (
                path.startswith("/_nicegui")
                or path in UNRESTRICTED_ROUTES
                or path.startswith("/api")  # no bloqueamos las APIs
                or path.startswith("/nomina")
        ):
            return await call_next(request)

        # Si no está autenticado, redirige a la raíz (formulario de conexión)
        if not app.storage.user.get("connected", False):
            return RedirectResponse(url="/")

        # Si está autenticado, continuar
        return await call_next(request)
