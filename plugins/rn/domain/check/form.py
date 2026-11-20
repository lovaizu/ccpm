"""Decides how a JSON value is held to one of rn's JSON Schemas, in the part of draft-07 that rn's
schemas and the design tree's use, with the standard library alone."""

from __future__ import annotations

from typing import Any


def faults(value: Any, schema_path: str) -> list[str]:
    """Each place where the value leaves the schema.

    Takes: a value read from JSON, and the path of a JSON Schema.
    Gives: each place, by its JSON Pointer, with what the schema takes there, such as
    `/work/0/do: takes one of make, decide`; none where the value holds the schema.
    Changes: nothing.
    Refuses: CantRun where the schema can't be read or uses a keyword that this module doesn't
    check, naming it, so that no keyword passes unchecked.
    """
    raise NotImplementedError("check.form.faults")
