"""The integration cases of S6, a subagent held to its steps: the guard checks each call of a
subagent by each Lane of its role with the run values of its Start, stops a call that breaks one
with the step's sentence and what it may do instead, stops a subagent's start of a role, records a
Result only from result.py, and holds an end with no Result, an end that names no printed line, and
an end whose check of the plugin's own fails. The test plays the main conversation and each
subagent."""

from __future__ import annotations

import os
import stat
from typing import Any

import pytest
from claude_code import Conversation
from lane_example import (
    PROPOSAL,
    Repo,
    conversation,
    lane,
    lay,
    put,
    result_command,
    reviewer_after_written,
    starts,
)

pytestmark = pytest.mark.xfail(
    strict=True, reason="Lane's parts are skeletons, their bodies unbuilt"
)


def laid_with(repo: Repo, proposal: dict[str, Any]) -> Conversation:
    lay(repo, proposal)
    return conversation(repo, repo.plugin)


def with_lanes(*more: dict[str, Any], **fields: Any) -> dict[str, Any]:
    return {**PROPOSAL, "lanes": [*PROPOSAL["lanes"], *more], **fields}


@pytest.mark.supports("S6", "guard", "Call", "lane types")
def test_a_call_that_keeps_every_lane_of_its_role_passes(run: Conversation):
    """Given a Run of `changelog` in which writer runs
    When writer runs `git log --oneline`, word for word as its step 2 names it
    Then the guard lets it through, and it runs"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    ran = writer.bash("git log --oneline")
    assert not ran.blocked and ran.exit_code == 0


@pytest.mark.supports("S6", "guard", "Call", "Lane", "lane types")
def test_a_command_not_word_for_word_is_stopped_with_the_steps_sentence_and_the_commands(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` in which writer runs
    When writer runs `git -C <repo> log --oneline`
    Then the guard stops it, with the sentence of step 2 and the commands writer may run, as the
    walkthrough shows"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    stopped = writer.bash(f"git -C {laid.root} log --oneline")
    result = os.path.join(laid.plugin, "hooks", "lane", "result.py")
    assert stopped.blocked
    assert stopped.said == (
        "changelog: Run only `git log --oneline`.\nThe commands you may run, each word for word:"
        f" `git log --oneline`, `python3 {result} writer written`."
    )


@pytest.mark.supports("S6", "lane types", "Call")
def test_a_write_of_a_file_that_no_write_only_lane_takes_is_stopped(run: Conversation, laid: Repo):
    """Given a Run of `changelog` in which writer runs
    When writer writes NOTES.md
    Then the guard stops the write with the sentence `Write only `CHANGELOG.md`.`, and no
    NOTES.md is written"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    stopped = writer.write(os.path.join(laid.root, "NOTES.md"), "notes")
    assert stopped.blocked and "Write only `CHANGELOG.md`." in stopped.said
    assert not os.path.exists(os.path.join(laid.root, "NOTES.md"))


@pytest.mark.supports("S6", "lane types", "Call")
def test_a_read_of_a_path_that_read_never_keeps_unread_is_stopped_and_its_bang_part_passes(
    repo: Repo,
):
    """Given `changelog` laid with a read_never Lane on reviewer's step 1 that takes `notes/` and
    `!notes/public.md`, and a Run in which reviewer runs
    When reviewer reads notes/secret.md, and then notes/public.md
    Then the guard stops the first read and lets the second through"""
    put(repo.root, "notes/secret.md", "s")
    put(repo.root, "notes/public.md", "p")
    conv = laid_with(
        repo, with_lanes(lane("reviewer", 1, "read_never", "notes/", "!notes/public.md"))
    )
    reviewer = reviewer_after_written(conv, repo)
    assert reviewer.read(os.path.join(repo.root, "notes", "secret.md")).blocked
    assert not reviewer.read(os.path.join(repo.root, "notes", "public.md")).blocked


@pytest.mark.supports("S6", "guard", "Start", "Only the main conversation starts the roles")
def test_a_subagents_start_of_a_role_is_stopped_with_the_sentence_of_its_last_step(
    broken: bool, run: Conversation
):
    """Given a Run of `changelog` in which writer runs
    When writer starts reviewer by the Agent tool
    Then the guard stops the start, and gives writer the sentence of its last step"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    stopped, agent = writer.start("changelog:reviewer", "Carry out your steps", "reviewer")
    assert agent is None and stopped.blocked
    assert "End by running" in stopped.said and "writer written" in stopped.said


@pytest.mark.supports("S6", "guard", "Laid")
def test_a_call_that_the_guard_cant_check_is_stopped_with_why_and_who_must_fix_it(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` in which writer runs, and hooks/lanes.json then made unreadable
    When writer runs `git log --oneline`
    Then the guard stops it, naming hooks/lanes.json and who must fix it"""
    run.type("/changelog:write")
    _, writer = starts(run, "writer")
    assert writer
    put(laid.plugin, "hooks/lanes.json", "{")
    stopped = writer.bash("git log --oneline")
    assert stopped.blocked and "lanes.json" in stopped.said and "fix" in stopped.said


@pytest.mark.supports("S6", "result.py", "Result")
def test_result_py_refuses_a_result_that_the_role_may_not_give_with_those_it_may(
    run: Conversation, laid: Repo
):
    """Given a Run of `changelog` in which reviewer runs
    When reviewer runs `result.py reviewer done`
    Then result.py exits 1 naming `more` and `good`, and records no Result"""
    reviewer = reviewer_after_written(run, laid)
    refused = reviewer.bash(result_command(laid, "reviewer", "done"))
    assert refused.exit_code == 1 and "more" in refused.output and "good" in refused.output
    stopped, _ = reviewer.end("Done.")
    assert stopped.blocked


@pytest.mark.supports("S6", "guard", "Result", "A result only from the result script")
def test_an_end_with_no_result_is_held_with_the_sentence_of_the_last_step(
    broken: bool, run: Conversation, laid: Repo
):
    """Given a Run of `changelog` in which reviewer runs
    When reviewer runs result.py at the end of a longer command, which records no Result, and
    ends with the reply `No more entries`
    Then the guard holds the end, with the sentence of reviewer's step 2, as the walkthrough
    shows"""
    reviewer = reviewer_after_written(run, laid)
    reviewer.bash(f"git status && {result_command(laid, 'reviewer', 'good')}")
    stopped, reached = reviewer.end("No more entries")
    result = os.path.join(laid.plugin, "hooks", "lane", "result.py")
    assert stopped.blocked and reached is None
    assert stopped.said == (
        f"changelog: End by running `python3 {result} reviewer more` or"
        f" `python3 {result} reviewer good`."
    )


@pytest.mark.supports("S6", "lane types", "Lane", "Call")
def test_an_end_that_starts_no_line_with_a_line_that_its_command_printed_is_held(repo: Repo):
    """Given `changelog` laid with a names_printed Lane on writer's step 2 that takes
    `git log --oneline`, and a Run in which writer ran it
    When writer gives `written` and ends with a message that names no line git log printed, and
    then with one that starts a line with such a line
    Then the guard holds the first end, with each line printed, and lets the second end"""
    conv = laid_with(repo, with_lanes(lane("writer", 2, "names_printed", "git log --oneline")))
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    printed = writer.bash("git log --oneline").output.splitlines()
    writer.bash(result_command(repo, "writer", "written"))
    held, _ = writer.end("I wrote the entries.")
    assert held.blocked and printed[0] in held.said
    let, reached = writer.end(f"{printed[0]}\nis the newest commit.")
    assert not let.blocked and reached


@pytest.mark.supports("S6", "lane types", "Lane", "Result")
def test_an_end_whose_check_of_the_plugins_own_gives_other_than_0_is_held_with_what_it_printed(
    repo: Repo,
):
    """Given `changelog` laid with an ends_checked Lane on writer's step 4 that runs
    `python3 check.py {result}`, which exits 1 printing `no entry for --lines`, and a Run in which
    writer gave `written`
    When writer ends
    Then the guard holds the end, with the Lane's sentence and `no entry for --lines`"""
    put(repo.root, "check.py", "import sys\nprint('no entry for --lines')\nsys.exit(1)\n")
    conv = laid_with(
        repo, with_lanes(lane("writer", 4, "ends_checked", "python3 check.py {result}"))
    )
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    writer.bash(result_command(repo, "writer", "written"))
    held, _ = writer.end("Done.")
    assert held.blocked and "no entry for --lines" in held.said and "check.py" in held.said


@pytest.mark.supports("S6", "lane types", "Start")
def test_an_end_whose_check_names_a_value_its_start_didnt_give_is_held_with_who_must_fix_it(
    repo: Repo,
):
    """Given `changelog` laid with an ends_checked Lane on writer's step 4 that runs
    `python3 check.py {version}`, and no adapter, so that writer's Start gives no `version`
    When writer gives `written` and ends
    Then the guard holds the end, naming `{version}` and who must fix it"""
    put(repo.root, "check.py", "pass\n")
    conv = laid_with(
        repo, with_lanes(lane("writer", 4, "ends_checked", "python3 check.py {version}"))
    )
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer
    writer.bash(result_command(repo, "writer", "written"))
    held, _ = writer.end("Done.")
    assert held.blocked and "{version}" in held.said and "fix" in held.said


@pytest.mark.supports("S6", "Start", "adapter", "lane types")
def test_a_run_value_holds_each_subagent_to_the_value_of_its_own_start(repo: Repo):
    """Given `changelog` laid with a write_only Lane on writer's step 3 that takes
    `notes/{part}.md`, an adapter that gives writer `part` `a`, then `b` beside one that runs, and
    two writers started side by side
    When the writer of `a` writes notes/b.md, and then notes/a.md
    Then the guard stops the first write and lets the second through"""
    path = put(
        repo.plugin,
        "hooks/adapters/text",
        "#!/usr/bin/env python3\nimport json, sys\nrunning = json.load(sys.stdin)['running']\n"
        "part = 'ab'[len(running)]\nprint(json.dumps({'text': 'Write ' + part,"
        " 'values': {'part': part}}))\n",
    )
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    lanes = [each for each in PROPOSAL["lanes"] if each["type"] != "write_only"]
    lanes.append(lane("writer", 3, "write_only", "notes/{part}.md"))
    routes = [{"after": "first", "moves": [{"kind": "start", "role": "writer"}] * 2}]
    conv = laid_with(
        repo,
        {
            **PROPOSAL,
            "lanes": lanes,
            "routes": routes + PROPOSAL["routes"][1:],
            "text_adapter": "text",
        },
    )
    conv.type("/changelog:write")
    _, a = starts(conv, "writer", "Write a")
    _, b = starts(conv, "writer", "Write b")
    assert a and b
    assert a.write(os.path.join(repo.root, "notes", "b.md"), "b").blocked
    assert not a.write(os.path.join(repo.root, "notes", "a.md"), "a").blocked
