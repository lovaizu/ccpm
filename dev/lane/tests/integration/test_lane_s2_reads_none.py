"""The integration cases of S2, the files a step never reads: a Read of a file that the step of its
start names never to read, or of a file under a folder it names, stopped with the step's sentence;
a Read of any other file let through; a Grep whose search reaches such a file stopped with the
step's sentence, while a Glob there goes through; and a Bash command that reaches such a file
stopped by the step's rule of commands. Each runs `log` and Lane through the double of Claude
Code."""

from __future__ import annotations

import pytest
from lane_bench import Bench, opened, started


@pytest.mark.supports("S2", "rule types")
def test_a_read_of_a_file_under_a_folder_never_to_read_is_stopped_with_the_step(b: Bench):
    """Given the writer running at its step `write`, which never reads secrets/
    When it reads secrets/key.txt
    Then the read is stopped with the step's sentence, naming the step and the files it never
    reads"""
    answer = started(opened(b)).read(b.at("secrets/key.txt"))
    assert answer.blocked
    for named in ("write", "secrets/", ".env"):
        assert named in answer.said


@pytest.mark.supports("S2")
def test_a_read_of_a_file_never_to_read_is_stopped(b: Bench):
    """Given the writer running at its step `write`, which never reads .env
    When it reads .env
    Then the read is stopped"""
    assert started(opened(b)).read(b.at(".env")).blocked


@pytest.mark.supports("S2")
def test_a_read_of_another_file_goes_through(b: Bench):
    """Given the writer running at its step `write`
    When it reads NOTES.md
    Then the read goes through"""
    assert not started(opened(b)).read(b.at("NOTES.md")).blocked


@pytest.mark.supports("S2", "S4")
def test_a_bash_command_that_reads_a_file_never_to_read_is_stopped_by_its_commands(b: Bench):
    """Given the writer running at its step `write`, which never reads secrets/ and runs `git log`
    When it runs `cat secrets/key.txt`
    Then the call is stopped with the step's sentence, naming `git log`"""
    answer = started(opened(b)).bash("cat secrets/key.txt")
    assert answer.blocked
    assert "git log" in answer.said


@pytest.mark.supports("S2")
def test_a_grep_whose_search_reaches_a_file_never_to_read_is_stopped_with_the_step(b: Bench):
    """Given the writer running at its step `write`, which never reads secrets/ and .env
    When it greps for `k` in secrets
    Then the search is stopped with the step's sentence, asking for a path outside those files
    instead of secrets"""
    answer = started(opened(b)).grep("k", "secrets")
    assert answer.blocked
    assert answer.said == (
        "You're at the step `write` of log:writer, which never reads secrets/ and .env.\n"
        "Give Grep a path outside those files instead of secrets."
    )


@pytest.mark.supports("S2")
def test_a_glob_in_a_folder_never_to_read_goes_through(b: Bench):
    """Given the writer running at its step `write`, which never reads secrets/
    When it globs `*.txt` in secrets
    Then the search goes through, as a Glob reads no file's content"""
    assert not started(opened(b)).glob("*.txt", "secrets").blocked
