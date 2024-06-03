from typing import Any
import sys


def get_module_namespace(module: str) -> dict[str, Any]:
    return vars(sys.modules[module])
