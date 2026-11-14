"""The unit cases of hooks/lane/result.py, the result script's entry, through `main`, run from a
copy of Lane's code laid in a plugin of the test's own, with the lines of a Run of the conversation
in its record."""

from __future__ import annotations

import os
import shutil
from typing import Any

import pytest
from claude_code import run_python
from domain.laid_set import dumps
from domain.run_record import add, load
from lane_example import LANE
from lane_parts import REVIEWER_GAVE_GOOD, SESSION, WRITER_GAVE_WRITTEN, WRITER_RUNNING, laid_set


@pytest.fixture
def plugin(tmp_path: Any) -> dict[str, str]:
    """The walkthrough's `changelog` laid in a folder of the test's own, with Lane's code copied in,
    and the environment of a Bash command of the conversation."""
    base = os.path.realpath(str(tmp_path))
    root = os.path.join(base, "changelog")
    shutil.copytree(os.path.join(LANE, "hooks", "lane"), os.path.join(root, "hooks", "lane"))
    with open(os.path.join(root, "hooks", "lanes.json"), "w", encoding="utf-8") as f:
        f.write(dumps(laid_set()))
    temp = os.path.join(base, "tmp")
    os.makedirs(temp)
    return {"root": root, "temp": temp}


def result(plugin: dict[str, str], *args: str) -> tuple[int, str, str]:
    """`python3 <plugin>/hooks/lane/result.py <args>`, as a role runs it."""
    script = os.path.join(plugin["root"], "hooks", "lane", "result.py")
    env = dict(os.environ, TMPDIR=plugin["temp"], CLAUDE_CODE_SESSION_ID=SESSION)
    return run_python(script, list(args), "", env, plugin["root"])


def writer_runs(plugin: dict[str, str]) -> None:
    """The lines of a Run in which writer, subagent a1, runs."""
    for line in WRITER_RUNNING:
        add(line, plugin["temp"], "changelog", SESSION)


@pytest.mark.supports(
    "test_the_command_gives_the_first_start_and_each_result_gives_the_next_until_no_more"
)
def test_a_result_the_role_may_give_exits_0_and_writes_no_line(plugin: dict[str, str]):
    """Given a Run in which writer runs
    When `result.py writer written` runs
    Then it exits 0, and the run record holds the lines it held, as the guard adds the Result at
    the PostToolUse of the run"""
    writer_runs(plugin)
    code, _, _ = result(plugin, "writer", "written")
    assert code == 0 and load(plugin["temp"], "changelog", SESSION) == WRITER_RUNNING


@pytest.mark.supports(
    "test_result_py_refuses_a_result_that_the_role_may_not_give_with_those_it_may"
)
def test_a_result_the_role_may_not_give_exits_1_naming_those_it_may(plugin: dict[str, str]):
    """Given a Run in which writer runs
    When `result.py writer done` runs
    Then it exits 1, naming `written`"""
    writer_runs(plugin)
    code, out, err = result(plugin, "writer", "done")
    assert code == 1 and "written" in out + err


@pytest.mark.supports("test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step")
def test_a_result_with_no_run_of_the_conversation_exits_1_with_why(plugin: dict[str, str]):
    """Given no Run of the conversation
    When `result.py writer written` runs
    Then it exits 1, saying no Run holds the role"""
    code, out, err = result(plugin, "writer", "written")
    assert code == 1 and out + err


@pytest.mark.supports(
    "test_result_py_refuses_a_result_that_the_role_may_not_give_with_those_it_may"
)
def test_arguments_other_than_a_role_and_a_result_exit_2_with_the_usage(plugin: dict[str, str]):
    """Given a Run of the conversation
    When `result.py writer` runs, with no result
    Then it exits 2 with the usage"""
    writer_runs(plugin)
    code, _, err = result(plugin, "writer")
    assert code == 2 and "usage" in err


@pytest.mark.supports("test_the_skills_own_result_where_a_move_starts_no_more_ends_the_run")
def test_the_skills_result_once_its_moves_start_no_more_exits_0(plugin: dict[str, str]):
    """Given a Run whose reviewer gave `good`, so that the move starts no more
    When `result.py write good` runs
    Then it exits 0"""
    for line in REVIEWER_GAVE_GOOD:
        add(line, plugin["temp"], "changelog", SESSION)
    assert result(plugin, "write", "good")[0] == 0


@pytest.mark.supports("test_the_skills_own_result_ends_only_the_run_of_the_skill_it_names")
def test_the_skills_result_while_a_start_is_due_exits_1_with_why(plugin: dict[str, str]):
    """Given a Run whose writer gave `written`, so that reviewer's start is due
    When `result.py write good` runs
    Then it exits 1, saying that no run holds `write` now"""
    for line in WRITER_GAVE_WRITTEN:
        add(line, plugin["temp"], "changelog", SESSION)
    code, out, err = result(plugin, "write", "good")
    assert code == 1 and "holds write" in out + err
