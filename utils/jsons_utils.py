# db/jsons_utils.py
# helpers
import json
import os
from collections import OrderedDict

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