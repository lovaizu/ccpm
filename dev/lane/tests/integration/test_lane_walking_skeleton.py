"""The integration cases of Lane's walking skeleton: the thinnest run of the README's walkthrough
through every part, from the proposal that up shows and the person's yes that lays it, to the run
of /changelog:write that starts each subagent in the order set and stops a subagent's command
outside its step with that step's sentence."""

from __future__ import annotations

import json
import os

import pytest
import walkthrough as w


@pytest.mark.supports("S1", "up", "user", "Proposal")
def test_up_shows_the_walkthroughs_proposal(b: w.Bench) -> None:
    """Given: changelog as the walkthrough gives it, with no Lane laid.
    When: the person types /lane:up changelog, and up hands the walkthrough's Proposal to lay.py
    print.
    Then: lay.py print exits 0 and shows the Routes, each Step as it'll read, and the ID, word for
    word as the README shows them."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert printed.exit_code == 0
    assert printed.output.rstrip("\n") == w.shown(pid)


@pytest.mark.supports("S2", "Approval", "Laid", "lay.py", "user")
def test_yes_lays_the_proposal_into_the_plugin(b: w.Bench) -> None:
    """Given: up gave what lay.py print showed of the walkthrough's Proposal.
    When: the person replies yes, and up runs lay.py write changelog with the ID.
    Then: lay.py write exits 0 and shows each file written, as the README shows; each Step holds
    its sentence; hooks/lane/ holds Lane's code; lanes.json holds the Proposal and the Laid; and
    result.py up laid gives 0."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert not c.stop(printed.output).blocked
    assert not c.type("yes").blocked
    written = c.bash(b.lay_py("write", "changelog", pid))
    assert written.exit_code == 0
    assert written.output.rstrip("\n") == w.WROTE
    writer = w.read(os.path.join(b.changelog, "agents", "writer.md"))
    assert "2. Read the commits since then with `git log --oneline`. Run only `git log" in writer
    assert (
        "4. Reply with the entries you wrote. End by running"
        f" `{w.RESULT} writer written`." in writer
    )
    assert os.path.isfile(os.path.join(b.changelog, "hooks", "lane", "hook.py"))
    lanes = json.loads(w.read(os.path.join(b.changelog, "hooks", "lanes.json")))
    assert len(lanes["routes"]) == 4
    files = {"skills/write/SKILL.md", "agents/writer.md", "agents/reviewer.md"}
    assert {s["file"] for s in lanes["laid"]["sentences"]} == files
    assert c.bash(b.up_result("laid")).exit_code == 0


@pytest.mark.supports("S5", "Route", "Start", "Result", "Run", "guard")
def test_the_walkthroughs_run_moves_in_the_order_the_user_set(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, and Claude Code's plugins reloaded.
    When: the person types /changelog:write, and the main conversation starts each subagent it's
    told to, writer giving `written`, reviewer `more`, writer `written`, and reviewer `good`.
    Then: Lane gives each start due and each Result with its moves, word for word as the README
    shows, and the skill's result.py write good ends the Run."""
    c = w.laid(b)
    assert w.due("writer") in c.type("/changelog:write").said
    for role, result, then in (
        ("writer", "written", w.due("reviewer")),
        ("reviewer", "more", w.due("writer")),
        ("writer", "written", w.due("reviewer")),
        ("reviewer", "good", "changelog: reviewer gave `good`. Start no more subagents."),
    ):
        started, agent = w.start(c, role)
        assert not started.blocked and agent
        reached = w.give(b, agent, result)
        assert f"changelog: {role} gave `{result}`." in reached.said
        assert then.split(": ", 1)[-1] in reached.said
    assert c.bash(b.result("write", "good")).exit_code == 0
    assert all(r.ended for r in w.where(b.changelog, b, c.session_id).runs)


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
