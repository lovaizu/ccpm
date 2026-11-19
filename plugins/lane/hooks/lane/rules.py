"""The form of a plugin's lane/rules.json, as rules.schema.json beside this module gives it, and
holding a plugin's file to that form."""

from __future__ import annotations

from typing import TypedDict


class Rule(TypedDict, total=False):
    """One rule of a step: its `type`, the name of a module of rule_types/, and that type's
    values."""

    type: str
    paths: list[str]
    commands: list[str]
    items: list[str]
    results: list[str]
    ends: list[str]
    check: str


class Named(TypedDict):
    """A step's name."""

    name: str


class Step(Named, total=False):
    """One step of a role, by its name, with its rules, which a step of a subagent may leave for
    the plugin's adapter of the rules to give for each start."""

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
    """A step of a fixed order: the roles to start after what the route goes after, each by its
    agent type, a role named several times starting as many times at once."""

    after: After
    start: list[str]


class Steps(TypedDict):
    """Each role's steps, a subagent's by its agent type and the main conversation's by the skill's
    name."""

    roles: dict[str, Role]


class Rules(Steps, total=False):
    """What a plugin gives Lane: each role's steps, and, where the plugin fixes its order, its
    routes."""

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
