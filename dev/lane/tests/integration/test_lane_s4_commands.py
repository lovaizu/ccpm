"""The integration cases of S4, the commands a step runs: a Bash call of a command that the step of
its start doesn't name stopped with the step's sentence, and so one chained after a named command;
a named command, with more words after it too, or with a quoted word that holds an operator, and a
reporter of Lane's let through; and the main conversation's calls in a run held to its skill's
step. Each runs `log` and Lane through the double of Claude Code."""

from __future__ import annotations

import copy

import pytest
from lane_bench import RULES, Bench, opened, started


@pytest.mark.supports("S4", "rule types")
def test_a_command_that_its_step_doesnt_name_is_stopped_with_the_step(b: Bench):
    """Given the writer running at its step `write`, which runs `git log`
    When it runs `git push`
    Then the call is stopped with the step's sentence, naming the step and the commands it runs"""
    answer = started(opened(b)).bash("git push")
    assert answer.blocked
    assert "write" in answer.said
    assert "git log" in answer.said


@pytest.mark.supports("S4")
def test_a_command_that_its_step_names_goes_through(b: Bench):
    """Given the writer running at its step `write`
    When it runs `git log`
    Then the call goes through and runs"""
    answer = started(opened(b)).bash("git log")
    assert not answer.blocked
    assert answer.exit_code == 0


@pytest.mark.supports("S4")
def test_a_command_chained_after_a_named_one_is_stopped(b: Bench):
    """Given the writer running at its step `write`, which runs `git log`
    When it runs `git log && git push`
    Then the call is stopped with the step's sentence, naming `git log`"""
    answer = started(opened(b)).bash("git log && git push")
    assert answer.blocked
    assert "git log" in answer.said


@pytest.mark.supports("S4")
def test_a_named_command_with_more_words_after_it_goes_through(b: Bench):
    """Given the writer running at its step `write`
    When it runs `git log --oneline`
    Then the call goes through and runs"""
    answer = started(opened(b)).bash("git log --oneline")
    assert not answer.blocked
    assert answer.exit_code == 0


def committing(b: Bench) -> None:
    """Writes the rules of `log` with the writer's step `write` running only `git commit`."""
    rules = copy.deepcopy(RULES)
    write = rules["roles"]["log:writer"]["steps"][0]
    write["rules"] = [r for r in write["rules"] if r["type"] != "commands"]
    write["rules"].append({"type": "commands", "commands": ["git commit"]})
    b.rules(rules)


@pytest.mark.supports("S4")
def test_a_quoted_operator_stays_in_its_named_command(b: Bench):
    """Given `log` whose writer's step `write` runs only `git commit`, and the writer running
    When it runs `git commit -m "Fix; test && more"`, and then `git commit -m x; rm y`
    Then the first goes through, and the second is stopped with the step's sentence, naming
    `git commit`"""
    committing(b)
    writer = started(opened(b))
    assert not writer.bash('git commit -m "Fix; test && more"').blocked
    answer = writer.bash("git commit -m x; rm y")
    assert answer.blocked
    assert "git commit" in answer.said


@pytest.mark.supports("S4", "reporters")
def test_a_reporter_of_lanes_goes_through_though_no_step_names_it(b: Bench):
    """Given the writer running at its step `write`, which names no reporter
    When it runs `lane-item write dated`
    Then the call goes through and exits 0"""
    answer = started(opened(b)).bash("lane-item write dated")
    assert not answer.blocked
    assert answer.exit_code == 0


@pytest.mark.supports("S4")
def test_the_main_conversations_command_in_a_run_is_held_to_its_skills_step(b: Bench):
    """Given the person typed /log:up 1.2.0
    When the main conversation runs `ls`, and then `git status`
    Then the first is stopped naming `git status`, and the second goes through"""
    c = opened(b)
    answer = c.bash("ls")
    assert answer.blocked
    assert "git status" in answer.said
    assert not c.bash("git status").blocked
