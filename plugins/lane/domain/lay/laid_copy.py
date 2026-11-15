"""How lay.py reads the Laid of a plugin through the guard's code that the plugin's own hooks/lane/
holds, the code of the Lane that laid it, loaded apart from this Lane's code of the same names."""

from __future__ import annotations

import importlib.util
import os
import sys
from types import ModuleType

from form import Laid, OutOfForm


def read_laid(plugin: str) -> Laid:
    """What Lane laid in the plugin, read by the code of the Lane that laid it.

    Takes: the plugin's folder.
    Gives: the Laid that `form.read_lanes` of the plugin's hooks/lane/domain/ reads from its
    hooks/lanes.json, by the fields that every version of form.Laid keeps, as this Lane's Laid; an
    empty Laid where the plugin holds no hooks/lane/, as Lane never laid in it.
    Changes: nothing.
    Refuses: form.OutOfForm, where the plugin's copy finds lanes.json out of its form, or where
    hooks/lane/ holds no code that reads it.
    Carries: S1 `L->>LS: reads the Laid`, S4 `L->>LS: reads the Laid by the guard's code in its
    hooks/lane/, the form of the Lane that laid it`.
    """
    if not os.path.isdir(os.path.join(plugin, "hooks", "lane")):
        return Laid("", ())
    form = _copy_form(plugin)
    try:
        form.read_lanes(os.path.join(plugin, "hooks", "lanes.json"))
    except form.OutOfForm as e:
        raise OutOfForm(e.problems) from e
    raise NotImplementedError("laid_copy.read_laid, of a plugin Lane laid in")


def _copy_form(plugin: str) -> ModuleType:
    """The plugin's own hooks/lane/domain/form.py, loaded under a name of its own, so that it stands
    apart from this Lane's form; OutOfForm where the plugin holds no such file."""
    path = os.path.join(plugin, "hooks", "lane", "domain", "form.py")
    if not os.path.isfile(path):
        where = os.path.join(plugin, "hooks", "lane")
        raise OutOfForm([f"{where} holds no domain/form.py that reads hooks/lanes.json"])
    spec = importlib.util.spec_from_file_location("laid_copy_form", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # dataclasses finds a module's names through sys.modules while it runs the module.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        del sys.modules[spec.name]
    return module
