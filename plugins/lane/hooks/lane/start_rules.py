"""Where a start's steps and rules come from: wholly from the plugin's lane/rules.json, or, for a
subagent's role that it names with no steps, wholly from the plugin's adapter of the rules for the
start, from its prompt."""

from __future__ import annotations

from rules import Rules, Step


def asks_adapter(rules: Rules, role: str) -> bool:
    """Whether a start of the role takes its steps from the plugin's adapter of the rules.

    Takes: the plugin's rules, and a subagent's role, by its agent type.
    Gives: True where the rules name the role with no steps; False where they give its steps, or
    don't name it.
    Changes: nothing.
    Refuses: nothing.
    """
    named = rules["roles"].get(role)
    return named is not None and "steps" not in named


def steps(rules: Rules, role: str, given: list[Step] | None) -> list[Step]:
    """The steps and rules that hold a start of the role.

    Takes: the plugin's rules, the role, a subagent's agent type or the skill's name for the main
    conversation, and the steps that the plugin's adapter of the rules gave for the start, None
    where asks_adapter gives False.
    Gives: the role's steps that the rules give, in their order; the given steps, where the rules
    name the role with no steps; none where the rules don't name the role.
    Changes: nothing.
    Refuses: nothing.
    """
    named = rules["roles"].get(role)
    if named is None:
        return []
    return named.get("steps", given or [])
