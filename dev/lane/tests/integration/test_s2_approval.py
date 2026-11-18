"""The integration cases of S2, the user, a person or an AI, approves or asks a change: up and
lay.py write joined through the double of Claude Code, on each path of S2's sequence, with the
rules that S2 keeps."""

from __future__ import annotations

import json
import os

import pytest
import walkthrough as w


@pytest.mark.supports("S2", "Step", "The steps are the one source")
def test_a_change_is_written_into_its_step_and_proposed_again(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and up's next Run after the person typed
    /lane:up changelog again.
    When: the person asks that writer also read README.md, up writes it into writer's step 1, and
    runs lay.py steps changelog.
    Then: the Steps hold the change, and none of the sentences that Lane laid."""
    w.lay(b)
    c = w.converse(b)
    assert not c.type("/lane:up changelog").blocked
    assert not c.type("Have writer read README.md too.").blocked
    path = os.path.join(b.changelog, "agents", "writer.md")
    step = next(line for line in w.WRITER.splitlines() if line.startswith("1. "))
    assert not c.edit(path, step, step[:-1] + ", and `README.md`.").blocked
    ran = c.bash(b.lay_py("steps", "changelog"))
    assert ran.exit_code == 0
    texts = [s["text"] for s in json.loads(ran.output)["steps"] if s["role"] == "writer"]
    assert texts[0].endswith("and `README.md`.")
    assert not any("Run only" in t or "Write only" in t or "End by" in t for t in texts)


@pytest.mark.supports("S2", "lay.py")
def test_lay_of_an_id_no_proposal_has_is_refused(b: w.Bench) -> None:
    """Given: up gave what lay.py print showed, and the person replied yes.
    When: up runs lay.py write changelog with an ID that no Proposal has.
    Then: lay.py write exits 1, saying no such Proposal, and lays nothing."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert not c.stop(printed.output).blocked
    assert not c.type("yes").blocked
    refused = c.bash(b.lay_py("write", "changelog", "0" * len(pid)))
    assert refused.exit_code == 1
    assert "0" * len(pid) in refused.output
    assert not os.path.exists(os.path.join(b.changelog, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "lay.py", "Step", "Laid only as shown")
def test_lay_after_the_steps_changed_is_refused(b: w.Bench, broken: None) -> None:
    """Given: up gave what lay.py print showed, then reviewer's step 1 changed in its file.
    When: the person replies yes, and up runs lay.py write changelog with the ID.
    Then: lay.py write exits 1, saying the Steps changed, and every file stands as it was."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert not c.stop(printed.output).blocked
    path = os.path.join(b.changelog, "agents", "reviewer.md")
    changed = w.REVIEWER.replace("against the commits", "against each commit")
    w.write_files(b.changelog, {"agents/reviewer.md": changed})
    assert not c.type("yes").blocked
    refused = c.bash(b.lay_py("write", "changelog", pid))
    assert refused.exit_code == 1
    assert w.read(path) == changed
    assert w.read(os.path.join(b.changelog, "agents", "writer.md")) == w.WRITER


@pytest.mark.supports("S2", "lay.py")
def test_a_failed_validate_puts_back_each_file(b: w.Bench) -> None:
    """Given: up gave what lay.py print showed, then changelog's plugin.json given a `name` that
    isn't a string, so claude plugin validate fails.
    When: the person replies yes, and up runs lay.py write changelog with the ID.
    Then: lay.py write exits 1 with what failed, and each other file of changelog stands as
    before."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert not c.stop(printed.output).blocked
    w.write_files(b.changelog, {".claude-plugin/plugin.json": '{"name": 1}\n'})
    assert not c.type("yes").blocked
    refused = c.bash(b.lay_py("write", "changelog", pid))
    assert refused.exit_code == 1
    assert "Validation failed" in refused.output
    assert w.git(b.repo, "status", "--porcelain") == " M changelog/.claude-plugin/plugin.json\n"


@pytest.mark.supports("S2", "Lane's part replaced whole")
def test_lay_keeps_the_users_hook_entries(tmp_path: object, broken: None) -> None:
    """Given: changelog whose hooks/hooks.json holds an entry of its own on SessionStart.
    When: the person lays the walkthrough's Proposal.
    Then: hooks.json holds the user's entry as it stood, beside Lane's entries."""
    own = {"type": "command", "command": "echo", "args": ["hello"]}
    hooks = {"hooks": {"SessionStart": [{"hooks": [own]}]}}
    b = w.bench(str(tmp_path), dict(w.FILES, **{"hooks/hooks.json": json.dumps(hooks)}))
    w.lay(b)
    written = json.loads(w.read(os.path.join(b.changelog, "hooks", "hooks.json")))["hooks"]
    assert written["SessionStart"] == [{"hooks": [own]}]
    assert "PreToolUse" in written


@pytest.mark.supports("S2", "Lane's part replaced whole", "Laid")
def test_lay_again_replaces_what_the_earlier_lay_added(b: w.Bench, broken: None) -> None:
    """Given: the walkthrough's Proposal laid, and hooks.json given an entry of the user's after.
    When: the person lays it again by /lane:up changelog.
    Then: each Step holds each sentence once, and hooks.json holds Lane's entries once and the
    user's entry as it stood."""
    w.lay(b)
    path = os.path.join(b.changelog, "hooks", "hooks.json")
    hooks = json.loads(w.read(path))
    own = {"type": "command", "command": "echo", "args": ["hello"]}
    hooks["hooks"]["SessionStart"] = [{"hooks": [own]}]
    w.write_files(b.changelog, {"hooks/hooks.json": json.dumps(hooks)})
    before = w.read(os.path.join(b.changelog, "agents", "writer.md"))
    w.lay(b)
    assert w.read(os.path.join(b.changelog, "agents", "writer.md")) == before
    written = json.loads(w.read(path))["hooks"]
    assert written["SessionStart"] == [{"hooks": [own]}]
    assert len(written["PreToolUse"]) == 1


@pytest.mark.supports("S2", "user")
def test_an_ai_lays_by_its_own_run_of_lay(b: w.Bench) -> None:
    """Given: an AI in the main conversation called up by the Skill tool, and lay.py print showed
    the walkthrough's Proposal.
    When: it runs lay.py write changelog with the ID, with no person's prompt since.
    Then: the guard lets it through, and lay.py write lays the Proposal."""
    c = w.converse(b)
    printed, pid = w.propose(b, c, by_ai=True)
    assert not c.stop(printed.output).blocked
    written = c.bash(b.lay_py("write", "changelog", pid))
    assert not written.blocked
    assert written.exit_code == 0
    assert os.path.isfile(os.path.join(b.changelog, "hooks", "lanes.json"))


@pytest.mark.supports("S2", "Laid", "lay.py", "user")
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
        f" `{w.RESULT} writer written`, as a command of its own." in writer
    )
    assert os.path.isfile(os.path.join(b.changelog, "hooks", "lane", "hook.py"))
    lanes = json.loads(w.read(os.path.join(b.changelog, "hooks", "lanes.json")))
    assert len(lanes["routes"]) == 4
    files = {"skills/write/SKILL.md", "agents/writer.md", "agents/reviewer.md"}
    assert {s["file"] for s in lanes["laid"]["sentences"]} == files


@pytest.mark.supports("S2", "lay.py", "Step")
def test_a_proposal_refused_as_the_steps_changed_lays_once_proposed_again(b: w.Bench) -> None:
    """Given: up gave what lay.py print showed, then reviewer's step 1 changed in its file, and the
    person's yes was refused by lay.py write, as the Steps changed.
    When: up proposes again, as S1 draws, and the person replies yes to what it shows.
    Then: lay.py write lays the new ID, and reviewer's step 1 holds the person's change."""
    c = w.converse(b)
    printed, pid = w.propose(b, c)
    assert not c.stop(printed.output).blocked
    changed = w.REVIEWER.replace("against the commits", "against each commit")
    w.write_files(b.changelog, {"agents/reviewer.md": changed})
    assert not c.type("yes").blocked
    assert c.bash(b.lay_py("write", "changelog", pid)).exit_code == 1
    again, new = w.propose(b, c)
    assert new != pid
    assert not c.stop(again.output).blocked
    assert not c.type("yes").blocked
    written = c.bash(b.lay_py("write", "changelog", new))
    assert written.exit_code == 0, written.output
    assert "against each commit" in w.read(os.path.join(b.changelog, "agents", "reviewer.md"))
