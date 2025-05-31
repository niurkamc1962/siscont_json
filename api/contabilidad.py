# api/contabilidad.py
from fastapi import APIRouter
from core.database import get_db_connection
import pyodbc

router = APIRouter(prefix="/contabilidad", tags=["Contabilidad"])


@router.get("/balance-general")
async def get_balance_general():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM BalanceGeneral")
    columns = [column[0] for column in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return {"data": results}