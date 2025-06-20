import datetime
import logging
from typing import Dict, List

from utils.jsons_utils import export_table_to_json, \
    export_table_to_json_paginated


# Para obtener las unidades de medida y poniendo alias con el nombre
# del campo en el doctype
def get_unidad_medida(db):
    doctype_name = "UOM"
    sqlserver_name = "SMGNOMENCLADORUNIDADMEDIDA"
    module_name = "Setup"

    field_mapping = [
        # Campos del doctype principal (trabajador)
        # (alias, (sql_field, doctype_field_type))
        ("uom_name", ("UMedDescrip", 'string'))
    ]
    # Construimos la cláusula SELECT
    select_clauses = [
        f"{sql_field} as {alias}" for alias, (sql_field, _) in field_mapping
    ]

    query = f"""
       SELECT
           {', '.join(select_clauses)}
        FROM SMGNOMENCLADORUNIDADMEDIDA
        WHERE UMedactiva = 1
    """

    return export_table_to_json(
        db=db,
        doctype_name=doctype_name,
        sqlserver_name=sqlserver_name,
        module_name=module_name,
        field_mapping=field_mapping,
        table_query=query
    )
