"""How lay.py reads the Laid of a plugin through the guard's code that the plugin's own hooks/lane/
holds, the code of the Lane that laid it, loaded apart from this Lane's code of the same names."""

from __future__ import annotations

from form import Laid


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
    raise NotImplementedError
