# db/jsons_utils.py
# helpers
import json
import logging
import os
from collections import OrderedDict
import datetime
import decimal

from config import get_output_dir


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
