"""Where the steps and rules of a start, or of a turn of the main conversation, come from: wholly
from the plugin's lane/rules.json, or, for a role that it names with no steps, wholly from the
plugin's adapter of the rules, for each start of a subagent from its prompt, and for each turn of
the main conversation from the prompt that began the turn."""

from __future__ import annotations

from rules import Rules, Step


def asks_adapter(rules: Rules, role: str) -> bool:
    """Whether a start of the role, or a turn of the main conversation in the role, takes its steps
    from the plugin's adapter of the rules.

    Takes: the plugin's rules, and a role: a subagent's, by its agent type, or the main
    conversation's, by the skill's name.
    Gives: True where the rules name the role with no steps, a subagent's start then asking the
    adapter at each start and the main conversation at each turn; False where they give its steps,
    or don't name it.
    Changes: nothing.
    Refuses: nothing.
    """
    named = rules["roles"].get(role)
    return named is not None and "steps" not in named


def steps(rules: Rules, role: str, given: list[Step] | None) -> list[Step]:
    """The steps and rules that hold a start of the role, or the main conversation's turn.

    Takes: the plugin's rules, the role, a subagent's agent type or the skill's name for the main
    conversation, and the steps that the plugin's adapter of the rules gave for the start, or for
    the main conversation's turn, None where asks_adapter gives False or no turn holds steps yet.
    Gives: the role's steps that the rules give, in their order; the given steps, where the rules
    name the role with no steps; none where the rules don't name the role.
    Changes: nothing.
    Refuses: nothing.
    """
    named = rules["roles"].get(role)
    if named is None:
        return []
    return named.get("steps", given or [])
