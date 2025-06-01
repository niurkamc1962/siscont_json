import json
from datetime import date, datetime
from decimal import Decimal


def serialize_value(value):
    if isinstance(value, (datetime, date)):
        # return value.isoformat()
        if value.year == 1753:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return str(value)


def is_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False
