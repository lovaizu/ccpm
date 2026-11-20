"""The unit cases of hooks/lane/rules.py's read_rules: one for each class of a plugin's
lane/rules.json, in Lane's form or out of it, with the edges of each list that the form bounds, a
role of no step, of one, and of several, and each refusal naming the file, the place, and what the
plugin's author mends it to."""

from __future__ import annotations

import copy
import json
import os
from typing import Any

import lane_bench
import pytest
from repo_files import write_files
from rules import OutOfForm, read_rules


def plugin_with(folder: str, rules: Any) -> str:
    """A plugin in the folder whose lane/rules.json holds the rules, as JSON where they aren't
    text."""
    text = rules if isinstance(rules, str) else json.dumps(rules)
    write_files(folder, {"lane/rules.json": text})
    return folder


def writer_rule(rule: Any) -> Any:
    """The rules of `log`, its writer's step `write` holding the rule alone."""
    rules = copy.deepcopy(lane_bench.RULES)
    rules["roles"]["log:writer"]["steps"][0]["rules"] = [rule]
    return rules


def refused(folder: str, rules: Any) -> str:
    """What OutOfForm says of the rules, which names the file and closes with what the plugin's
    author mends it to."""
    with pytest.raises(OutOfForm) as raised:
        read_rules(plugin_with(folder, rules))
    said = str(raised.value)
    assert os.path.join(folder, "lane", "rules.json") in said
    assert said.endswith(MEND)
    return said


# What each refusal closes with: who mends the file, and to which form.
MEND = "The plugin's author mends it to the form of Lane's hooks/lane/rules.schema.json."


def held(folder: str, rules: Any) -> None:
    """The rules read as the file holds them."""
    assert read_rules(plugin_with(folder, rules)) == rules


@pytest.mark.supports("test_each_plugins_run_is_held_to_the_rules_in_its_own_folder")
def test_rules_in_the_form_read_as_they_are(log: str):
    """Given `log`, whose lane/rules.json holds each type of rule and the routes
    When Lane reads its rules
    Then they are the rules the file holds"""
    assert read_rules(log) == lane_bench.RULES


@pytest.mark.supports("test_work_outside_a_run_of_a_plugin_with_rules_is_left_alone")
def test_a_plugin_with_no_rules_file_has_no_rules(tmp_path: Any):
    """Given a plugin with no lane/rules.json
    When Lane reads its rules
    Then it has none, so Lane leaves its runs alone"""
    folder = os.path.join(str(tmp_path), "plain")
    os.makedirs(folder)
    assert read_rules(folder) is None


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_a_file_that_isnt_json_is_out_of_form_naming_the_file(tmp_path: Any):
    """Given a plugin whose lane/rules.json isn't JSON
    When Lane reads its rules
    Then it refuses with OutOfForm naming the file, saying it isn't JSON, and what the plugin's
    author mends it to"""
    assert "isn't JSON" in refused(str(tmp_path), "{roles")


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_rules_of_a_wrong_type_are_out_of_form_naming_what_the_form_takes(tmp_path: Any):
    """Given a plugin whose lane/rules.json holds a list at its top
    When Lane reads its rules
    Then it refuses with OutOfForm naming the file and the object that the form takes there"""
    assert "the top: takes object" in refused(str(tmp_path), [lane_bench.RULES])


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
def test_rules_without_roles_are_out_of_form_naming_them(tmp_path: Any):
    """Given rules that lack their roles
    When Lane reads them
    Then it refuses with OutOfForm naming the file and the roles"""
    assert "roles" in refused(str(tmp_path), {"routes": lane_bench.RULES["routes"]})


@pytest.mark.supports(
    "test_a_run_of_a_plugin_with_no_order_holds_the_main_conversation_to_its_skills_steps"
)
def test_rules_without_routes_are_in_the_form(tmp_path: Any):
    """Given rules with roles and no routes, of a plugin that gives no order or an adapter of it
    When Lane reads them
    Then they read as they are"""
    rules = {"roles": lane_bench.RULES["roles"]}
    assert read_rules(plugin_with(str(tmp_path), rules)) == rules


@pytest.mark.supports(
    "test_a_role_with_no_fixed_steps_takes_them_from_the_plugins_adapter_for_each_start"
)
def test_a_role_named_with_no_steps_is_in_the_form(tmp_path: Any):
    """Given rules that name the writer with no steps, for the plugin's adapter of the rules to give
    When Lane reads them
    Then they read as they are"""
    rules = lane_bench.ADAPTED
    assert read_rules(plugin_with(str(tmp_path), rules)) == rules


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_its_step_lets_it_end_with_later_steps_undone"
)
@pytest.mark.parametrize(
    "rule",
    [
        {"type": "result", "ends": ["unclear"]},
        {"type": "result", "results": ["written"], "ends": ["unclear"]},
    ],
)
def test_a_result_rule_with_results_that_end_the_start_is_in_the_form(tmp_path: Any, rule: Any):
    """Given rules whose writer's step holds a rule of results naming only those that end the start,
    or both kinds
    When Lane reads them
    Then they read as they are"""
    rules = writer_rule(rule)
    assert read_rules(plugin_with(str(tmp_path), rules)) == rules


@pytest.mark.supports(
    "test_a_result_that_ends_the_start_at_its_step_lets_it_end_with_later_steps_undone"
)
@pytest.mark.parametrize("rule", [{"type": "result"}, {"type": "result", "ends": []}])
def test_a_result_rule_with_no_result_of_either_kind_is_out_of_form(tmp_path: Any, rule: Any):
    """Given rules whose writer's step holds a rule of results with neither kind, or no result that
    ends the start
    When Lane reads them
    Then it refuses with OutOfForm"""
    refused(str(tmp_path), writer_rule(rule))


@pytest.mark.supports("test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend")
def test_a_rule_of_a_type_that_lane_lacks_is_out_of_form_naming_its_place(tmp_path: Any):
    """Given rules whose writer's step holds a rule of the type `size`
    When Lane reads them
    Then it refuses with OutOfForm naming the rule's place and its type"""
    said = refused(str(tmp_path), writer_rule({"type": "size"}))
    assert "log:writer" in said
    assert "size" in said


@pytest.mark.supports("test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend")
@pytest.mark.parametrize("kind", ["reads_none", "reads_whole", "result"])
def test_a_rule_with_an_empty_list_is_out_of_form(tmp_path: Any, kind: str):
    """Given rules whose writer's step holds a rule of the files never to read or to read whole
    with no path, or a rule of results with no result
    When Lane reads them
    Then it refuses with OutOfForm, as the form takes one at least"""
    values = "results" if kind == "result" else "paths"
    refused(str(tmp_path), writer_rule({"type": kind, values: []}))


@pytest.mark.supports("test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step")
@pytest.mark.xfail(
    strict=True,
    reason="rules.schema.json takes a rule of the files a step writes with no path, as a step that"
    " writes nothing",
)
def test_a_rule_of_the_files_written_with_no_path_is_in_the_form(tmp_path: Any):
    """Given rules whose writer's step writes nothing, by a rule of the files it writes with an
    empty list
    When Lane reads them
    Then they read as they are"""
    held(str(tmp_path), writer_rule({"type": "writes", "paths": []}))


@pytest.mark.supports("test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file")
@pytest.mark.parametrize("paths", [["docs/"], ["NOTES.md", "docs/changes/"]])
@pytest.mark.xfail(
    strict=True,
    reason="rules.schema.json refuses a path that ends with / in a rule of the files to read whole,"
    " as a folder has no lines to read",
)
def test_a_folder_in_a_rule_of_the_files_to_read_whole_is_out_of_form(
    tmp_path: Any, paths: list[str]
):
    """Given rules whose writer's step reads whole the folder docs/, or NOTES.md and the folder
    docs/changes/
    When Lane reads them
    Then it refuses with OutOfForm"""
    refused(str(tmp_path), writer_rule({"type": "reads_whole", "paths": paths}))


@pytest.mark.supports("test_a_step_marked_done_with_a_file_unread_is_stopped_with_the_file")
def test_a_file_in_a_folder_in_a_rule_of_the_files_to_read_whole_is_in_the_form(tmp_path: Any):
    """Given rules whose writer's step reads whole docs/style.md, a file in a folder
    When Lane reads them
    Then they read as they are"""
    held(str(tmp_path), writer_rule({"type": "reads_whole", "paths": ["docs/style.md"]}))


@pytest.mark.supports("test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend")
@pytest.mark.parametrize("kind", ["writes", "reads_none", "reads_whole", "result"])
def test_a_rule_with_one_value_is_in_the_form(tmp_path: Any, kind: str):
    """Given rules whose writer's step holds a rule of the type with one path or one result
    When Lane reads them
    Then they read as they are"""
    values = "results" if kind == "result" else "paths"
    rules = writer_rule({"type": kind, values: ["CHANGELOG.md"]})
    assert read_rules(plugin_with(str(tmp_path), rules)) == rules


@pytest.mark.supports("test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend")
def test_a_commands_rule_with_no_command_is_in_the_form(tmp_path: Any):
    """Given rules whose writer's step runs no command, by a rule of commands with an empty list
    When Lane reads them
    Then they read as they are, as the form bounds no list of commands"""
    rules = writer_rule({"type": "commands", "commands": []})
    assert read_rules(plugin_with(str(tmp_path), rules)) == rules


@pytest.mark.supports("test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend")
@pytest.mark.parametrize(
    "rule",
    [{"type": "writes"}, {"type": "check"}, {"type": "order", "paths": ["x"]}],
)
def test_a_rule_without_its_values_or_with_others_is_out_of_form(tmp_path: Any, rule: Any):
    """Given rules whose writer's step holds a rule that lacks its type's values, or has values of
    another type
    When Lane reads them
    Then it refuses with OutOfForm"""
    refused(str(tmp_path), writer_rule(rule))


@pytest.mark.supports("test_a_rule_of_a_type_that_lane_lacks_stops_saying_what_to_mend")
@pytest.mark.parametrize(
    "after, place",
    [
        ({}, "after: holds none of the forms it may take"),
        ({"role": "log:writer"}, "after: holds none of the forms it may take"),
        ({"command": "log:up", "role": "log:writer", "result": "x"}, "after/role"),
    ],
)
def test_a_route_after_neither_a_command_nor_a_result_is_out_of_form(
    tmp_path: Any, after: Any, place: str
):
    """Given rules with a route after nothing, after a role with no result, or after both a
    command and a result
    When Lane reads them
    Then it refuses with OutOfForm naming the route's place: its `after`, which no form of it
    goes into, or the place deepest in the first form it goes into"""
    rules = copy.deepcopy(lane_bench.RULES)
    rules["routes"].append({"after": after, "start": []})
    n = len(lane_bench.RULES["routes"])
    assert f"routes/{n}/{place}" in refused(str(tmp_path), rules)


@pytest.mark.supports("test_a_step_is_held_only_to_the_types_its_rules_pick")
@pytest.mark.parametrize(
    "roles",
    [
        {},
        {"log:up": {"steps": []}},
        {"log:up": {"steps": [{"name": "lead", "rules": []}]}},
        {
            "log:writer": {
                "steps": [
                    {"name": "draft", "rules": [{"type": "order"}]},
                    {"name": "write", "rules": [{"type": "order"}]},
                    {"name": "report", "rules": [{"type": "result", "results": ["written"]}]},
                ]
            }
        },
    ],
)
def test_roles_of_none_one_and_several_steps_are_in_the_form(tmp_path: Any, roles: Any):
    """Given rules with no role, a role with an empty list of steps, a role of one step with no
    rule, or a role of three steps
    When Lane reads them
    Then they read as they are"""
    held(str(tmp_path), {"roles": roles})


@pytest.mark.supports("test_rules_out_of_form_stop_the_call_saying_what_the_author_mends")
@pytest.mark.parametrize(
    "rules, place",
    [
        ({"roles": {}, "order": []}, "at order: "),
        ({"roles": {"log:writer": {"steps": [], "model": "x"}}}, "roles/log:writer/model"),
        ({"roles": {"log:writer": {"steps": [{"name": "", "rules": []}]}}}, "steps/0/name"),
        ({"roles": {"log:writer": {"steps": [{"name": "write"}]}}}, "steps/0"),
        ({"roles": {"log:writer": {"steps": {"name": "write"}}}}, "roles/log:writer/steps"),
    ],
)
def test_rules_with_a_key_more_or_a_step_out_of_form_are_refused_naming_its_place(
    tmp_path: Any, rules: Any, place: str
):
    """Given rules with a key that the form lacks at their top or in a role, a step with an empty
    name or no rules, or steps that aren't a list
    When Lane reads them
    Then it refuses with OutOfForm naming the place"""
    assert place in refused(str(tmp_path), rules)


@pytest.mark.supports("test_a_role_named_twice_in_a_route_is_due_twice_at_once")
@pytest.mark.parametrize(
    "start, kept", [([], True), (["log:writer", "log:writer"], True), ([""], False)]
)
def test_a_routes_start_of_none_or_of_a_role_twice_is_in_the_form_and_an_empty_name_isnt(
    tmp_path: Any, start: list[str], kept: bool
):
    """Given rules with a route after /log:retry that starts no role, the writer twice, or a role
    with an empty name
    When Lane reads them
    Then the first two read as they are, and the last is refused with OutOfForm naming its place"""
    rules = copy.deepcopy(lane_bench.RULES)
    rules["routes"].append({"after": {"command": "log:again"}, "start": start})
    if kept:
        held(str(tmp_path), rules)
    else:
        n = len(lane_bench.RULES["routes"])
        assert f"routes/{n}/start/0" in refused(str(tmp_path), rules)
