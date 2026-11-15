"""How lay.py tells Lane's entries in a plugin's hooks.json from the user's own, as the guard's code
names Lane's, and replaces Lane's while it leaves the user's as they stand."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def replace_entries(plugin: str, entries: Mapping[str, Any]) -> None:
    """Puts Lane's entries in the plugin's hooks.json in place of those of an earlier Lane.

    Takes: the plugin's folder, and Lane's entries from `events.hook_entries`.
    Gives: nothing.
    Changes: hooks/hooks.json, made where it isn't there, each entry that runs
    hooks/lane/hook.py replaced and each other entry kept.
    Refuses: form.OutOfForm, where hooks.json isn't JSON in Claude Code's form, and OSError,
    where it can't be written.
    Carries: S2 `L->>LS: replaces Lane's hook entries, as the guard's code names them`.
    """
    raise NotImplementedError("hooks_file.replace_entries")
