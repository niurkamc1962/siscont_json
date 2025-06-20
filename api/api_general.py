import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from db import db_general as general
from db.db_connection import create_db_manager
from db.db_manager import ConexionParams
from db.db_nomina import (get_categorias_ocupacionales,
                          get_relaciones_trabajadores, get_trabajadores)

router = APIRouter()


@router.post(
    "/unidad_medida",
    summary="Lista las unidades de medida",
    description="Muestra listado de las unidades de medida",
    tags=["GENERAL"],
)
async def get_unidad_medida_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            data = general.get_unidad_medida(db)
            return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener datos de SMGNOMENCLADORUNIDADMEDIDA:"
                   f" {str(e)}",
        )
