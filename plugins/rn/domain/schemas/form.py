"""Decides how rn holds a JSON value to one of its JSON Schemas: the keywords of draft-07 that rn's
schemas use, and the one place where a value leaves its form, named by its path from the top, such
as `deliverables/0/status`, so that whoever wrote the value can mend it."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

# A JSON value as Python reads it.
Json = Any


def load(path: str) -> Mapping[str, Json]:
    """The JSON Schema at `path`.

    Takes: the path of a schema, such as a file of `schemas/` or the design tree best practice's.
    Gives: the schema.
    Refuses: CantRun where the file can't be read or isn't JSON, as rn's own file is at fault."""
    raise NotImplementedError("form.load")


def hold(value: Json, schema: Mapping[str, Json], name: str) -> None:
    """Holds `value` to `schema`.

    Takes: the value read from the file named `name`, and its schema.
    Gives: nothing, where the value holds its form.
    Refuses: Wrong, naming `name`, the path within the value of the first place that leaves the
    form, and what the schema takes there."""
    raise NotImplementedError("form.hold")
