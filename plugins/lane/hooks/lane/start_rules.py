"""Where a start's steps and rules come from: those that the plugin's lane/rules.json fixes for its
role, those that the plugin's adapter of the rules gives for the start from its prompt where the
file leaves them, or both."""

from __future__ import annotations

from rules import Rules, Step


def asks_adapter(rules: Rules, role: str) -> bool:
    """Whether a start of the role takes rules from the plugin's adapter of the rules.

    Takes: the plugin's rules, and a subagent's role, by its agent type.
    Gives: True where the rules name no steps of the role, or name a step of it with no rules;
    False where they fix each step's rules.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("start_rules.asks_adapter")


def steps(rules: Rules, role: str, given: list[Step] | None) -> list[Step]:
    """The steps and rules that hold a start of the role.

    Takes: the plugin's rules, the role, a subagent's agent type or the skill's name for the main
    conversation, and the steps that the plugin's adapter of the rules gave for the start, None
    where it gave none.
    Gives: the role's steps that the rules fix, in their order, each step that they name with no
    rules taking the rules that the given steps hold for the step of its name; the given steps
    whole, where the rules name no steps of the role; none where neither gives any, so that no rule
    holds the start.
    Changes: nothing.
    Refuses: nothing.
    """
    raise NotImplementedError("start_rules.steps")
