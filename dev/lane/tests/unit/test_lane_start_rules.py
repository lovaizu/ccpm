"""The unit cases of hooks/lane/start_rules.py: asks_adapter and steps, one for each class of what
the plugin's rules give a role: its steps, a name with no steps, or nothing, for a subagent's role
and for the main conversation's skill; with a role named with an empty list of steps, a role whose
name nearly matches one that the rules name, and steps given beside rules that fix the role's own
or don't name it."""

from __future__ import annotations

import copy
from typing import Any

import lane_bench
import pytest
from rules import Rules, Step
from start_rules import asks_adapter, steps

# The rules of `log`, naming the scribe with no steps, so that each start of it takes them from the
# plugin's adapter of the rules.
RULES: Rules = copy.deepcopy(lane_bench.RULES)
RULES["roles"]["log:scribe"] = {}
RULES["roles"]["log:idle"] = {"steps": []}
GIVEN: list[Step] = [{"name": "jot", "rules": [{"type": "writes", "paths": ["NOTE.md"]}]}]
WRITER: Any = lane_bench.RULES["roles"]["log:writer"]["steps"]


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_role_named_with_no_steps_asks_the_adapter():
    """Given rules that name the scribe with no steps
    When Lane decides whether a start of the scribe asks the adapter of the rules
    Then it does"""
    assert asks_adapter(RULES, "log:scribe")


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.parametrize("role", ["log:writer", "general-purpose"])
def test_a_role_with_steps_or_not_named_asks_no_adapter(role: str):
    """Given rules that give the writer's steps and name no general-purpose
    When Lane decides whether a start of the writer, or of general-purpose, asks the adapter
    Then neither does"""
    assert not asks_adapter(RULES, role)


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
def test_a_role_with_steps_is_held_to_them_in_their_order():
    """Given rules that give the writer's steps `write` and `report`
    When Lane gives the steps of a writer's start
    Then they are those, in their order"""
    assert steps(RULES, "log:writer", None) == WRITER


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_role_named_with_no_steps_is_held_to_the_steps_given():
    """Given rules that name the scribe with no steps, and the steps that the adapter gave its start
    When Lane gives the steps of the start
    Then they are those given"""
    assert steps(RULES, "log:scribe", GIVEN) == GIVEN


@pytest.mark.supports("test_a_subagent_started_in_the_foreground_lies_outside_the_run")
def test_a_role_that_the_rules_dont_name_has_no_steps():
    """Given rules that name no general-purpose
    When Lane gives the steps of its start
    Then there's none"""
    assert steps(RULES, "general-purpose", None) == []


@pytest.mark.supports("test_the_main_conversations_write_in_a_run_is_held_to_its_skills_step")
@pytest.mark.parametrize("skill", ["log:up", "log:tag"])
def test_the_main_conversation_is_held_to_its_skills_steps(skill: str):
    """Given rules that give the steps of the skills log:up and log:tag
    When Lane gives the steps of the main conversation in a run of either
    Then they are that skill's steps"""
    assert steps(RULES, skill, None) == lane_bench.RULES["roles"][skill]["steps"]


@pytest.mark.supports("test_the_main_conversation_holds_to_the_steps_of_the_latest_commands_skill")
def test_a_skill_that_the_rules_give_no_steps_has_none():
    """Given rules that give no steps of the skill log:retry
    When Lane gives the steps of the main conversation in it
    Then there's none"""
    assert steps(RULES, "log:retry", None) == []


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
@pytest.mark.parametrize("role", ["log:idle", "log:scrib", "log:scribe2"])
def test_a_role_named_with_an_empty_list_or_named_nearly_asks_no_adapter(role: str):
    """Given rules that name log:idle with an empty list of steps, and the scribe with none
    When Lane decides whether a start of log:idle, or of a role whose name nearly matches the
    scribe's, asks the adapter of the rules
    Then none does"""
    assert not asks_adapter(RULES, role)


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
@pytest.mark.parametrize("role, held", [("log:writer", WRITER), ("log:idle", [])])
def test_a_role_whose_steps_the_rules_give_is_held_to_them_beside_steps_given(
    role: str, held: list[Step]
):
    """Given rules that give the writer's steps, and log:idle's empty list, and steps given for a
    start
    When Lane gives the steps of a start of either
    Then they are those that the rules give, and not those given"""
    assert steps(RULES, role, GIVEN) == held


@pytest.mark.supports("test_a_start_of_a_subagent_that_isnt_the_plugins_lies_outside_the_run")
def test_a_role_that_the_rules_dont_name_has_no_steps_beside_steps_given():
    """Given rules that name no general-purpose, and steps given for its start
    When Lane gives the steps of the start
    Then there's none"""
    assert steps(RULES, "general-purpose", GIVEN) == []


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
@pytest.mark.parametrize("given", [None, []])
def test_a_role_named_with_no_steps_and_none_given_has_none(given: list[Step] | None):
    """Given rules that name the scribe with no steps, and no steps given for its start, or an
    empty list
    When Lane gives the steps of the start
    Then there's none"""
    assert steps(RULES, "log:scribe", given) == []
