"""The integration cases of S1, the files a step writes: a Write or an Edit of a file that the step
of its start doesn't name stopped with the step's sentence, a named file and each file under a named
folder let through, and the main conversation's calls in a run held to its skill's step. Each runs
`log` and Lane through the double of Claude Code."""

from __future__ import annotations

import os

import pytest
from lane_bench import ENTRY, Bench, opened, started


@pytest.mark.supports("S1", "rule types")
def test_a_write_of_a_file_that_its_step_doesnt_name_is_stopped_with_the_step(b: Bench):
    """Given the writer running at its step `write`
    When it writes notes.txt
    Then the write is stopped with the step's sentence, naming the step and the files it writes,
    and notes.txt isn't written"""
    answer = started(opened(b)).write(b.at("notes.txt"), "x\n")
    assert answer.blocked
    for named in ("write", "CHANGELOG.md", "docs/changes/"):
        assert named in answer.said
    assert not os.path.exists(b.at("notes.txt"))


@pytest.mark.supports("S1")
def test_a_write_of_a_file_that_its_step_names_goes_through(b: Bench):
    """Given the writer running at its step `write`
    When it writes CHANGELOG.md
    Then the write goes through"""
    assert not started(opened(b)).write(b.at("CHANGELOG.md"), ENTRY).blocked


@pytest.mark.supports("S1")
def test_a_write_of_a_file_under_a_folder_that_its_step_names_goes_through(b: Bench):
    """Given the writer running at its step `write`, which names the folder docs/changes/
    When it writes docs/changes/1.2.0/invoices.md
    Then the write goes through, as a deliverable of several files is written whole"""
    writer = started(opened(b))
    assert not writer.write(b.at("docs/changes/1.2.0/invoices.md"), "x\n").blocked


@pytest.mark.supports("S1")
def test_an_edit_of_a_file_that_its_step_doesnt_name_is_stopped(b: Bench):
    """Given the writer running at its step `write`
    When it edits README.md
    Then the edit is stopped with the step's sentence, and README.md stays as it was"""
    answer = started(opened(b)).edit(b.at("README.md"), "# repo", "# log")
    assert answer.blocked
    assert "CHANGELOG.md" in answer.said
    with open(b.at("README.md"), encoding="utf-8") as f:
        assert f.read() == "# repo\n"


@pytest.mark.supports("S1")
def test_the_main_conversations_write_in_a_run_is_held_to_its_skills_step(b: Bench):
    """Given the person typed /log:up 1.2.0
    When the main conversation writes .log/notes.md, and then .log/up.md
    Then the first write is stopped with the step `lead` and the file it writes, and the second
    goes through"""
    c = opened(b)
    answer = c.write(None, b.at(".log/notes.md"), "x\n")
    assert answer.blocked
    assert "lead" in answer.said
    assert ".log/up.md" in answer.said
    assert not c.write(None, b.at(".log/up.md"), "x\n").blocked
