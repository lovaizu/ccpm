"""The integration cases of S6, a subagent held to its steps: the laid guard, the lane types,
result.py, and the plugin's command joined through the double of Claude Code, on each path of S6's
sequence, with the rules that S6 keeps."""

from __future__ import annotations

import os
from typing import Any

import pytest
import walkthrough as w

pytestmark = pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")


@pytest.mark.supports("S6", "Lane", "Call")
def test_calls_that_keep_every_lane_go_through(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started.
    When: writer reads CHANGELOG.md, runs `git log --oneline`, and writes CHANGELOG.md anew.
    Then: the guard lets each call through."""
    _, writer = w.writer_started(b)
    assert not writer.read(os.path.join(b.repo, "CHANGELOG.md")).blocked
    ran = writer.bash("git log --oneline")
    assert not ran.blocked and "Count lines" in ran.output
    os.remove(os.path.join(b.repo, "CHANGELOG.md"))
    assert not writer.write(os.path.join(b.repo, "CHANGELOG.md"), "# Changelog\n").blocked


@pytest.mark.supports("S6", "A stop gives the step back", "Lane")
def test_a_call_that_breaks_a_lane_gets_its_steps_sentence(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and writer started.
    When: writer runs `git -C <tally> log --oneline`.
    Then: the guard stops it with the step's sentence and each command writer may run, word for
    word as the README shows."""
    _, writer = w.writer_started(b)
    stopped = writer.bash(f"git -C {b.repo} log --oneline")
    assert stopped.blocked
    assert stopped.said == (
        "changelog: Run only `git log --oneline`.\n"
        "The commands you may run, each word for word: `git log --oneline`,"
        f" `{b.result('writer', 'written')}`."
    )


@pytest.mark.supports("S6", "One type gives the sentence, the check, and the steps it suits")
def test_the_sentence_laid_is_the_sentence_a_stop_gives(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and writer started.
    When: writer writes NOTES.md, which its step 3 doesn't name.
    Then: the guard stops it with the very sentence that agents/writer.md's step 3 holds."""
    _, writer = w.writer_started(b)
    stopped = writer.write(os.path.join(b.repo, "NOTES.md"), "notes\n")
    assert stopped.blocked
    step = next(
        line
        for line in w.read(os.path.join(b.changelog, "agents", "writer.md")).splitlines()
        if line.startswith("3. ")
    )
    sentence = step.removeprefix("3. Write the new entries into `CHANGELOG.md`. ")
    assert sentence and sentence in stopped.said


@pytest.mark.supports("S6", "Only the main conversation starts the roles", "Role")
def test_a_subagents_start_of_a_role_is_stopped(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid; writer started and gave `written`, so reviewer's
    start is due.
    When: writer, before it ends, starts changelog:reviewer itself.
    Then: the guard stops the start, with the sentence of the Lane on writer's last Step."""
    _, writer = w.writer_started(b)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    stopped, agent = writer.start("changelog:reviewer", w.TEXT, "reviewer")
    assert stopped.blocked and agent is None
    assert stopped.said == f"changelog: End by running `{b.result('writer', 'written')}`."


@pytest.mark.supports("S6", "guard")
def test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, writer started, then changelog's hooks/lanes.json
    left unreadable.
    When: writer runs `git log --oneline`.
    Then: the guard stops it, saying it can't read hooks/lanes.json and who must fix it."""
    _, writer = w.writer_started(b)
    w.write_files(b.changelog, {"hooks/lanes.json": "{"})
    stopped = writer.bash("git log --oneline")
    assert stopped.blocked
    assert "lanes.json" in stopped.said and "/lane:up" in stopped.said


@pytest.mark.supports("S6", "result.py", "Result")
def test_a_result_the_role_may_not_give_is_refused(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started.
    When: writer runs result.py writer good.
    Then: result.py exits 1 with the Results writer may give, `written`, and no Result moves the
    Run."""
    c, writer = w.writer_started(b)
    refused = writer.bash(b.result("writer", "good"))
    assert refused.exit_code == 1 and "written" in refused.output
    run = next(r for r in w.where(b.changelog, b, c.session_id).runs if r.skill == "write")
    assert run.results == ()


@pytest.mark.supports("S6", "result.py", "Start")
def test_a_result_is_added_for_the_subagents_start(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and writer started.
    When: writer runs result.py writer written, and its PostToolUse reaches the guard.
    Then: writer's Start in the Run holds the Result `written`."""
    c, writer = w.writer_started(b)
    assert writer.bash(b.result("writer", "written")).exit_code == 0
    run = next(r for r in w.where(b.changelog, b, c.session_id).runs if r.skill == "write")
    assert [s.results for s in run.starts if s.role == "writer"] == [("written",)]


@pytest.mark.supports("S6", "A result only from the result script")
def test_an_end_with_no_result_is_stopped_with_its_last_steps_sentence(
    b: w.Bench, broken: None
) -> None:
    """Given: the walkthrough's Proposal laid, and reviewer started after writer's `written`.
    When: reviewer ends with the reply `more`, without running result.py.
    Then: the guard stops the end with reviewer's last Step's sentence, word for word as the
    README shows, and no start of writer is due."""
    c = w.laid(b)
    reviewer = w.to_reviewer(b, c)
    stopped, reached = reviewer.end("more")
    assert stopped.blocked and reached is None
    assert stopped.said == (
        f"changelog: End by running `{b.result('reviewer', 'more')}`"
        f" or `{b.result('reviewer', 'good')}`."
    )


@pytest.mark.supports("S6", "lane types", "Result")
def test_an_end_held_to_the_plugins_command_goes_once_it_gives_0(tmp_path: Any) -> None:
    """Given: the Proposal laid with an ends_checked Lane on reviewer's step 2 whose command passes
    only where CHANGELOG.md names 0.2.0, and reviewer started.
    When: reviewer gives `good` and ends, first before CHANGELOG.md names 0.2.0, then after.
    Then: the guard stops the first end with the Lane's sentence, and lets the second end."""
    b = w.bench(str(tmp_path))
    check = "grep -q 0.2.0 CHANGELOG.md"

    def make() -> dict[str, Any]:
        proposal = w.walkthrough_proposal()
        lane = w.lane("reviewer", "agents/reviewer.md", 2, "ends_checked", command=check)
        proposal["lanes"].append(lane)
        return proposal

    c = w.laid(b, make=make)
    reviewer = w.to_reviewer(b, c)
    assert reviewer.bash(b.result("reviewer", "good")).exit_code == 0
    stopped, _ = reviewer.end("Gave good.")
    assert stopped.blocked and check in stopped.said
    w.write_files(b.repo, {"CHANGELOG.md": "# Changelog\n\n## 0.2.0\n\n- Counts.\n"})
    ended, reached = reviewer.end("Gave good.")
    assert not ended.blocked and reached is not None


@pytest.mark.supports("S6", "lane types", "Lane")
def test_an_end_with_no_result_runs_no_command_of_the_plugins(tmp_path: Any) -> None:
    """Given: the Proposal laid with an ends_checked Lane on reviewer's step 2 whose command writes
    checked.txt, and reviewer started.
    When: reviewer ends without running result.py.
    Then: the guard stops the end with the sentence of the Lane on reviewer's last Step, and the
    command didn't run, as that Lane is checked first."""
    b = w.bench(str(tmp_path))
    check = "touch checked.txt"

    def make() -> dict[str, Any]:
        proposal = w.walkthrough_proposal()
        lane = w.lane("reviewer", "agents/reviewer.md", 2, "ends_checked", command=check)
        proposal["lanes"].append(lane)
        return proposal

    c = w.laid(b, make=make)
    reviewer = w.to_reviewer(b, c)
    stopped, reached = reviewer.end("Every entry is right.")
    assert stopped.blocked and reached is None
    assert b.result("reviewer", "good") in stopped.said
    assert not os.path.exists(os.path.join(b.repo, "checked.txt"))
