"""The unit cases of steering/command.py, steering's command line as the orchestrator runs it: each
aim taken in, a task it leaves out canceled into closed.json, each mark of the stage, each written
to the steering alone, what's due read, each start of a task's next role by its id with what it's
given, the records of another version of rn brought into this one, and each refusal: a steering
missing or out of its schema, an aim that isn't JSON, leaves its schema, or that the steering
refuses, a mark that the steering refuses, a hand-over or an end with a TODO left, a start that
can't be, records of another version out of this rn's form, and arguments of another form."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from typing import Any

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
    Then the steering holds it, each task with its id, not committed, as the orchestrator
    commits, the command is due to make by its id, and no task is closed."""
    before = git(made.worktree, "rev-parse", "HEAD")
    assert call(made, "aim", words=json.dumps(rn_files.aim())) == (
        0,
        f"make\t{rn_files.COMMAND_ID}\tcode\tgenerator\n",
        "",
    )
    assert git(made.worktree, "rev-parse", "HEAD") == before
    assert (held(made), os.path.exists(made.closed)) == (rn_files.steering(), False)


def test_a_later_aim_keeps_the_stage(made: WorkPlace) -> None:
    """Given a steering in the user's hands with no task left, and an aim with a task to mend.
    When it's given to `steering aim`.
    Then the steering holds the task with the first id, and keeps the stage, so the try waits once
    it's mended."""
    steering(made, rn_files.steering(ids=(), stage="trying"))
    code, _, _ = call(made, "aim", words=json.dumps(rn_files.aim(rn_files.TASKS[:1])))
    assert (code, held(made)) == (0, rn_files.steering((rn_files.COMMAND_ID,), stage="trying"))


def test_a_task_the_aim_leaves_out_is_canceled_into_the_closed_tasks(made: WorkPlace) -> None:
    """Given a steering holding the command and the guide, and closed.json holding a task 003.
    When an aim that keeps the guide alone and adds a task is given to `steering aim`.
    Then the steering holds the guide and the new task 004, and closed.json holds 003, then the
    command, canceled."""
    steering(made, rn_files.steering())
    earlier = {**rn_files.tasks()[1], "id": "003", "closed": "completed"}
    rn_files.write_json(made.closed, {"tasks": [earlier]})
    aim = rn_files.aim([*rn_files.tasks((rn_files.GUIDE_ID,)), {"task": "Print.", "kind": "code"}])
    code, _, _ = call(made, "aim", words=json.dumps(aim))
    assert [each["id"] for each in held(made)["tasks"]] == [rn_files.GUIDE_ID, "004"]
    with open(made.closed, encoding="utf-8") as f:
        closed = json.load(f)["tasks"]
    assert (code, closed) == (0, [earlier, {**rn_files.tasks()[0], "closed": "canceled"}])


@pytest.mark.parametrize(
    ("words", "says"),
    [
        ("{", "the aim isn't JSON"),
        (json.dumps({}), "aim.schema.json: /ost: is required"),
        (json.dumps(rn_files.aim([{**rn_files.tasks()[0], "next": "generator"}])), "has had its 2"),
        (json.dumps(rn_files.aim([{**rn_files.TASKS[0], "id": "009"}])), "no task left has the id"),
    ],
    ids=["not-json", "schema", "refused", "no-id"],
)
def test_an_aim_that_can_not_be_taken_in_is_refused_and_changes_nothing(
    made: WorkPlace, words: str, says: str
) -> None:
    """Given a steering whose command has had its evaluated Rounds, and an aim that isn't JSON,
    leaves its schema, makes the command again, or names an id that no task left has.
    When it's given to `steering aim`.
    Then it gives 1 saying why, and changes nothing."""
    at(made, next="weigh", entry="02-content", evaluated=2)
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
    steering(made, rn_files.steering(ids=()))
    assert call(made, "mark", stage) == (0, line, "")
    assert held(made)["stage"] == stage


@pytest.mark.parametrize("stage", ["trying", "inspected"])
def test_a_hand_over_or_an_end_with_a_todo_left_is_refused(made: WorkPlace, stage: str) -> None:
    """Given a steering with no task left, and the work's guide still holding a TODO.
    When the work is marked trying, or inspected.
    Then it gives 1 naming the TODO's place, and changes nothing, as what it marks is still to
    make."""
    write_files(made.worktree, {rn_files.GUIDE: "# Guide\n\nTODO: the rules.\n"})
    steering(made, rn_files.steering(ids=()))
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
    assert call(made, "due") == (0, f"make\t{rn_files.COMMAND_ID}\tcode\tgenerator\n", "")


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


def rounds_of(work: WorkPlace) -> str:
    """The folder of the command's task's Rounds and Fixes."""
    return os.path.join(work.tasks, rn_files.COMMAND_ID)


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
    lines = [("Worktree", made.worktree), ("Task", rn_files.TASKS[0]["task"]), *things]
    return role + "\n" + "".join(f"{name}: {value}\n" for name, value in lines)


def kept(made: WorkPlace, place: str, folder: str) -> list[tuple[str, str]]:
    """What each role but the evaluator is given beside the worktree and the task."""
    return [("Steering", made.steering), ("Kind", "code"), (place, folder)]


def test_a_round_of_content_starts_in_a_new_folder_and_again_in_the_same(made: WorkPlace) -> None:
    """Given the walkthrough's steering, its command not started.
    When its next role is started, twice, as a stop left the first with no result.
    Then each gives its generator, 01-content, and the code best practice, and the steering holds
    01-content as its entry."""
    at(made)
    folder = os.path.join(rounds_of(made), "01-content")
    want = (
        0,
        given(
            made, "generator", *kept(made, "Round", folder), ("Best practice", practice_of("code"))
        ),
        "",
    )
    assert (call(made, "start", rn_files.COMMAND_ID), call(made, "start", rn_files.COMMAND_ID)) == (
        want,
        want,
    )
    assert (os.path.isdir(folder), command_of(made)["entry"]) == (True, "01-content")


def test_a_round_made_again_starts_past_the_last(made: WorkPlace) -> None:
    """Given a command whose 01-content and 02-fix are made, and that the orchestrator has made
    again.
    When its next role is started.
    Then it's 03-content."""
    at(made, next="generator", evaluated=1)
    rn_files.write_json(os.path.join(rounds_of(made), "01-content", "generator.json"), MADE)
    os.makedirs(os.path.join(rounds_of(made), "02-fix"))
    code, out, _ = call(made, "start", rn_files.COMMAND_ID)
    assert (code, f"Round: {os.path.join(rounds_of(made), '03-content')}" in out) == (0, True)


def test_the_evaluator_judges_its_round_by_the_conditions_alone(made: WorkPlace) -> None:
    """Given a command whose 01-content is made, its evaluator next.
    When its next role is started.
    Then it gives the evaluator, the work, 01-content, and judges-by.json there, holding the
    conditions, the outcome, and the target solution with its assumptions."""
    at(made, next="evaluator", entry="01-content")
    folder = os.path.join(rounds_of(made), "01-content")
    os.makedirs(folder)
    judges = os.path.join(folder, "judges-by.json")
    want = given(made, "evaluator", ("Round", folder), ("Judges by", judges))
    want = want.replace("evaluator\n", f"evaluator\nWork: {made.folder}\n", 1)
    assert call(made, "start", rn_files.COMMAND_ID) == (0, want, "")
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
    """Given a command waiting on the orchestrator's weighing of 01-content, which holds an
    evaluator's findings, or a generator's or a fixer's point alone.
    When its next role is started.
    Then it gives the weighing, with the result to weigh, and changes nothing."""
    at(made, next="weigh", entry="01-content")
    folder = os.path.join(rounds_of(made), "01-content")
    for role in results:
        rn_files.write_json(os.path.join(folder, f"{role}.json"), {"result": "x"})
    before = held(made)
    assert call(made, "start", rn_files.COMMAND_ID) == (
        0,
        f"weigh\t{os.path.join(folder, weighed + '.json')}\n",
        "",
    )
    assert held(made) == before


def test_a_fix_starts_with_the_problem_in_its_words(made: WorkPlace) -> None:
    """Given a command that the orchestrator keeps to mend, its 01-content made.
    When its next role is started with the problem's words on stdin.
    Then it gives the fixer, 02-fix, and the code best practice, with problem.md holding them."""
    at(made, next="fixer")
    os.makedirs(os.path.join(rounds_of(made), "01-content"))
    folder = os.path.join(rounds_of(made), "02-fix")
    assert call(made, "start", rn_files.COMMAND_ID, words="The total is off.") == (
        0,
        given(made, "fixer", *kept(made, "Fix", folder), ("Best practice", practice_of("code"))),
        "",
    )
    with open(os.path.join(folder, "problem.md"), encoding="utf-8") as f:
        assert f.read() == "The total is off.\n"


def test_a_refactoring_takes_its_kinds_refactor_best_practice(made: WorkPlace) -> None:
    """Given a command whose Rounds are good, its refactorer next.
    When its next role is started.
    Then it gives the refactorer, 01-refactor, refactor-code, and the code best practice, whose
    template's form the refactoring keeps."""
    at(made, next="refactorer")
    folder = os.path.join(rounds_of(made), "01-refactor")
    assert call(made, "start", rn_files.COMMAND_ID) == (
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
    ("fields", "task", "words", "says"),
    [
        ({}, "009", "", "no task has the id"),
        ({"next": "fixer"}, rn_files.COMMAND_ID, " ", "the problem's words are empty"),
        ({"kind": "poster"}, rn_files.COMMAND_ID, "", "no best practice of the kind 'poster'"),
        ({"next": "evaluator"}, rn_files.COMMAND_ID, "", "no Round to evaluate"),
        ({"next": "weigh", "entry": "01-content"}, rn_files.COMMAND_ID, "", "no result to weigh"),
    ],
    ids=["unnamed", "no-words", "no-practice", "no-round", "nothing-to-weigh"],
)
def test_a_start_that_can_not_be_is_refused(
    made: WorkPlace, fields: dict[str, Any], task: str, words: str, says: str
) -> None:
    """Given an id that no task has, mended with no words, of a kind rn has no best
    practice of, with its evaluator next and no Round made, or waiting on a weighing of a Round
    that holds no result.
    When its next role is started.
    Then it gives 1 saying why."""
    at(made, **fields)
    code, _, err = call(made, "start", task, words=words)
    assert (code, says in err) == (1, True)


def test_a_steering_of_another_version_in_this_rns_form_is_marked_with_this_one(
    made: WorkPlace,
) -> None:
    """Given a steering that an rn before 0.13.0 wrote, naming no version, in this rn's form.
    When `steering due` runs.
    Then the steering names this rn's version, and the command is due to make."""
    value = rn_files.steering()
    del value["rn"]
    steering(made, value)
    assert call(made, "due") == (0, f"make\t{rn_files.COMMAND_ID}\tcode\tgenerator\n", "")
    assert held(made) == rn_files.steering()


def test_records_of_another_version_out_of_this_rns_form_are_named(made: WorkPlace) -> None:
    """Given a steering of another version, and a Fix whose result an earlier fixer wrote.
    When `steering due` runs.
    Then it gives 1 naming the version and each record to bring into this rn's form, and
    changes nothing."""
    steering(made, {**rn_files.steering(), "rn": "0.0.1"})
    folder = os.path.join(rounds_of(made), "01-fix")
    rn_files.write_json(os.path.join(folder, "fixer.json"), {"result": "fixed", "files": []})
    git(made.worktree, "add", "-A")
    git(made.worktree, "commit", "-q", "-m", "fix")
    code, _, err = call(made, "due")
    assert (code, "written by rn 0.0.1" in err, "fixer.json" in err) == (1, True, True)
    assert unchanged(made)


def test_a_steering_of_another_version_that_is_not_json_is_refused(made: WorkPlace) -> None:
    """Given a steering that isn't JSON.
    When `steering due` runs.
    Then it gives 1 naming its path."""
    os.makedirs(made.folder, exist_ok=True)
    with open(made.steering, "w", encoding="utf-8") as f:
        f.write("{")
    code, _, err = call(made, "due")
    assert (code, "steering.json: isn't JSON" in err) == (1, True)


def test_closed_tasks_of_another_version_out_of_this_rns_form_are_named(made: WorkPlace) -> None:
    """Given a steering of another version, and closed.json whose task has no id.
    When `steering due` runs.
    Then it gives 1 naming closed.json, and changes nothing."""
    steering(made, {**rn_files.steering(), "rn": "0.0.1"})
    rn_files.write_json(made.closed, {"tasks": [{**rn_files.TASKS[0], "closed": "completed"}]})
    git(made.worktree, "add", "-A")
    git(made.worktree, "commit", "-q", "-m", "closed")
    code, _, err = call(made, "due")
    assert (code, "closed.json" in err, unchanged(made)) == (1, True, True)
