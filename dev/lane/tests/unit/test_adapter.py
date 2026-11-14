"""The unit cases of domain/adapter.py: how the guard runs the plugin's adapters and reads what
they print, through `start_text` and `kept_results`, on adapters that each test writes."""

from __future__ import annotations

import os
import stat
from typing import Any

import pytest
from domain.adapter import StartText, kept_results, start_text
from domain.fault import Fault
from domain.run_record import Result, Start

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


@pytest.fixture
def folder(tmp_path: Any) -> str:
    return os.path.realpath(str(tmp_path))


def program(folder: str, body: str, executable: bool = True) -> str:
    """An adapter of the test's own, a Python program with the body."""
    path = os.path.join(folder, "adapter")
    with open(path, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env python3\nimport json, os, sys\n" + body)
    if executable:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


@pytest.mark.supports("test_the_adapter_gives_a_start_its_text_and_run_values")
def test_a_text_alone_gives_a_start_with_no_values(folder: str):
    """Given an adapter that prints `{"text": "Write 0.2.0"}`
    When the text of writer's start is asked
    Then it is `Write 0.2.0`, with no values"""
    path = program(folder, 'print(json.dumps({"text": "Write 0.2.0"}))\n')
    assert start_text(path, "writer", [], folder) == StartText("Write 0.2.0", {})


@pytest.mark.supports("test_the_adapter_gives_a_start_its_text_and_run_values")
def test_a_text_with_values_gives_both(folder: str):
    """Given an adapter that prints a text and the value `version` `0.2.0`
    When the text of writer's start is asked
    Then it is the text, with the value"""
    path = program(folder, 'print(json.dumps({"text": "W", "values": {"version": "0.2.0"}}))\n')
    assert start_text(path, "writer", [], folder) == StartText("W", {"version": "0.2.0"})


@pytest.mark.supports(
    "test_starts_side_by_side_each_with_a_text_other_than_those_of_its_role_that_run"
)
def test_the_adapter_reads_the_role_and_each_start_that_runs(folder: str):
    """Given an adapter that prints its argument and what it read on stdin as the text
    When the text of writer's start is asked, with writer running on `Write a` and `part` `a`
    Then the adapter got `writer` and `{"running": [{"role": "writer", "text": "Write a",
    "values": {"part": "a"}}]}`"""
    path = program(folder, 'print(json.dumps({"text": sys.argv[1] + " " + sys.stdin.read()}))\n')
    running = [Start(1, "writer", "Write a", {"part": "a"}, agent="a1", running=True)]
    text = start_text(path, "writer", running, folder).text
    role, given = text.split(" ", 1)
    expected = {"running": [{"role": "writer", "text": "Write a", "values": {"part": "a"}}]}
    assert (role, __import__("json").loads(given)) == ("writer", expected)


@pytest.mark.supports("test_the_adapter_gives_a_start_its_text_and_run_values")
def test_the_adapter_runs_in_the_folder_that_the_conversation_works_in(folder: str):
    """Given an adapter that prints the folder it runs in as the text
    When the text of a start is asked with the folder given
    Then the text is that folder"""
    path = program(folder, 'print(json.dumps({"text": os.getcwd()}))\n')
    assert start_text(path, "writer", [], folder).text == folder


@pytest.mark.supports(
    "test_a_start_whose_text_the_adapter_cant_give_is_stopped_with_who_must_fix_it"
)
def test_an_adapter_that_exits_1_raises_a_fault_with_what_it_said(folder: str):
    """Given an adapter that prints `no plan yet` on stderr and exits 1
    When the text of writer's start is asked
    Then a Fault holds `no plan yet`, with the plugin's maker to fix it"""
    path = program(folder, 'print("no plan yet", file=sys.stderr)\nsys.exit(1)\n')
    with pytest.raises(Fault, match="no plan yet") as raised:
        start_text(path, "writer", [], folder)
    assert "maker" in raised.value.who


@pytest.mark.supports(
    "test_a_start_whose_text_the_adapter_cant_give_is_stopped_with_who_must_fix_it"
)
def test_an_adapter_that_prints_what_isnt_json_raises_a_fault(folder: str):
    """Given an adapter that prints `Write 0.2.0`, not JSON
    When the text of writer's start is asked
    Then a Fault says what it printed isn't the form"""
    with pytest.raises(Fault):
        start_text(program(folder, 'print("Write 0.2.0")\n'), "writer", [], folder)


@pytest.mark.supports(
    "test_a_start_whose_text_the_adapter_cant_give_is_stopped_with_who_must_fix_it"
)
def test_an_adapter_whose_json_has_no_text_raises_a_fault_naming_text(folder: str):
    """Given an adapter that prints `{"values": {}}`
    When the text of writer's start is asked
    Then a Fault names `text`"""
    with pytest.raises(Fault, match="text"):
        start_text(program(folder, 'print(json.dumps({"values": {}}))\n'), "writer", [], folder)


@pytest.mark.supports(
    "test_a_start_whose_text_the_adapter_cant_give_is_stopped_with_who_must_fix_it"
)
def test_an_adapter_that_cant_run_raises_a_fault(folder: str):
    """Given an adapter that isn't executable
    When the text of writer's start is asked
    Then a Fault says it can't run"""
    path = program(folder, 'print(json.dumps({"text": "t"}))\n', executable=False)
    with pytest.raises(Fault):
        start_text(path, "writer", [], folder)


@pytest.mark.supports(
    "test_a_new_conversation_picks_up_from_the_kept_results_that_follow_the_routes"
)
def test_kept_results_read_in_their_order(folder: str):
    """Given an adapter that prints writer `written` and reviewer `more`
    When the Kept results are asked
    Then they are those two Results, in order"""
    printed = (
        '{"results": [{"role": "writer", "result": "written"},'
        ' {"role": "reviewer", "result": "more"}]}'
    )
    path = program(folder, f"print({printed!r})\n")
    assert kept_results(path, folder) == [Result("writer", "written"), Result("reviewer", "more")]


@pytest.mark.supports("test_an_adapter_of_the_records_that_fails_stops_the_command_with_why")
def test_kept_results_not_in_the_form_raise_a_fault(folder: str):
    """Given an adapter that prints `{"results": [{"role": "writer"}]}`
    When the Kept results are asked
    Then a Fault names `result`"""
    path = program(folder, 'print(json.dumps({"results": [{"role": "writer"}]}))\n')
    with pytest.raises(Fault, match="result"):
        kept_results(path, folder)
