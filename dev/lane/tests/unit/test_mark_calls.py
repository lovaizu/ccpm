"""The unit cases of what carries a Mark from a role to the guard, and a Step's Items from the
plugin: script_calls.py's `step_command`, `step_args`, `item_command`, and `item_args`, the words
of a run of step.py and item.py; adapters.py's `step_items`, what the adapter of a step's items is
handed and gives, and how it fails."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import pytest
from adapters import AdapterFailed, step_items
from script_calls import item_args, item_command, step_args, step_command

pytestmark = pytest.mark.xfail(
    strict=True, reason="the parts that carry a Mark and a Step's Items have empty bodies"
)

ROOT = "/home/you/tally/changelog"


def program(tmp_path: Any, text: str) -> str:
    """An executable Python program with the text, as an adapter of the plugin."""
    path = tmp_path / "items.py"
    path.write_text(f"#!{sys.executable}\n{text}")
    os.chmod(path, 0o755)
    return str(path)


@pytest.mark.supports("test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence")
def test_the_step_command_names_the_role_and_a_place_for_the_steps_number() -> None:
    """Given: writer.
    When: step_command gives the command by which writer marks a Step.
    Then: it names the plugin's step.py by `${CLAUDE_PLUGIN_ROOT}`, writer, and `<n>`."""
    assert step_command("writer") == "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py writer <n>"


@pytest.mark.supports("test_a_proposal_of_the_lane_types_of_steps_shows_each_steps_sentence")
def test_the_item_command_names_the_role_and_a_place_for_the_items_id() -> None:
    """Given: writer.
    When: item_command gives the command by which writer marks an Item.
    Then: it names the plugin's item.py by `${CLAUDE_PLUGIN_ROOT}`, writer, and `<id>`."""
    assert item_command("writer") == "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/item.py writer <id>"


@pytest.mark.supports("test_a_step_marked_in_its_turn_is_added_for_the_subagents_start")
@pytest.mark.parametrize(
    "command, read",
    [
        (f"python3 {ROOT}/hooks/lane/step.py writer 2", ("writer", 2)),
        ("python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py write 1", ("write", 1)),
        (f"python3 {ROOT}/hooks/lane/step.py writer 1", ("writer", 1)),
        (f"python3 {ROOT}/hooks/lane/step.py writer 0", None),
        (f"python3 {ROOT}/hooks/lane/step.py writer two", None),
        (f"python3 {ROOT}/hooks/lane/step.py writer", None),
        (f"python3 {ROOT}/hooks/lane/step.py writer 2 3", None),
        (f"python3 {ROOT}/hooks/lane/step.py writer 2; rm CHANGELOG.md", None),
        ("python3 /other/hooks/lane/step.py writer 2", None),
        (f"python3 {ROOT}/hooks/lane/item.py writer 2", None),
        (f"python3 {ROOT}/hooks/lane/step.py writer '2", None),
    ],
    ids=[
        "the plugin's step.py",
        "by the root's name",
        "Step 1, the first",
        "Step 0",
        "a word for the number",
        "no number",
        "a word more",
        "and another command",
        "another plugin's",
        "item.py",
        "a command shlex can't split",
    ],
)
def test_a_run_of_step_py_names_its_role_and_step(command: str, read: Any) -> None:
    """Given: a Bash command, and changelog's folder.
    When: step_args reads it.
    Then: it gives the role and the Step only for one run of changelog's step.py with a role and
    a whole number of 1 or more."""
    assert step_args(command, ROOT) == read


@pytest.mark.supports("test_an_item_of_the_step_due_is_marked")
@pytest.mark.parametrize(
    "command, read",
    [
        (f"python3 {ROOT}/hooks/lane/item.py writer dated", ("writer", "dated")),
        ("python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/item.py write N2.4", ("write", "N2.4")),
        (f"python3 {ROOT}/hooks/lane/item.py writer", None),
        (f"python3 {ROOT}/hooks/lane/item.py writer dated linked", None),
        (f"python3 {ROOT}/hooks/lane/item.py writer dated && rm CHANGELOG.md", None),
        ("python3 /other/hooks/lane/item.py writer dated", None),
        (f"python3 {ROOT}/hooks/lane/step.py writer dated", None),
    ],
    ids=[
        "the plugin's item.py",
        "by the root's name",
        "no ID",
        "a word more",
        "and another command",
        "another plugin's",
        "step.py",
    ],
)
def test_a_run_of_item_py_names_its_role_and_item(command: str, read: Any) -> None:
    """Given: a Bash command, and changelog's folder.
    When: item_args reads it.
    Then: it gives the role and the Item only for one run of changelog's item.py with two
    arguments."""
    assert item_args(command, ROOT) == read


ECHO = """import json, os, sys
handed = json.load(sys.stdin)
print(json.dumps({"items": [json.dumps([sys.argv[1:], handed, os.getcwd()])]}))
"""


@pytest.mark.supports(
    "test_the_adapter_of_a_steps_items_is_handed_the_role_the_step_and_the_run_values"
)
def test_the_adapter_of_a_steps_items_is_handed_the_role_the_step_and_the_values(
    tmp_path: Any,
) -> None:
    """Given: an adapter of a step's items that prints, as its one Item, what it was handed.
    When: step_items asks it for writer's step 3, with the value version 0.2.0, in tally.
    Then: it was handed `writer` and `3` as its two arguments, `{"values": {"version": "0.2.0"}}`
    on standard input, and ran in tally."""
    repo = tmp_path / "tally"
    repo.mkdir()
    (item,) = step_items(program(tmp_path, ECHO), "writer", 3, {"version": "0.2.0"}, str(repo))
    assert json.loads(item) == [["writer", "3"], {"values": {"version": "0.2.0"}}, str(repo)]


@pytest.mark.supports("test_a_step_with_an_item_left_goes_back_to_the_step")
@pytest.mark.parametrize(
    "items", [["dated", "linked"], ["dated"], []], ids=["two Items", "one Item", "none"]
)
def test_the_adapter_of_a_steps_items_gives_each_id_in_its_order(tmp_path: Any, items: Any) -> None:
    """Given: an adapter of a step's items that prints the IDs.
    When: step_items asks it for writer's step 3.
    Then: it gives each ID in the adapter's order, none where it prints none."""
    adapter = program(tmp_path, f"print({json.dumps(json.dumps({'items': items}))})\n")
    assert step_items(adapter, "writer", 3, {}, str(tmp_path)) == tuple(items)


@pytest.mark.supports(
    "test_an_adapter_of_a_steps_items_that_fails_stops_the_mark_with_who_must_fix_it"
)
@pytest.mark.parametrize(
    "text, why",
    [
        ("import sys\nsys.exit('CHECKLIST.md is not there')\n", "CHECKLIST.md is not there"),
        ("print('dated')\n", "JSON"),
        ("print('[\"dated\"]')\n", "items"),
        ('print(\'{"items": "dated"}\')\n', "items"),
        ("print('{\"items\": [1]}')\n", "items"),
    ],
    ids=["it exits 1", "not JSON", "not an object", "items not a list", "an ID not a string"],
)
def test_an_adapter_of_a_steps_items_that_fails_or_strays_from_its_form_is_refused(
    tmp_path: Any, text: str, why: str
) -> None:
    """Given: an adapter of a step's items that exits 1 with why, or prints other than a JSON
    object whose `items` is a list of strings.
    When: step_items asks it for writer's step 3.
    Then: it raises AdapterFailed, naming the adapter and why."""
    adapter = program(tmp_path, text)
    with pytest.raises(AdapterFailed, match=why) as raised:
        step_items(adapter, "writer", 3, {}, str(tmp_path))
    assert adapter in str(raised.value)


@pytest.mark.supports(
    "test_an_adapter_of_a_steps_items_that_fails_stops_the_mark_with_who_must_fix_it"
)
def test_an_adapter_of_a_steps_items_that_cant_run_is_refused(tmp_path: Any) -> None:
    """Given: an adapter of a step's items that isn't there.
    When: step_items asks it for writer's step 3.
    Then: it raises AdapterFailed, naming the adapter."""
    missing = str(tmp_path / "items.py")
    with pytest.raises(AdapterFailed, match="items.py"):
        step_items(missing, "writer", 3, {}, str(tmp_path))
