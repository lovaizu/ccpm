"""The integration cases of S3, proposed again after the steps or Lane change: up and lay.py joined
through the double of Claude Code, on each path of S3's sequence."""

from __future__ import annotations

import json
import os

import pytest
import walkthrough as w


@pytest.mark.supports("S2", "Step", "up")
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


@pytest.mark.supports("S3", "Laid", "Step")
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


@pytest.mark.supports("S3", "Laid", "user")
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


@pytest.mark.supports("S3", "lay.py", "Laid")
def test_a_lay_after_lane_updates_lays_with_the_newest_code(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, then Lane updated, its result.py changed.
    When: the person lays the walkthrough's Proposal again.
    Then: changelog's hooks/lane/ holds the updated result.py."""
    w.lay(b)
    path = os.path.join(b.lane, "hooks", "lane", "result.py")
    updated = w.read(path) + "# Lane updated.\n"
    w.write_files(b.lane, {"hooks/lane/result.py": updated})
    w.lay(b)
    assert w.read(os.path.join(b.changelog, "hooks", "lane", "result.py")) == updated


@pytest.mark.supports("S3", "Laid", "Step")
@pytest.mark.xfail(
    strict=True,
    reason=(
        "the Laid names each sentence by its Step's number, so a Step the user adds before it"
        " leaves Lane's sentence in the Step it moved to and notes a change on the Step now there"
    ),
)
def test_a_step_added_after_a_lay_leaves_each_step_without_lanes_sentences(b: w.Bench) -> None:
    """Given: the walkthrough's Proposal laid, then the user added a Step to writer before its step
    2, so that each Step after it moved down by one.
    When: the person types /lane:up changelog again, and up runs lay.py steps changelog.
    Then: each Step reads as the user wrote it, the new one among them, without a sentence that
    Lane laid, and no notes."""
    w.lay(b)
    path = os.path.join(b.changelog, "agents", "writer.md")
    text = w.read(path)
    for number in (4, 3, 2):
        text = text.replace(f"\n{number}. ", f"\n{number + 1}. ")
    text = text.replace("\n3. ", "\n2. Read `README.md` for the project's name.\n3. ", 1)
    w.write_files(b.changelog, {"agents/writer.md": text})
    c = w.converse(b)
    assert not c.type("/lane:up changelog").blocked
    given = json.loads(c.bash(b.lay_py("steps", "changelog")).output)
    texts = {s["number"]: s["text"] for s in given["steps"] if s["file"] == "agents/writer.md"}
    assert texts == {
        1: "Read `CHANGELOG.md` to learn its last version and its form, and `REVIEW.md`, where it"
        " exists, to learn what the entries lack.",
        2: "Read `README.md` for the project's name.",
        3: "Read the commits since then with `git log --oneline`.",
        4: "Write the new entries into `CHANGELOG.md`.",
        5: "Reply with the entries you wrote.",
    }
    assert given["notes"] == []
