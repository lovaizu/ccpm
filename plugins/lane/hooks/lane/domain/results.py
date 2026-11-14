"""Decides whether a result is one that the role may give, and records it for the Start of the
subagent that gave it, as result.py runs it, so that the guard goes on only from a Result that
this module recorded, as the principle A result only from the result script says."""

from __future__ import annotations

from domain.laid_set import LaidSet
from domain.run_record import Result, Run


def may_give(laid_set: LaidSet, role: str) -> tuple[str, ...]:
    """Each result that the role may give, as its gives_result Lane takes them, in their order;
    none for a role of no such Lane."""
    raise NotImplementedError("results.may_give")


def record(run: Run, laid_set: LaidSet, role: str, result: str) -> Result:
    """Adds to the Run the result of the role, for the Start of the subagent of that role whose
    call of result.py the guard let through last, or for the skill where the main conversation
    ran it, and gives the Result. Raises Fault, naming each result that the role may give, where
    the role may give no such result, or where no call of result.py by the role is in the Run, as
    when a role runs it at the end of a longer command."""
    raise NotImplementedError("results.record")
