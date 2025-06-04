import json
import decimal
import datetime
import logging


# def serialize_value(value):
#     if value is None:
#         return None
#     if isinstance(value, (datetime, date)):
#         # return value.isoformat()
#         if value.year == 1753:
#             return None
#         return value.strftime("%Y-%m-%d %H:%M:%S")
#     elif isinstance(value, Decimal):
#         return float(value)
#     elif isinstance(value, bytes):
#         return value.decode("utf-8", errors="ignore")
#     return str(value)

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
        # elif field_type == 'auto':
        #     return _auto_detect(value)
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


# def _auto_detect(value):
#     if isinstance(value, bool):
#         return value
#
#     if isinstance(value, (int, float)):
#         if value in (0, 1):  # tratar 0 y 1 como boolean
#             return bool(value)
#         return value
#
#     str_val = str(value).strip().upper()
#     if str_val in ('1', '0', 'S', 'N', 'TRUE', 'FALSE', 'Y', 'N', 'YES', 'NO'):
#         return _serialize_boolean(value)
#
#     try:
#         return _serialize_numeric(value)
#     except:
#         pass
#
#     if isinstance(value, (datetime.date, datetime.datetime)):
#         return _serialize_date(value)
#
#     return str(value).strip()

def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False
