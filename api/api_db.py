from typing import Any, Dict, List

import pyodbc
from fastapi import APIRouter, FastAPI, HTTPException

from db.db_connection import create_db_manager
from db.db_manager import ConexionParams, GenerateDoctype, Payload

# from db.doctype_generator import generate_frappe_doctype

router = APIRouter()


@router.get("/", tags=["Root"])
async def hello():
    return {"message": "Hello, FastAPI + NiceGUI"}


@router.post("/conectar-params", tags=["Database"])
async def conectar_parametros(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            tables = db.get_all_tables()
            table_count = len(tables)
            return {"tables": tables, "table_count": table_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tables", tags=["Database"], response_model=Dict[str, Any])
async def get_tables_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            return db.get_all_tables()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/table-structure/{table_name}", tags=["Database"])
async def get_table_structure_endpoint(table_name: str, params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            structure = db.get_table_structure(table_name)
            if not structure:
                raise HTTPException(status_code=404, detail="Tabla no encontrada")
            return {"table_name": table_name, "columns": structure}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/table-data/{table_name}", tags=["Database"])
async def get_table_data_endpoint(table_name: str, payload: Payload):
    try:
        with create_db_manager(payload.params) as db:
            fields = [field.nombre_campo for field in payload.fields]
            return db.export_table_to_json(table_name=table_name, fields=fields)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al procesar la tabla {table_name}: {str(e)}"
        )


@router.post(
    "/table-relation/{table_name}",
    tags=["Database"],
    response_model=List[Dict[str, Any]],
)
async def get_table_relation_endpoint(table_name: str, params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            relations = db.get_table_relations(table_name)
            return relations or []
    except pyodbc.Error as e:
        raise HTTPException(status_code=400, detail=f"Error de base de datos: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener relaciones para {table_name}: {str(e)}",
        )


@router.post("/all-relation", tags=["Database"], response_model=List[Dict])
async def get_all_relation_endpoint(params: ConexionParams):
    try:
        with create_db_manager(params) as db:
            return db.get_all_relations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/generate-doctype-json/{table_name}", tags=["Database"])
# async def generate_doctype_json(table_name: str, payload: GenerateDoctype):
#     try:
#         with create_db_manager(payload.params) as db:
#             structure = db.get_table_structure(table_name)
#             if not structure:
#                 raise HTTPException(status_code=404, detail="Tabla no encontrada")
#
#             output_path = generate_frappe_doctype(table_name, structure)
#             return {
#                 "message": f"Archivo generado correctamente: {output_path}",
#                 "table": table_name,
#                 "path": output_path,
#             }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error al generar el JSON para {table_name}: {str(e)}",
#         )
