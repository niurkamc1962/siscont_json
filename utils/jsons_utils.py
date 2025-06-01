# db/jsons_utils.py
# helpers
import json
import os
from typing import OrderedDict

from config import get_output_dir


def save_json_file(
    doctype_name: str, data: list, module_name: str = None, sqlserver_name: str = None
) -> str:
    output_dir = get_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{sqlserver_name}.json")

    # Preparando el formato del JSON
    content = OrderedDict()
    # content["sqlserver"] = sqlserver_name
    content["doctype"] = doctype_name
    # content["module"] = module_name if module_name else "no_module"
    content["data"] = data

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=4, ensure_ascii=False)

    return output_path
