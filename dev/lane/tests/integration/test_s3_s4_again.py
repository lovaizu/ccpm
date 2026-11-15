"""The integration cases of S3, an AI approves by its own act, and S4, proposed again after the
steps or Lane change: the guard on up, lay.py, and up joined through the double of Claude Code, on
each path of their sequences."""

from __future__ import annotations

import json
import os

import pytest
import walkthrough as w


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S3", "Approval")
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


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S3", "Run")
def test_an_ais_run_keeps_a_persons_waiting_proposal(b: w.Bench) -> None:
    """Given: a person typed /lane:up changelog and up showed a Proposal that waits for their
    reply.
    When: an AI calls up by the Skill tool in the same conversation, and lay.py print shows a
    second Proposal.
    Then: the person's Run still waits, so lay.py write of the first ID is stopped until the
    person replies, and the AI's ID lays."""
    c = w.converse(b)
    first, person_id = w.propose(b, c)
    assert not c.stop(first.output).blocked
    _, ai_id = w.propose(b, c, by_ai=True)
    runs = [r for r in w.where(b.lane, b, c.session_id).runs if r.skill == "up"]
    assert [r.by for r in runs] == ["person", "ai"]
    assert not runs[0].ended
    assert c.bash(b.lay_py("write", "changelog", person_id)).blocked
    assert c.bash(b.lay_py("write", "changelog", ai_id)).exit_code == 0


@pytest.mark.supports("S3", "Step", "up")
def test_an_ai_writes_its_change_into_the_step_before_it_lays(b: w.Bench) -> None:
    """Given: an AI called up by the Skill tool, and lay.py print showed the walkthrough's
    Proposal.
    When: it finds writer's step 3 falls short, writes the change into the Step, and proposes
    again.
    Then: lay.py print shows the changed Step with its sentence, and a new ID."""
    c = w.converse(b)
    _, first = w.propose(b, c, by_ai=True)
    path = os.path.join(b.changelog, "agents", "writer.md")
    step = "3. Write the new entries into `CHANGELOG.md`."
    assert not c.edit(path, step, "3. Write the new entries at the top of `CHANGELOG.md`.").blocked
    w.types(b, c)
    assert c.bash(b.lay_py("steps", "changelog")).exit_code == 0
    printed = w.print_proposal(b, c, w.walkthrough_proposal())
    assert printed.exit_code == 0
    assert "3. Write the new entries at the top of `CHANGELOG.md`. Write only" in printed.output
    assert w.proposal_id(printed.output) != first


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S4", "Laid", "Step")
def test_steps_after_a_lay_come_without_lanes_sentences(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid.
    When: the person types /lane:up changelog again, and up runs lay.py steps changelog.
    Then: each Step reads as the user wrote it, without a sentence that Lane laid, and no notes."""
    w.lay(b)
    c = w.converse(b)
    assert not c.type("/lane:up changelog").blocked
    ran = c.bash(b.lay_py("steps", "changelog"))
    assert ran.exit_code == 0
    given = json.loads(ran.output)
    texts = {(s["file"], s["number"]): s["text"] for s in given["steps"]}
    assert texts[("agents/writer.md", 2)] == "Read the commits since then with `git log --oneline`."
    assert texts[("agents/writer.md", 3)] == "Write the new entries into `CHANGELOG.md`."
    assert texts[("agents/writer.md", 4)] == "Reply with the entries you wrote."
    assert texts[("skills/write/SKILL.md", 1)] == "Have the entries written and reviewed."
    assert given["notes"] == []


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S4", "Laid", "user")
def test_a_sentence_the_user_changed_stays_as_theirs(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, then the user changed the sentence that Lane laid on
    writer's step 3 to `Write only CHANGELOG.md and NEWS.md.`.
    When: up runs lay.py steps changelog.
    Then: the Step keeps the user's sentence, and a note names the file, the Step, the sentence
    laid, and the user's."""
    w.lay(b)
    path = os.path.join(b.changelog, "agents", "writer.md")
    text = w.read(path).replace(
        "Write only `CHANGELOG.md`.", "Write only `CHANGELOG.md` and `NEWS.md`."
    )
    w.write_files(b.changelog, {"agents/writer.md": text})
    c = w.converse(b)
    assert not c.type("/lane:up changelog").blocked
    given = json.loads(c.bash(b.lay_py("steps", "changelog")).output)
    texts = {(s["file"], s["number"]): s["text"] for s in given["steps"]}
    assert texts[("agents/writer.md", 3)].endswith("Write only `CHANGELOG.md` and `NEWS.md`.")
    assert given["notes"] == [
        {
            "file": "agents/writer.md",
            "step": 3,
            "laid": "Write only `CHANGELOG.md`.",
            "now": "Write only `CHANGELOG.md` and `NEWS.md`.",
        }
    ]


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S4", "lay.py", "Laid")
def test_a_lay_after_lane_updates_lays_with_the_newest_code(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, then Lane updated, its result.py changed.
    When: the person lays the walkthrough's Proposal again.
    Then: changelog's hooks/lane/ holds the updated result.py, and lanes.json's Laid names Lane's
    version."""
    w.lay(b)
    path = os.path.join(b.lane, "hooks", "lane", "result.py")
    updated = w.read(path) + "# Lane updated.\n"
    w.write_files(b.lane, {"hooks/lane/result.py": updated})
    w.lay(b)
    assert w.read(os.path.join(b.changelog, "hooks", "lane", "result.py")) == updated
    lanes = json.loads(w.read(os.path.join(b.changelog, "hooks", "lanes.json")))
    plugin = json.loads(w.read(os.path.join(b.lane, ".claude-plugin", "plugin.json")))
    assert lanes["laid"]["version"] == plugin["version"]


@pytest.mark.xfail(strict=True, reason="Lane's parts have empty bodies")
@pytest.mark.supports("S4", "lay.py", "Laid", "Step")
def test_a_plugin_laid_by_an_earlier_lane_is_read_by_its_own_copy(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, then changelog's hooks/lane/ and lanes.json put in
    the form of an earlier Lane, whose copy keeps the Laid under `added`, which this Lane's form
    doesn't read.
    When: in a conversation with Lane alone, as the earlier copy's guard isn't this case's, the
    person types /lane:up changelog, and up runs lay.py steps changelog.
    Then: each Step reads as the user wrote it, as lay.py read the Laid through the plugin's own
    copy, and no notes."""
    w.lay(b)
    path = os.path.join(b.changelog, "hooks", "lanes.json")
    laid = json.loads(w.read(path))["laid"]
    sentences = [[x["file"], x["step"], x["text"]] for x in laid["sentences"]]
    earlier = {"added": {"version": "0.0.1", "sentences": sentences}}
    w.write_files(
        b.changelog,
        {"hooks/lanes.json": json.dumps(earlier), "hooks/lane/domain/form.py": w.EARLIER_FORM},
    )
    c = w.Conversation(b.repo, [b.lane], b.env, b.temp)
    assert not c.type("/lane:up changelog").blocked
    ran = c.bash(b.lay_py("steps", "changelog"))
    assert ran.exit_code == 0, ran.output
    given = json.loads(ran.output)
    texts = {(s["file"], s["number"]): s["text"] for s in given["steps"]}
    assert texts[("agents/writer.md", 2)] == "Read the commits since then with `git log --oneline`."
    assert texts[("agents/reviewer.md", 2)] == w.REVIEWER.splitlines()[-1][3:]
    assert given["notes"] == []
