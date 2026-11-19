"""The form of a plugin's lane/rules.json, as rules.schema.json beside this module gives it, and
holding a plugin's file to that form."""

from __future__ import annotations

import json
import os
from typing import TypedDict, cast

from json_form import held


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


class Step(TypedDict):
    """One step of a role, by its name, with its rules."""

    name: str
    rules: list[Rule]


class Role(TypedDict, total=False):
    """The steps of one role, in their order: a subagent of the plugin, or the main conversation
    in a run of a skill; a subagent's role with no steps takes them from the plugin's adapter of
    the rules for each start."""

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
    path = os.path.join(plugin_root, "lane", "rules.json")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return None
    try:
        rules = json.loads(text)
    except ValueError as error:
        raise OutOfForm(f"Lane: {path} isn't JSON: {error}. {_MEND}") from None
    left = held(rules, "rules.schema.json")
    if left is not None:
        raise OutOfForm(f"Lane: {path}, at {left}. {_MEND}")
    return cast(Rules, rules)


# What the plugin's author does with a file out of Lane's form.
_MEND = "The plugin's author mends it to the form of Lane's hooks/lane/rules.schema.json."
