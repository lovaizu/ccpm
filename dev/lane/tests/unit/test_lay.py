"""The unit cases of lay.py's code in domain/lay/, through `steps.read_steps`,
`laid.unlaid`, `laid.strip`, `laid.as_laid`, `laid.lay`, `check.check`, `show.render`,
`proposals.keep`, `proposals.find`, `write.write`, `hooks_file.replace_entries`, and
`claude.validate`: where Steps lie, the Laid read from the plugin's lanes.json,
Lane's sentences taken out, kept, and added once, what a Proposal must be and whose each fault is,
what print shows, where a Proposal is kept, each refusal of write, Lane's hook entries beside the
user's, and validate as the double of Claude Code gives it."""

from __future__ import annotations

import dataclasses
import json
import os
import re
import shutil
import tempfile
from typing import Any

import lane_data as d
import pytest
import walkthrough as w
from claude_code import claude_program
from form import After, Laid, LaidSentence, Move, OutOfForm, Route
from lay.check import Checked, Faults, check
from lay.claude import validate
from lay.hooks_file import replace_entries
from lay.laid import Note, as_laid, lay, strip, unlaid
from lay.proposals import find, keep
from lay.show import render
from lay.steps import Step, as_held, read_steps
from lay.write import Refused, write

STEP_2 = Step(
    "writer", "agents/writer.md", 2, "Read the commits since then with `git log --oneline`."
)
STEP_3 = Step("writer", "agents/writer.md", 3, "Write the new entries into `CHANGELOG.md`.")
LAID_2 = Step("writer", "agents/writer.md", 2, f"{STEP_2.text} Run only `git log --oneline`.")
LAID_3 = Step("writer", "agents/writer.md", 3, f"{STEP_3.text} Write only `CHANGELOG.md`.")
SENTENCES = {
    ("agents/writer.md", 2): "Run only `git log --oneline`.",
    ("agents/writer.md", 3): "Write only `CHANGELOG.md`.",
}
# Each sentence of writer's Lanes, its end on step 4 among them.
WRITERS = {**SENTENCES, ("agents/writer.md", 4): d.LAID.sentences[2].text}


@pytest.fixture
def plugin(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> str:
    """The walkthrough's changelog, and the system's temporary folder set to the case's own."""
    monkeypatch.setenv("TMPDIR", str(tmp_path / "temp"))
    monkeypatch.setattr(tempfile, "tempdir", None)
    os.makedirs(tmp_path / "temp")
    w.write_files(str(tmp_path / "changelog"), w.FILES)
    return str(tmp_path / "changelog")


def shown_steps() -> list[Step]:
    """Each Step as the README's walkthrough shows it laid, by its role's file."""
    files = {
        "write": "skills/write/SKILL.md",
        "writer": "agents/writer.md",
        "reviewer": "agents/reviewer.md",
    }
    steps, role = [], ""
    for line in w.SHOWN.splitlines():
        heading = re.match(r"(?:Routes|Lanes) of (\w+)", line)
        numbered = re.match(r"(\d+)\. (.*)$", line)
        if heading:
            role = heading[1]
        elif numbered:
            steps.append(Step(role, files[role], int(numbered[1]), numbered[2]))
    return steps


def steps_of(plugin: str) -> dict[tuple[str, int], Step]:
    return {(s.file, s.number): s for s in read_steps(plugin)}


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_each_roles_steps_are_read_from_its_file(plugin: str) -> None:
    """Given: the walkthrough's changelog.
    When: read_steps reads it.
    Then: it gives write's step 1, writer's four, and reviewer's three, each as its file holds
    it."""
    steps = steps_of(plugin)
    assert len(steps) == 8
    assert steps[("agents/writer.md", 2)] == STEP_2
    assert steps[("skills/write/SKILL.md", 1)].role == "write"


@pytest.mark.supports("test_a_steps_file_two_roles_share_goes_to_the_user")
def test_steps_in_the_file_a_body_names_are_the_roles(plugin: str) -> None:
    """Given: writer's body naming `${CLAUDE_PLUGIN_ROOT}/writer-steps.md`, which holds its Steps.
    When: read_steps reads the plugin.
    Then: writer's Steps come from writer-steps.md."""
    body = "Your steps are in `${CLAUDE_PLUGIN_ROOT}/writer-steps.md`.\n"
    w.write_files(plugin, {"agents/writer.md": w.WRITER.split("## Steps")[0] + body})
    w.write_files(plugin, {"writer-steps.md": "## Steps\n\n1. Read.\n2. Write.\n"})
    writer = [s for s in read_steps(plugin) if s.role == "writer"]
    assert [(s.file, s.number, s.text) for s in writer] == [
        ("writer-steps.md", 1, "Read."),
        ("writer-steps.md", 2, "Write."),
    ]


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_a_name_in_a_body_that_is_no_file_of_the_plugin_holds_no_steps(plugin: str) -> None:
    """Given: writer's body naming `${CLAUDE_PLUGIN_ROOT}/scripts/check.sh`, which the plugin
    doesn't hold.
    When: read_steps reads the plugin.
    Then: writer's Steps are those of agents/writer.md alone."""
    before = read_steps(plugin)
    named = w.WRITER.replace(
        "## Steps", "Check with `${CLAUDE_PLUGIN_ROOT}/scripts/check.sh`.\n\n## Steps"
    )
    w.write_files(plugin, {"agents/writer.md": named})
    assert read_steps(plugin) == before


# The Step of write-steps.md that write's SKILL.md and approve's both name.
WRITE_STEP = Step("write", "write-steps.md", 1, "Have the entries written and reviewed.")
APPROVE_STEP = dataclasses.replace(WRITE_STEP, role="approve")


@pytest.mark.supports("test_a_steps_file_a_skill_and_its_command_share_is_the_skills")
@pytest.mark.parametrize(
    "tie",
    [
        lambda: d.route(d.After("first"), d.Move("wait", command="approve")),
        lambda: d.route(d.After("command", command="approve"), d.Move("no_more", result="good")),
    ],
    ids=["a Route waits for the command", "a Route goes after the command"],
)
def test_a_commands_step_from_its_skills_file_is_held_as_the_skills(tie: Any) -> None:
    """Given: write-steps.md's step 1, read as write's and as approve's, and a Route of write that
    waits for approve or goes after it.
    When: as_held gives the Steps as Lane holds them.
    Then: it gives write's alone."""
    assert as_held((WRITE_STEP, APPROVE_STEP), (tie(),)) == (WRITE_STEP,)


@pytest.mark.supports("test_a_steps_file_two_roles_share_goes_to_the_user")
def test_a_commands_step_that_no_route_ties_is_held_as_its_own() -> None:
    """Given: write-steps.md's step 1, read as write's and as approve's, and write's Routes, none
    of which waits for approve or goes after it.
    When: as_held gives the Steps as Lane holds them.
    Then: it gives both."""
    steps = (WRITE_STEP, APPROVE_STEP)
    assert as_held(steps, d.ROUTES_OF_WRITE) == steps


# The front matter of the command approve, which only the person runs.
APPROVE_FRONT = "---\nname: approve\ndescription: A.\ndisable-model-invocation: true\n---\n\n"
# A body that names write-steps.md as the file of its Steps.
NAMES_WRITE_STEPS = "Your steps are in `${CLAUDE_PLUGIN_ROOT}/write-steps.md`.\n"


@pytest.mark.supports("test_a_steps_file_a_skill_and_its_command_share_is_the_skills")
def test_a_steps_file_a_skill_and_its_commands_share_is_read_once_as_the_skills(
    plugin: str,
) -> None:
    """Given: changelog whose skill write and command approve, which sets
    `disable-model-invocation: true` and comes first by name, both name write-steps.md by
    `${CLAUDE_PLUGIN_ROOT}/`, and approve's SKILL.md holds a Step of its own.
    When: read_steps reads the plugin, with no Proposal.
    Then: it gives write-steps.md's step 1 once, as write's, and approve's own Step as
    approve's."""
    w.write_files(
        plugin,
        {
            "skills/write/SKILL.md": w.WRITE.split("## Steps")[0] + NAMES_WRITE_STEPS,
            "skills/approve/SKILL.md": APPROVE_FRONT
            + NAMES_WRITE_STEPS
            + "\n## Steps\n\n1. Go on.\n",
            "write-steps.md": "## Steps\n\n1. Have the entries written and reviewed.\n",
        },
    )
    skills = [s for s in read_steps(plugin) if s.role in ("write", "approve")]
    assert skills == [
        Step("approve", "skills/approve/SKILL.md", 1, "Go on."),
        WRITE_STEP,
    ]


@pytest.mark.supports("test_a_steps_file_two_roles_share_goes_to_the_user")
def test_a_steps_file_two_skills_share_is_read_as_each(plugin: str) -> None:
    """Given: changelog whose skills write and approve, neither setting
    `disable-model-invocation: true`, both name write-steps.md by `${CLAUDE_PLUGIN_ROOT}/`.
    When: read_steps reads the plugin.
    Then: it gives write-steps.md's step 1 as approve's and as write's, so that check names the
    file to the user."""
    approve = APPROVE_FRONT.replace("disable-model-invocation: true\n", "")
    w.write_files(
        plugin,
        {
            "skills/write/SKILL.md": w.WRITE.split("## Steps")[0] + NAMES_WRITE_STEPS,
            "skills/approve/SKILL.md": approve + NAMES_WRITE_STEPS,
            "write-steps.md": "## Steps\n\n1. Have the entries written and reviewed.\n",
        },
    )
    skills = [s for s in read_steps(plugin) if s.role in ("write", "approve")]
    assert skills == [APPROVE_STEP, WRITE_STEP]


@pytest.mark.supports("test_a_move_that_waits_for_the_person_lets_the_turn_end")
def test_a_commands_steps_are_read_as_its_own(plugin: str) -> None:
    """Given: changelog with a command skill approve whose SKILL.md holds one Step.
    When: read_steps reads the plugin.
    Then: it gives approve's Step from skills/approve/SKILL.md."""
    front = "---\nname: approve\ndescription: A.\ndisable-model-invocation: true\n---\n\n"
    approve = front + "## Steps\n\n1. Go on.\n"
    w.write_files(plugin, {"skills/approve/SKILL.md": approve})
    assert steps_of(plugin)[("skills/approve/SKILL.md", 1)].text == "Go on."


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_a_role_with_no_steps_gives_none(plugin: str) -> None:
    """Given: changelog whose reviewer.md holds no `## Steps`.
    When: read_steps reads the plugin.
    Then: it gives no Step of reviewer."""
    w.write_files(plugin, {"agents/reviewer.md": w.REVIEWER.split("## Steps")[0]})
    assert not [s for s in read_steps(plugin) if s.role == "reviewer"]


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_a_folder_in_skills_with_no_skill_md_is_no_role(plugin: str) -> None:
    """Given: changelog with skills/shared/, which holds a template and no SKILL.md, so that Claude
    Code loads no skill from it.
    When: read_steps reads the plugin.
    Then: it gives the same Steps as without the folder."""
    before = read_steps(plugin)
    w.write_files(plugin, {"skills/shared/template.md": "## Steps\n\n1. Not a skill's.\n"})
    assert read_steps(plugin) == before


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_a_folder_that_isnt_there_is_refused(tmp_path: Any) -> None:
    """Given: a path where no folder lies.
    When: read_steps reads it.
    Then: it raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_steps(str(tmp_path / "nowhere"))


def copied(plugin: str) -> None:
    """Puts a copy of Lane's code in the plugin's hooks/lane/, as lay.py write puts it."""
    shutil.copytree(os.path.join(w.LANE, "hooks", "lane"), os.path.join(plugin, "hooks", "lane"))


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_a_plugin_lane_never_laid_in_gives_its_steps_as_they_are(plugin: str) -> None:
    """Given: changelog with no hooks/lanes.json.
    When: unlaid reads it.
    Then: it gives each Step as read_steps reads it, with no notes."""
    assert unlaid(plugin) == (read_steps(plugin), ())


@pytest.mark.supports("test_a_call_the_guard_cant_check_is_stopped_with_who_must_fix_it")
def test_a_laid_out_of_form_is_refused(plugin: str) -> None:
    """Given: changelog whose hooks/lanes.json is out of its form.
    When: unlaid reads it.
    Then: it raises OutOfForm."""
    w.write_files(plugin, {"hooks/lanes.json": "{}"})
    with pytest.raises(OutOfForm):
        unlaid(plugin)


@pytest.mark.supports("test_steps_after_a_lay_come_without_lanes_sentences")
def test_a_sentence_still_word_for_word_is_taken_out() -> None:
    """Given: writer's steps 2 and 3, each holding the sentence Lane laid.
    When: strip takes out the Laid's text.
    Then: each Step reads as the user wrote it, with no note."""
    assert strip((LAID_2, LAID_3), d.LAID) == ((STEP_2, STEP_3), ())


@pytest.mark.supports("test_steps_after_a_lay_come_without_lanes_sentences")
def test_the_end_laid_on_the_last_step_is_taken_out() -> None:
    """Given: writer's step 4, holding the sentence of the Lane on its last Step.
    When: strip takes out the Laid's text.
    Then: the Step reads as the user wrote it."""
    step = Step("writer", "agents/writer.md", 4, "Reply with the entries you wrote.")
    laid = dataclasses.replace(step, text=f"{step.text} {WRITERS[('agents/writer.md', 4)]}")
    assert strip((laid,), d.LAID) == ((step,), ())


@pytest.mark.supports("test_steps_after_a_lay_come_without_lanes_sentences")
def test_a_sentence_still_held_before_the_users_own_is_taken_out() -> None:
    """Given: writer's step 3, holding the sentence Lane laid, then a sentence the user added after
    it.
    When: strip takes out the Laid's text.
    Then: the Step keeps the user's words, both before and after, with no note."""
    added = "Keep its form."
    held = dataclasses.replace(LAID_3, text=f"{LAID_3.text} {added}")
    mine = dataclasses.replace(STEP_3, text=f"{STEP_3.text} {added}")
    assert strip((held,), d.LAID) == ((mine,), ())


@pytest.mark.supports("test_a_step_added_after_a_lay_leaves_each_step_without_lanes_sentences")
def test_a_sentence_on_a_step_that_moved_down_is_taken_out_where_it_now_lies() -> None:
    """Given: writer's steps 2 to 4, each holding the sentence Lane laid, moved down to 3 to 5 by a
    Step the user added as step 2.
    When: strip takes out the Laid's text.
    Then: each Step reads as the user wrote it, the new one among them, with no note."""
    added = Step("writer", "agents/writer.md", 2, "Read `README.md` for the project's name.")
    last = Step("writer", "agents/writer.md", 5, "Reply with the entries you wrote.")
    ended = dataclasses.replace(last, text=f"{last.text} {WRITERS[('agents/writer.md', 4)]}")
    moved = (dataclasses.replace(LAID_2, number=3), dataclasses.replace(LAID_3, number=4), ended)
    mine = (dataclasses.replace(STEP_2, number=3), dataclasses.replace(STEP_3, number=4), last)
    assert strip((added, *moved), d.LAID) == ((added, *mine), ())


@pytest.mark.supports("test_a_sentence_the_user_changed_stays_as_theirs")
def test_a_sentence_the_user_changed_is_kept_with_a_note() -> None:
    """Given: writer's step 3, whose laid sentence the user changed to name NEWS.md too.
    When: strip takes out the Laid's text.
    Then: the Step keeps the user's sentence, and a Note names the laid and the user's."""
    now = "Write only `CHANGELOG.md` and `NEWS.md`."
    changed = Step("writer", "agents/writer.md", 3, f"{STEP_3.text} {now}")
    steps, notes = strip((changed,), d.LAID)
    assert steps == (changed,)
    assert notes == (Note("agents/writer.md", 3, "Write only `CHANGELOG.md`.", now),)


@pytest.mark.supports("test_steps_give_each_step_of_each_role")
def test_steps_with_nothing_laid_are_left_as_they_are() -> None:
    """Given: writer's steps 2 and 3, and an empty Laid.
    When: strip takes out the Laid's text.
    Then: it gives them unchanged."""
    assert strip((STEP_2, STEP_3), Laid(())) == ((STEP_2, STEP_3), ())


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_a_steps_sentence_comes_after_its_own_words() -> None:
    """Given: writer's steps 2 and 3, and each Lane's sentence.
    When: as_laid gives each Step as it'll read.
    Then: each sentence follows its Step's own words."""
    assert as_laid((STEP_2, STEP_3), SENTENCES) == (LAID_2, LAID_3)


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_a_sentence_the_step_already_says_isnt_added() -> None:
    """Given: writer's step 2, which already says `Run only `git log --oneline`.`.
    When: as_laid gives it as it'll read.
    Then: it reads unchanged, the sentence said once."""
    assert as_laid((LAID_2,), SENTENCES) == (LAID_2,)


@pytest.mark.supports("test_yes_lays_the_proposal_into_the_plugin")
def test_lay_writes_each_sentence_into_its_file(plugin: str) -> None:
    """Given: the walkthrough's changelog.
    When: lay writes writer's steps 2 and 3 as laid.
    Then: agents/writer.md holds them, the rest as it was, and the new Laid names each sentence."""
    laid = lay(plugin, (LAID_2, LAID_3))
    text = w.read(os.path.join(plugin, "agents", "writer.md"))
    assert f"2. {LAID_2.text}\n3. {LAID_3.text}\n" in text and text.startswith("---\nname: writer")
    assert set(laid.sentences) == {
        LaidSentence("agents/writer.md", 2, "Run only `git log --oneline`."),
        LaidSentence("agents/writer.md", 3, "Write only `CHANGELOG.md`."),
    }


@pytest.mark.supports("test_a_failed_validate_puts_back_each_file")
def test_lay_into_a_file_that_cant_be_written_is_refused(plugin: str) -> None:
    """Given: changelog whose agents/writer.md can't be written.
    When: lay writes writer's steps as laid.
    Then: it raises OSError."""
    os.chmod(os.path.join(plugin, "agents", "writer.md"), 0o444)
    os.chmod(os.path.join(plugin, "agents"), 0o555)
    try:
        with pytest.raises(OSError):
            lay(plugin, (LAID_2,))
    finally:
        os.chmod(os.path.join(plugin, "agents"), 0o755)


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_a_proposal_that_can_stand_gives_each_sentence(plugin: str) -> None:
    """Given: the walkthrough's changelog, its Steps, and its Proposal.
    When: check checks the Proposal.
    Then: it gives Checked, with each Lane's sentence by its Step."""
    checked = check(plugin, d.proposal(), read_steps(plugin))
    assert isinstance(checked, Checked)
    assert {k: v for k, v in checked.sentences.items() if k[0] == "agents/writer.md"} == WRITERS


@pytest.mark.supports("test_a_lane_on_a_step_that_isnt_there_goes_back_to_up")
@pytest.mark.parametrize(
    "lane",
    [
        lambda: d.lane("writer", "agents/writer.md", 2, "run_once"),
        lambda: dataclasses.replace(d.run_only(), step=9),
        lambda: d.lane("writer", "agents/writer.md", 2, "run_only"),
    ],
    ids=["no such type", "no such Step", "a value missing"],
)
def test_a_lane_that_cant_stand_is_ups_to_mend(plugin: str, lane: Any) -> None:
    """Given: the walkthrough's Proposal with one Lane of no type, on no Step, or without its value.
    When: check checks it.
    Then: it gives Faults, each for up to mend, none for the user."""
    proposal = d.proposal()
    proposal = dataclasses.replace(proposal, lanes=(*proposal.lanes, lane()))
    faults = check(plugin, proposal, read_steps(plugin))
    assert isinstance(faults, Faults) and faults.proposal and not faults.plugin


@pytest.mark.supports("test_a_role_with_no_end_on_its_last_step_goes_back_to_up")
@pytest.mark.parametrize(
    "left_out, named",
    [
        (lambda: d.REVIEWER_END, "reviewer"),
        (lambda: d.WRITE_END, "write"),
        (lambda: d.WRITER_END, "writer"),
    ],
    ids=["a subagent a Route starts", "the skill", "the first subagent"],
)
def test_a_role_with_no_end_on_its_last_step_is_ups_to_mend(
    plugin: str, left_out: Any, named: str
) -> None:
    """Given: the walkthrough's Proposal without the Lane on reviewer's, write's, or writer's last
    Step.
    When: check checks it.
    Then: it gives Faults for up to mend, naming the role and ends_by_result."""
    proposal = d.proposal()
    lanes = tuple(x for x in proposal.lanes if x != left_out())
    faults = check(plugin, dataclasses.replace(proposal, lanes=lanes), read_steps(plugin))
    assert isinstance(faults, Faults) and not faults.plugin
    assert any(named in f and "ends_by_result" in f for f in faults.proposal)


@pytest.mark.supports("test_a_role_with_no_end_on_its_last_step_goes_back_to_up")
@pytest.mark.parametrize(
    "step, stands",
    [(4, True), (3, False), (1, False)],
    ids=["its last Step", "the Step before it", "its first Step"],
)
def test_an_end_on_a_step_other_than_the_roles_last_is_ups_to_mend(
    plugin: str, step: int, stands: bool
) -> None:
    """Given: the walkthrough's Proposal with the Lane of ends_by_result of writer on its step 4,
    3, or 1.
    When: check checks it.
    Then: it gives Checked where the Lane lies on writer's last Step, step 4, and else Faults for
    up to mend."""
    proposal = d.proposal()
    lanes = tuple(
        dataclasses.replace(x, step=step) if x == d.WRITER_END else x for x in proposal.lanes
    )
    given = check(plugin, dataclasses.replace(proposal, lanes=lanes), read_steps(plugin))
    assert isinstance(given, Checked if stands else Faults)


@pytest.mark.supports("test_a_file_that_cant_carry_the_proposal_goes_to_the_user")
@pytest.mark.parametrize(
    "files, named",
    [
        (
            {"agents/reviewer.md": w.REVIEWER.replace("background: true\n", "")},
            "agents/reviewer.md",
        ),
        ({"hooks/adapters/text.py": "print('{}')\n"}, "hooks/adapters/text.py"),
    ],
    ids=["a subagent not in the background", "an adapter the Proposal doesn't name"],
)
def test_a_file_that_cant_carry_the_proposal_is_the_users_to_fix(
    plugin: str, files: dict[str, str], named: str
) -> None:
    """Given: changelog with a subagent's file that doesn't set `background: true`, or an adapter
    the Proposal doesn't name.
    When: check checks the walkthrough's Proposal.
    Then: it gives Faults for the user, naming the file."""
    w.write_files(plugin, files)
    faults = check(plugin, d.proposal(), read_steps(plugin))
    assert isinstance(faults, Faults) and any(named in f for f in faults.plugin)


@pytest.mark.supports("test_an_adapter_the_proposal_doesnt_name_goes_to_the_user")
def test_a_folder_in_hooks_adapters_is_no_adapter(plugin: str) -> None:
    """Given: changelog whose hooks/adapters/ holds only __pycache__/, which Python leaves beside an
    adapter that another imports.
    When: check checks the walkthrough's Proposal, which names no adapter.
    Then: it gives Checked."""
    os.makedirs(os.path.join(plugin, "hooks", "adapters", "__pycache__"))
    assert isinstance(check(plugin, d.proposal(), read_steps(plugin)), Checked)


@pytest.mark.supports("test_a_route_command_the_model_may_call_goes_to_the_user")
def test_a_route_that_waits_for_the_persons_reply_names_no_command(plugin: str) -> None:
    """Given: the walkthrough's Proposal whose move after reviewer's `good` may also wait for the
    person's reply, an empty `wait`.
    When: check checks it.
    Then: it gives Checked, as no command's SKILL.md is to be read."""
    proposal = d.proposal()
    good = dataclasses.replace(
        proposal.routes[3], moves=(d.Move("wait", command=""), *proposal.routes[3].moves)
    )
    proposal = dataclasses.replace(proposal, routes=(*proposal.routes[:3], good))
    assert isinstance(check(plugin, proposal, read_steps(plugin)), Checked)


@pytest.mark.supports("test_a_steps_file_two_roles_share_goes_to_the_user")
def test_a_steps_file_two_skills_share_is_the_users_to_fix(plugin: str) -> None:
    """Given: changelog whose skill write and skill tidy, which no Route ties to write, both name
    write-steps.md by `${CLAUDE_PLUGIN_ROOT}/` as the file of their Steps.
    When: check checks the walkthrough's Proposal.
    Then: it gives Faults for the user, naming write-steps.md."""
    body = "Your steps are in `${CLAUDE_PLUGIN_ROOT}/write-steps.md`.\n"
    tidy = "---\nname: tidy\ndescription: Tidies.\n---\n\n" + body
    w.write_files(plugin, {"skills/write/SKILL.md": w.WRITE + body, "skills/tidy/SKILL.md": tidy})
    w.write_files(plugin, {"write-steps.md": "## Steps\n\n1. Keep it short.\n"})
    faults = check(plugin, d.proposal(), read_steps(plugin))
    assert isinstance(faults, Faults) and any("write-steps.md" in f for f in faults.plugin)


@pytest.mark.supports("test_a_route_after_a_command_the_model_may_call_goes_to_the_user")
def test_a_command_a_route_goes_after_that_the_model_may_call_is_the_users_to_fix(
    plugin: str,
) -> None:
    """Given: changelog with a command skill pause whose SKILL.md doesn't set
    `disable-model-invocation: true`.
    When: check checks the walkthrough's Proposal with a Route of write after pause.
    Then: it gives Faults for the user, naming skills/pause/SKILL.md."""
    pause = "---\nname: pause\ndescription: Pauses.\n---\n\n## Steps\n\n1. Stop.\n"
    w.write_files(plugin, {"skills/pause/SKILL.md": pause})
    proposal = d.proposal()
    paused = d.route(d.After("command", command="pause"), d.Move("no_more", result="paused"))
    proposal = dataclasses.replace(proposal, routes=(*proposal.routes, paused))
    faults = check(plugin, proposal, read_steps(plugin))
    assert isinstance(faults, Faults) and any("skills/pause/SKILL.md" in f for f in faults.plugin)


@pytest.mark.supports("test_up_shows_the_walkthroughs_proposal")
def test_print_shows_the_walkthroughs_proposal_as_the_readme_does() -> None:
    """Given: the walkthrough's Proposal, each Step as it'll read, and the ID b9fd8fd8.
    When: render gives what lay.py print shows.
    Then: it reads word for word as the README's walkthrough shows."""
    steps = shown_steps()
    assert render(d.proposal(), steps, w.README_ID, "changelog").rstrip("\n") == w.SHOWN


def routes_shown(*added: Route) -> list[str]:
    """The rows of write's Routes that render shows for the walkthrough's Proposal with the Routes
    added."""
    proposal = d.proposal()
    proposal = dataclasses.replace(proposal, routes=(*proposal.routes, *added))
    shown = render(proposal, shown_steps(), w.README_ID, "changelog")
    return shown.split("\n\n")[0].split("\n")[1:]


@pytest.mark.supports("test_a_steps_file_a_skill_and_its_command_share_is_the_skills")
def test_a_route_after_a_command_shows_the_person_typing_it() -> None:
    """Given: the walkthrough's Proposal with a Route of write after the command approve that
    starts no more.
    When: render gives what lay.py print shows.
    Then: the Route's row reads `the person types approve`, then `start no more`."""
    after = d.route(After("command", command="approve"), Move("no_more", result="good"))
    rows = routes_shown(after)
    assert rows[-1] == "  the person types approve  start no more"


@pytest.mark.supports("test_lay_of_an_id_no_proposal_has_is_refused")
def test_a_kept_proposal_is_found_by_its_id(plugin: str) -> None:
    """Given: the walkthrough's Proposal and Steps.
    When: keep keeps it, and find looks for its ID.
    Then: find gives it back, with the plugin and the Steps, from the plugin's folder of
    Proposals."""
    steps = read_steps(plugin)
    pid = keep(plugin, d.proposal(), steps)
    kept = find(plugin, pid)
    assert kept and (kept.id, kept.proposal, kept.steps) == (pid, d.proposal(), steps)
    folder = os.path.join(os.environ["TMPDIR"], "lane")
    assert any(name.endswith("-changelog") for name in os.listdir(folder))


@pytest.mark.supports("test_an_ai_writes_its_change_into_the_step_before_it_lays")
def test_each_kept_proposal_has_its_own_id(plugin: str) -> None:
    """Given: the walkthrough's Proposal and Steps.
    When: keep keeps it twice.
    Then: it gives two IDs."""
    steps = read_steps(plugin)
    assert keep(plugin, d.proposal(), steps) != keep(plugin, d.proposal(), steps)


@pytest.mark.supports("test_lay_of_an_id_no_proposal_has_is_refused")
def test_an_id_no_proposal_has_finds_none(plugin: str) -> None:
    """Given: no Proposal kept.
    When: find looks for b9fd8fd8.
    Then: it gives None."""
    assert find(plugin, "b9fd8fd8") is None


@pytest.mark.supports("test_lay_of_an_id_no_proposal_has_is_refused")
def test_lay_of_an_id_no_proposal_has_is_refused_by_write(plugin: str) -> None:
    """Given: no Proposal kept.
    When: write lays b9fd8fd8.
    Then: it raises Refused, and changes no file."""
    with pytest.raises(Refused):
        write(plugin, "b9fd8fd8", w.LANE)
    assert not os.path.exists(os.path.join(plugin, "hooks"))


@pytest.mark.supports("test_lay_keeps_the_users_hook_entries")
def test_lanes_entries_go_in_a_new_hooks_json(plugin: str) -> None:
    """Given: changelog with no hooks/hooks.json.
    When: replace_entries puts Lane's entries in.
    Then: hooks.json holds Lane's entries alone."""
    entries = {
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3",
                        "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"],
                    }
                ]
            }
        ]
    }
    replace_entries(plugin, entries)
    assert json.loads(w.read(os.path.join(plugin, "hooks", "hooks.json")))["hooks"] == entries


@pytest.mark.supports("test_lay_again_replaces_what_the_earlier_lay_added")
def test_an_earlier_lanes_entries_are_replaced_and_the_users_kept(plugin: str) -> None:
    """Given: changelog's hooks.json with an earlier Lane's Stop entry and the user's own Stop
    entry.
    When: replace_entries puts Lane's new entries in.
    Then: the earlier Lane's entry is gone, the new one is there once, and the user's stands."""
    hook = "${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py"
    earlier = {"type": "command", "command": "python3", "args": [hook], "timeout": 5}
    own = {"type": "command", "command": "echo", "args": ["done"]}
    w.write_files(
        plugin, {"hooks/hooks.json": json.dumps({"hooks": {"Stop": [{"hooks": [earlier, own]}]}})}
    )
    new = {"type": "command", "command": "python3", "args": [hook], "onFailure": "block"}
    replace_entries(plugin, {"Stop": [{"hooks": [new]}]})
    stop = json.loads(w.read(os.path.join(plugin, "hooks", "hooks.json")))["hooks"]["Stop"]
    held = [h for group in stop for h in group["hooks"]]
    assert earlier not in held and held.count(new) == 1 and own in held


@pytest.mark.supports("test_a_failed_validate_puts_back_each_file")
def test_a_hooks_json_out_of_form_is_refused(plugin: str) -> None:
    """Given: changelog whose hooks.json isn't JSON.
    When: replace_entries puts Lane's entries in.
    Then: it raises OutOfForm."""
    w.write_files(plugin, {"hooks/hooks.json": "{"})
    with pytest.raises(OutOfForm):
        replace_entries(plugin, {})


@pytest.mark.supports("test_yes_lays_the_proposal_into_the_plugin")
def test_validate_of_a_plugin_claude_code_takes_passes(
    plugin: str, tmp_path: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given: the double's `claude` on the PATH, and the walkthrough's changelog.
    When: validate runs `claude plugin validate` on changelog.
    Then: it gives passed, with what it said."""
    monkeypatch.setenv("PATH", claude_program(str(tmp_path / "bin")))
    given = validate(plugin)
    assert given.passed and "Validation passed" in given.said


@pytest.mark.supports("test_a_failed_validate_puts_back_each_file")
@pytest.mark.parametrize(
    "manifest, on_path",
    [('{"name": 1}\n', True), ('{"name": "changelog"}\n', False)],
    ids=["a manifest Claude Code doesn't take", "no claude on the PATH"],
)
def test_validate_that_fails_doesnt_pass(
    plugin: str, tmp_path: Any, monkeypatch: pytest.MonkeyPatch, manifest: str, on_path: bool
) -> None:
    """Given: changelog whose plugin.json gives a `name` that isn't a string, with the double's
    `claude` on the PATH; or a PATH that holds no `claude`.
    When: validate runs `claude plugin validate` on changelog.
    Then: it gives not passed, saying what failed."""
    w.write_files(plugin, {".claude-plugin/plugin.json": manifest})
    folder = claude_program(str(tmp_path / "bin")) if on_path else str(tmp_path / "empty")
    monkeypatch.setenv("PATH", folder)
    given = validate(plugin)
    assert not given.passed and given.said
