"""How rn's cases load each of rn's adapters of Lane, lane/adapters/<name>.py, from its file under
a module name of its own, as both adapters' names stand apart from rn's domain modules."""

from __future__ import annotations

import importlib.util
import os
from typing import Any

import rn_files


def adapter(name: str) -> Any:
    """rn's adapter of the name, `rules` or `starts_due`, loaded from its file."""
    path = os.path.join(rn_files.RN, "lane", "adapters", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"rn_adapter_{name}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
