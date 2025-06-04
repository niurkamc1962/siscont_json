# db/jsons_utils.py
# helpers
import json
import logging
import math
import os
from collections import OrderedDict
import datetime
import decimal
from typing import List, Dict, Any, Tuple

from config import get_output_dir, DEFAULT_MODULE, PAGINATION_THRESHOLD, \
    DEFAULT_PAGE_SIZE


def save_json_file(
        doctype_name: str, data: list, module_name: str = None,
        sqlserver_name: str = None
) -> str:
    try:
        output_dir = get_output_dir()
        if not output_dir:
            raise ValueError("get_output_dir() devolvió una ruta vacía o nula")

        os.makedirs(output_dir, exist_ok=True)

        if not sqlserver_name:
            raise ValueError("sqlserver_name no puede ser None")

        output_path = os.path.join(output_dir, f"{sqlserver_name}.json")

        content = OrderedDict()
        content["doctype"] = doctype_name
        content["data"] = data

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=4, ensure_ascii=False)

        print(f"✅ JSON guardado en: {output_path}")  # Para depuración directa
        return output_path

    except Exception as e:
        print(f"❌ Error al guardar el JSON: {e}")
        raise


def serialize_value(value, field_type):
    # 1. Normalización de valores vacíos
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, (list, dict)) and len(value) == 0:
        return None

    # 2. Caso Decimal especial
    if isinstance(value, decimal.Decimal):
        if field_type == 'string':
            return str(value)
        if field_type in ('auto', 'numeric', 'float'):
            return float(value)
        if field_type == 'integer':
            return int(value)
        return value

    # 3. Lógica por tipo de campo
    try:
        if field_type == 'numeric':
            return _serialize_numeric(value)
        elif field_type == 'integer':
            return int(value)
        elif field_type == 'float':
            return float(value)
        elif field_type == 'boolean':
            return _serialize_boolean(value)
        elif field_type == 'date':
            return _serialize_date(value)
        elif field_type == 'string':
            return str(value)
        return None  # Si el tipo no es reconocido
    except Exception as e:
        logging.warning(f"Fallo al serializar: {value} ({e})")
        return None


def _serialize_numeric(value):
    if isinstance(value, (int, float, decimal.Decimal)):
        return float(value) if isinstance(value, decimal.Decimal) else value
    return float(value) if '.' in str(value) else int(value)


def _serialize_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value == 1  # Solo 1 es True, cualquier otro número es False
    val = str(value).strip().upper()
    return val in ('1', 'S', 'TRUE', 'Y', 'YES')


def _serialize_date(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    return str(value)


def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


def export_table_to_json(db, doctype_name, sqlserver_name, module_name,
                         field_mapping, table_query) -> list:
    """
    Ejecuta una consulta SQL, serializa los datos según su tipo y guarda un
    archivo JSON.
    """
    field_type_map = {alias: field_type for alias, (_, field_type) in
                      field_mapping}

    try:
        with db.cursor() as cursor:
            cursor.execute(table_query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result = [
                {
                    key: serialize_value(value, field_type_map.get(key, 'auto'))
                    for key, value in zip(columns, row)
                }
                for row in rows
            ]

            output_path = save_json_file(doctype_name, result, module_name,
                                         sqlserver_name)
            logging.info(
                f"{doctype_name}.json guardado correctamente en {output_path}")
            return result

    except Exception as e:
        logging.error(f"Error exportando {doctype_name}: {e}")
        raise


def export_table_to_json_paginated(
        db,
        doctype_name: str,
        sqlserver_name: str,
        module_name: str,
        field_mapping: List[Tuple[str, Tuple[str, str]]],
        base_query_from: str,
        order_clause: str = ""
) -> List[Dict[str, Any]]:
    """
    Exporta los resultados paginados de una tabla a un archivo JSON.

    :param db: Conexión activa a la base de datos
    :param doctype_name: Nombre del tipo de documento
    :param sqlserver_name: Nombre de la tabla origen
    :param module_name: Módulo del sistema
    :param field_mapping: Lista de mapeos de campos (alias, (sql_field, tipo))
    :param base_query_from: FROM ... WHERE ... GROUP BY ...
    :param order_clause: ORDER BY ...
    :return: Lista de diccionarios con los datos serializados
    """
    try:
        select_clauses = [
            f"{sql_field} AS {alias}" for alias, (sql_field, _) in field_mapping
        ]
        select_clause = f"SELECT {', '.join(select_clauses)}"

        select_query = f"{select_clause} {base_query_from} {order_clause}"
        # ❗ IMPORTANTE: Eliminar ORDER BY de la subconsulta del conteo
        count_query = f"SELECT COUNT(*) FROM ({select_clause} {base_query_from}) AS sub"

        field_type_map = {alias: field_type for alias, (_, field_type) in
                          field_mapping}

        with db.cursor() as cursor:
            cursor.execute(count_query)
            total_items = cursor.fetchone()[0]
            logging.warning(f"Total de registros: {total_items}")

            if total_items == 0:
                logging.warning(f"No hay registros para {doctype_name}")
                return []

            all_results = []

            if total_items > PAGINATION_THRESHOLD:
                total_pages = math.ceil(total_items / DEFAULT_PAGE_SIZE)
                logging.warning(
                    f"Paginar {total_items} registros en {total_pages} páginas."
                )
                for page_num in range(total_pages):
                    offset = page_num * DEFAULT_PAGE_SIZE
                    paginated_query = f"{select_query} OFFSET {offset} ROWS FETCH NEXT {DEFAULT_PAGE_SIZE} ROWS ONLY"
                    cursor.execute(paginated_query)
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    page_results = [
                        {
                            key: serialize_value(value, field_type_map[key])
                            for key, value in zip(columns, row)
                        }
                        for row in rows
                    ]
                    all_results.extend(page_results)
            else:
                cursor.execute(select_query)
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                all_results = [
                    {
                        key: serialize_value(value, field_type_map[key])
                        for key, value in zip(columns, row)
                    }
                    for row in rows
                ]

            output_path = save_json_file(
                doctype_name, all_results, module_name, sqlserver_name
            )
            logging.warning(f"{doctype_name}.json guardado en {output_path}")
            return all_results

    except Exception as e:
        logging.error(f"❌ Error al exportar {doctype_name}: {e}")
        raise