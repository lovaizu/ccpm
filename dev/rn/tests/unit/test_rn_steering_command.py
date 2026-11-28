"""The unit cases of steering/command.py, steering's command line as the orchestrator runs it: each
aim taken in, each mark of the stage, each written to the steering alone, what's due read, each
start of a task's next role with what it's given, and each refusal: a steering missing or out of its
schema, an aim that isn't JSON, leaves its schema, or that the steering refuses, a mark that the
steering refuses, a hand-over or an end with a TODO left, a start that can't be, and arguments of
another form."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any
from urllib.parse import quote

import pytest
import rn_files
from host import run
from place import WorkPlace
from repo_files import git, write_files
from steering.command import USAGE, main

NAME = "20261126-invoice-from-statement"
FOLDER = f".rn/{NAME}"
MADE = {"result": "made", "files": [rn_files.COMMAND]}


@pytest.fixture
def made(tmp_path: Any) -> WorkPlace:
    """The work in the user's repository with origin, in its own worktree on the work's branch, its
    folder empty."""
    return rn_files.work_with_origin(str(tmp_path), NAME)


def steering(work: WorkPlace, value: Any) -> None:
    """Writes the steering, and commits it on the work's branch."""
    rn_files.write_json(work.steering, value)
    git(work.worktree, "add", "-A")
    git(work.worktree, "commit", "-q", "-m", "steering")


def call(work: WorkPlace, *argv: str, words: str = "") -> tuple[int, str, str]:
    """What `steering` gives with the arguments on the work, and the words given on stdin."""
    given = argv[:1] + (FOLDER,) + argv[1:]
    return main(given, work.worktree, rn_files.RN, lambda: words, run)


def unchanged(work: WorkPlace) -> bool:
    """Whether the work's worktree holds nothing but what was committed, as no script commits."""
    return git(work.worktree, "status", "--porcelain") == ""


def held(work: WorkPlace) -> Any:
    with open(work.steering, encoding="utf-8") as f:
        return json.load(f)


def test_the_first_aim_makes_the_steering_and_commits_nothing(made: WorkPlace) -> None:
    """Given the work with no steering, and the walkthrough's aim.
    When it's given to `steering aim`.
    Then the steering holds it, not committed, as the orchestrator commits, and the command is
    due to make."""
    before = git(made.worktree, "rev-parse", "HEAD")
    assert call(made, "aim", words=json.dumps(rn_files.aim())) == (
        0,
        f"make\t{rn_files.COMMAND}\tcode\tgenerator\n",
        "",
    )
    assert git(made.worktree, "rev-parse", "HEAD") == before
    assert held(made) == rn_files.steering()


def test_a_later_aim_keeps_the_stage(made: WorkPlace) -> None:
    """Given a steering in the user's hands with no task left, and an aim with a task to mend.
    When it's given to `steering aim`.
    Then the steering holds the task, and keeps the stage, so the try waits once it's mended."""
    steering(made, rn_files.steering(paths=(), stage="trying"))
    code, _, _ = call(made, "aim", words=json.dumps(rn_files.aim(rn_files.TASKS[:1])))
    assert (code, held(made)) == (0, rn_files.steering((rn_files.COMMAND,), stage="trying"))


@pytest.mark.parametrize(
    ("words", "says"),
    [
        ("{", "the aim isn't JSON"),
        (json.dumps({}), "aim.schema.json: /ost: is required"),
        (json.dumps(rn_files.aim([{**rn_files.TASKS[0], "next": "generator"}])), "has had its 2"),
    ],
    ids=["not-json", "schema", "refused"],
)
def test_an_aim_that_can_not_be_taken_in_is_refused_and_changes_nothing(
    made: WorkPlace, words: str, says: str
) -> None:
    """Given a steering whose command has had its judged Rounds, and an aim that isn't JSON, leaves
    its schema, or makes the command again.
    When it's given to `steering aim`.
    Then it gives 1 saying why, and changes nothing."""
    at(made, next="weigh", entry="content-2", judged=2)
    code, _, err = call(made, "aim", words=words)
    assert (code, says in err, unchanged(made)) == (1, True, True)


@pytest.mark.parametrize(
    ("stage", "line"),
    [("trying", f"trying\t{rn_files.SOLUTION}\n"), ("inspected", "ended\n")],
)
def test_each_mark_is_written_and_gives_whats_due(made: WorkPlace, stage: str, line: str) -> None:
    """Given a steering with no task left.
    When the work is marked trying, or inspected.
    Then the steering holds it, and the user's try, or the work's end, is due."""
    steering(made, rn_files.steering(paths=()))
    assert call(made, "mark", stage) == (0, line, "")
    assert held(made)["stage"] == stage


@pytest.mark.parametrize("stage", ["trying", "inspected"])
def test_a_hand_over_or_an_end_with_a_todo_left_is_refused(made: WorkPlace, stage: str) -> None:
    """Given a steering with no task left, and the work's guide still holding a TODO.
    When the work is marked trying, or inspected.
    Then it gives 1 naming the TODO's place, and changes nothing, as what it marks is still to
    make."""
    write_files(made.worktree, {rn_files.GUIDE: "# Guide\n\nTODO: the rules.\n"})
    steering(made, rn_files.steering(paths=()))
    code, _, err = call(made, "mark", stage)
    assert (code, f"{rn_files.GUIDE}:3: TODO" in err, unchanged(made)) == (1, True, True)


def test_a_mark_that_can_not_be_is_refused_and_changes_nothing(made: WorkPlace) -> None:
    """Given the walkthrough's steering.
    When the work is marked at a stage that isn't one.
    Then it gives 1 saying why, and changes nothing."""
    steering(made, rn_files.steering())
    code, _, err = call(made, "mark", "waiting")
    assert (code, "isn't a stage" in err, unchanged(made)) == (1, True, True)


def test_whats_due_is_read_from_the_steering(made: WorkPlace) -> None:
    """Given the walkthrough's steering.
    When `steering due` runs.
    Then the command is due to make."""
    steering(made, rn_files.steering())
    assert call(made, "due") == (0, f"make\t{rn_files.COMMAND}\tcode\tgenerator\n", "")


def test_a_steering_out_of_its_schema_is_refused(made: WorkPlace) -> None:
    """Given a steering with no tasks.
    When `steering due` runs.
    Then it gives 1 naming the place."""
    value = rn_files.steering()
    del value["tasks"]
    steering(made, value)
    code, _, err = call(made, "due")
    assert (code, "/tasks: is required" in err) == (1, True)


def test_a_mark_on_the_work_with_no_steering_is_refused(made: WorkPlace) -> None:
    """Given the work with no steering yet.
    When the work is marked trying.
    Then it gives 1 saying that no steering lies there."""
    code, _, err = call(made, "mark", "trying")
    assert (code, "no the steering lies there" in err) == (1, True)


@pytest.mark.parametrize("argv", [(), ("push", FOLDER), ("due",), ("aim",), ("mark", FOLDER)])
def test_arguments_of_another_form_give_the_usage(argv: Sequence[str]) -> None:
    """Given no subcommand, one that isn't steering's, or too few arguments.
    When steering runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN, str, run) == (2, "", USAGE)


def rounds_of(work: WorkPlace, path: str = rn_files.COMMAND) -> str:
    """The folder of the deliverable's Rounds and Fixes."""
    return os.path.join(work.rounds, quote(path, safe=""))


def at(work: WorkPlace, **fields: Any) -> None:
    """Writes the walkthrough's steering, its command with the fields given."""
    value = rn_files.steering()
    value["tasks"][0].update(fields)
    steering(work, value)


def command_of(work: WorkPlace) -> Any:
    return held(work)["tasks"][0]


def practice_of(kind: str) -> str:
    return os.path.join(rn_files.PRACTICES, kind)


def given(made: WorkPlace, role: str, *things: tuple[str, str]) -> str:
    """What starting the command's role gives: its name, then each thing it's given."""
    lines = [("Worktree", made.worktree), ("Deliverable", rn_files.COMMAND), *things]
    return role + "\n" + "".join(f"{name}: {value}\n" for name, value in lines)


def kept(made: WorkPlace, place: str, folder: str) -> list[tuple[str, str]]:
    """What each role but the evaluator is given beside the worktree and the deliverable."""
    return [("Steering", made.steering), ("Kind", "code"), (place, folder)]


def test_a_round_of_content_starts_in_a_new_folder_and_again_in_the_same(made: WorkPlace) -> None:
    """Given the walkthrough's steering, its command not started.
    When its next role is started, twice, as a stop left the first with no result.
    Then each gives its generator, content-1, and the code best practice, and the steering holds
    content-1 as its entry."""
    at(made)
    folder = os.path.join(rounds_of(made), "content-1")
    want = (
        0,
        given(
            made, "generator", *kept(made, "Round", folder), ("Best practice", practice_of("code"))
        ),
        "",
    )
    assert (call(made, "start", rn_files.COMMAND), call(made, "start", rn_files.COMMAND)) == (
        want,
        want,
    )
    assert (os.path.isdir(folder), command_of(made)["entry"]) == (True, "content-1")


def test_a_round_made_again_starts_past_the_last(made: WorkPlace) -> None:
    """Given a command whose content-1 and fix-2 are made, and that the orchestrator has made again.
    When its next role is started.
    Then it's content-3."""
    at(made, next="generator", judged=1)
    rn_files.write_json(os.path.join(rounds_of(made), "content-1", "generator.json"), MADE)
    os.makedirs(os.path.join(rounds_of(made), "fix-2"))
    code, out, _ = call(made, "start", rn_files.COMMAND)
    assert (code, f"Round: {os.path.join(rounds_of(made), 'content-3')}" in out) == (0, True)


def test_the_evaluator_judges_its_round_by_the_conditions_alone(made: WorkPlace) -> None:
    """Given a command whose content-1 is made, its evaluator next.
    When its next role is started.
    Then it gives the evaluator, the work, content-1, and judges-by.json there, holding the
    conditions, the outcome, and the target solution with its assumptions."""
    at(made, next="evaluator", entry="content-1")
    folder = os.path.join(rounds_of(made), "content-1")
    os.makedirs(folder)
    judges = os.path.join(folder, "judges-by.json")
    want = given(made, "evaluator", ("Round", folder), ("Judges by", judges))
    want = want.replace("evaluator\n", f"evaluator\nWork: {made.folder}\n", 1)
    assert call(made, "start", rn_files.COMMAND) == (0, want, "")
    solution = rn_files.ost()["opportunities"][0]["solutions"][0]
    with open(judges, encoding="utf-8") as f:
        assert json.load(f) == {
            **rn_files.judged_by("code"),
            "outcome": rn_files.OUTCOME,
            "solution": rn_files.SOLUTION,
            "assumptions": solution["assumptions"],
        }


@pytest.mark.parametrize(
    ("results", "weighed"),
    [
        (("generator", "evaluator"), "evaluator"),
        (("generator",), "generator"),
        (("fixer",), "fixer"),
    ],
    ids=["findings", "point", "fix-point"],
)
def test_a_weighing_takes_the_result_to_weigh(
    made: WorkPlace, results: Sequence[str], weighed: str
) -> None:
    """Given a command waiting on the orchestrator's weighing of content-1, which holds an
    evaluator's findings, or a generator's or a fixer's point alone.
    When its next role is started.
    Then it gives the weighing, with the result to weigh, and changes nothing."""
    at(made, next="weigh", entry="content-1")
    folder = os.path.join(rounds_of(made), "content-1")
    for role in results:
        rn_files.write_json(os.path.join(folder, f"{role}.json"), {"result": "x"})
    before = held(made)
    assert call(made, "start", rn_files.COMMAND) == (
        0,
        f"weigh\t{os.path.join(folder, weighed + '.json')}\n",
        "",
    )
    assert held(made) == before


def test_a_fix_starts_with_the_problem_in_its_words(made: WorkPlace) -> None:
    """Given a command that the orchestrator keeps to mend, its content-1 made.
    When its next role is started with the problem's words on stdin.
    Then it gives the fixer, fix-2, and the code best practice, with problem.md holding them."""
    at(made, next="fixer")
    os.makedirs(os.path.join(rounds_of(made), "content-1"))
    folder = os.path.join(rounds_of(made), "fix-2")
    assert call(made, "start", rn_files.COMMAND, words="The total is off.") == (
        0,
        given(made, "fixer", *kept(made, "Fix", folder), ("Best practice", practice_of("code"))),
        "",
    )
    with open(os.path.join(folder, "problem.md"), encoding="utf-8") as f:
        assert f.read() == "The total is off.\n"


def test_a_refactoring_takes_its_kinds_refactor_best_practice(made: WorkPlace) -> None:
    """Given a command whose Rounds are good, its refactorer next.
    When its next role is started.
    Then it gives the refactorer, refactor-1, refactor-code, and the code best practice, whose
    template's form the refactoring keeps."""
    at(made, next="refactorer")
    folder = os.path.join(rounds_of(made), "refactor-1")
    assert call(made, "start", rn_files.COMMAND) == (
        0,
        given(
            made,
            "refactorer",
            *kept(made, "Round", folder),
            ("Refactor best practice", practice_of("refactor-code")),
            ("Kind's best practice", practice_of("code")),
        ),
        "",
    )


@pytest.mark.parametrize(
    ("fields", "path", "words", "says"),
    [
        ({}, "x.md", "", "no task has the path"),
        ({"next": "fixer"}, rn_files.COMMAND, " ", "the problem's words are empty"),
        ({"kind": "poster"}, rn_files.COMMAND, "", "no best practice of the kind 'poster'"),
        ({"next": "evaluator"}, rn_files.COMMAND, "", "no Round to judge"),
        ({"next": "weigh", "entry": "content-1"}, rn_files.COMMAND, "", "no result to weigh"),
    ],
    ids=["unnamed", "no-words", "no-practice", "no-round", "nothing-to-weigh"],
)
def test_a_start_that_can_not_be_is_refused(
    made: WorkPlace, fields: dict[str, Any], path: str, words: str, says: str
) -> None:
    """Given a command that no task names, mended with no words, of a kind rn has no best
    practice of, with its evaluator next and no Round made, or waiting on a weighing of a Round
    that holds no result.
    When its next role is started.
    Then it gives 1 saying why."""
    at(made, **fields)
    code, _, err = call(made, "start", path, words=words)
    assert (code, says in err) == (1, True)
