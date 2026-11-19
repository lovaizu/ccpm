"""The form of a plugin's lane/rules.json, as rules.schema.json beside this module gives it, and
holding a plugin's file to that form."""

from __future__ import annotations

from typing import TypedDict


class Rule(TypedDict, total=False):
    """One rule of a step: its `type`, the name of a module of lanes/, and that type's values."""

    type: str
    paths: list[str]
    commands: list[str]
    results: list[str]
    check: str


class Step(TypedDict):
    """One step of a role, by its name, with its rules."""

    name: str
    rules: list[Rule]


class Role(TypedDict):
    """The steps of one role, in their order: a subagent of the plugin, or the main conversation
    in a run of a skill."""

    steps: list[Step]


class After(TypedDict, total=False):
    """What a route goes after: a command that the person types, or a role's result."""

    command: str
    role: str
    result: str


class Route(TypedDict):
    """The roles whose starts come due after what the route goes after, each by its agent type, a
    role named several times starting several times at once."""

    after: After
    start: list[str]


class Rules(TypedDict):
    """What a plugin gives Lane: each role's steps, a subagent's by its agent type and the main
    conversation's by the skill's name, and the routes."""

    roles: dict[str, Role]
    routes: list[Route]


class OutOfForm(Exception):
    """A plugin's lane/rules.json out of Lane's form, said with the file, the place in it, and
    what the form takes there, so that the plugin's author can mend it."""


def read_rules(plugin_root: str) -> Rules | None:
    """The rules of the plugin in the folder.

    Takes: the plugin's folder.
    Gives: the rules in its lane/rules.json, held to rules.schema.json; None where the plugin has
    no lane/rules.json, as Lane then leaves its runs alone.
    Changes: nothing.
    Refuses: OutOfForm, where the file can't be read as JSON or breaks the form.
    """
    raise NotImplementedError("rules.read_rules")
