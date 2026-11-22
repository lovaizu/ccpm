"""The form of a plugin's lane/rules.json, as rules.schema.json beside this module gives it, and
holding a plugin's file to that form."""

from __future__ import annotations

import json
import os
from typing import TypedDict, cast

from json_form import held


class Rule(TypedDict, total=False):
    """One rule of a step: its `type`, the name of a module of rule_types/, and that type's
    values, a checklist's `items` or the `command` that gives them at the mark."""

    type: str
    paths: list[str]
    commands: list[str]
    items: list[str]
    results: list[str]
    ends: list[str]
    check: str
    command: str


class Step(TypedDict):
    """One step of a role, by its name, with its rules."""

    name: str
    rules: list[Rule]


class Role(TypedDict, total=False):
    """The steps of one role, in their order: a subagent of the plugin, or the main conversation
    in a run of a skill; a subagent's role with no steps takes them from the plugin's adapter of
    the rules for each start, and the main conversation's for each turn."""

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


# A class apart from Rules only so that `roles` is required and `routes` isn't, as the TypedDict of
# Python 3.9, which Lane runs on, has no NotRequired.
class Steps(TypedDict):
    """Each role's steps, a subagent's by its agent type and the main conversation's by the skill's
    name."""

    roles: dict[str, Role]


class Rules(Steps, total=False):
    """What a plugin gives Lane: each role's steps, and, where the plugin fixes its order, its
    routes."""

    routes: list[Route]


class OutOfForm(Exception):
    """A plugin's lane/rules.json out of Lane's form, said with what Lane couldn't check and why:
    the file, the place in it, and what the form takes there."""


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
        raise OutOfForm(f"{_UNCHECKED}{path} isn't JSON: {error}") from None
    left = held(rules, "rules.schema.json")
    if left is not None:
        raise OutOfForm(
            f"{_UNCHECKED}{path} leaves the form of Lane's hooks/lane/rules.schema.json, at {left}"
        )
    return cast(Rules, rules)


# What Lane couldn't check where a plugin's rules are out of its form.
_UNCHECKED = "Lane couldn't check this move by the plugin's rules: "
