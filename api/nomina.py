# api/nomina.py
from fastapi import APIRouter
from core.database import get_db_connection
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/nomina", tags=["Nómina"])


@router.get("/empleados")
async def get_empleados():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, puesto FROM Empleados")
        columns = [column[0] for column in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return JSONResponse(content={"data": results})
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
    finally:
        conn.close()