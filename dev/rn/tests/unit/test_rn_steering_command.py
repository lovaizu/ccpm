"""The unit cases of steering/command.py, steering's command line as the orchestrator runs it: each
aim taken in, committed, and pushed, each mark committed and pushed, the inspection's pass
committed, what's due read, each start of a deliverable's next role with what it's given, and each
refusal: a steering missing or out of its schema, an aim that isn't JSON, leaves its schema, or that
the steering refuses, a step's number that isn't one, a mark that the steering refuses, a start that
can't be, git refusing the commit, and arguments of another form."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import quote

import pytest
import rn_files
from gh import gh_double
from host import Ran, run
from place import WorkPlace
from repo_files import git
from steering.command import USAGE, main

NAME = "20261126-invoice-from-statement"
FOLDER = f".rn/{NAME}"
STEP = rn_files.WAY
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


def call(work: WorkPlace, *argv: str, host: Any = None, words: str = "") -> tuple[int, str, str]:
    """What `steering` gives with the arguments on the work, with git run for real and gh from its
    records, unless another host is given, and the words given on stdin."""
    gh = host or gh_double.host(os.path.join(os.path.dirname(work.worktree), "gh"))
    given = argv[:1] + (FOLDER,) + argv[1:]
    return main(given, work.worktree, rn_files.RN, gh, lambda: words)


def held(work: WorkPlace) -> Any:
    with open(work.steering, encoding="utf-8") as f:
        return json.load(f)


def test_the_first_aim_makes_the_steering_and_is_pushed(made: WorkPlace) -> None:
    """Given the work with no steering, and an aim with the pick still asked.
    When it's given to `steering aim`.
    Then the steering holds its tree and its question, committed as `rn: <message>` and pushed,
    and the question is due."""
    aim = {
        "message": "the needs, with the pick asked",
        "ost": rn_files.ost(target=None, questions=["Which need first?"]),
    }
    assert call(made, "aim", words=json.dumps(aim)) == (0, "question\tWhich need first?\n", "")
    assert git(made.worktree, "log", "-1", "--format=%s") == "rn: the needs, with the pick asked\n"
    origin = os.path.join(os.path.dirname(made.worktree), "origin.git")
    assert git(origin, "rev-parse", "invoices") == git(made.worktree, "rev-parse", "HEAD")
    assert held(made)["ost"]["questions"] == ["Which need first?"]


def test_a_later_aim_takes_in_the_steps_and_keeps_the_issues(made: WorkPlace) -> None:
    """Given a steering with its issues and no step, and an aim with the target and the steps.
    When it's given to `steering aim`.
    Then the steering holds the steps open and the issues kept, and the command is due to make."""
    steering(made, rn_files.steering([]))
    aim = {"message": "printing first", "ost": rn_files.ost(), "steps": [rn_files.WAY]}
    assert call(made, "aim", words=json.dumps(aim)) == (
        0,
        f"make\t1\t{rn_files.COMMAND}\tcode\tgenerator\n",
        "",
    )
    assert held(made) == rn_files.steering()


@pytest.mark.parametrize(
    ("words", "says"),
    [
        ("{", "the aim isn't JSON"),
        (json.dumps({"ost": {}}), "aim.schema.json: /message: is required"),
        (
            json.dumps({"message": "m", "ost": rn_files.ost(), "steps": [rn_files.WAY]}),
            rn_files.COMMAND,
        ),
    ],
    ids=["not-json", "schema", "refused"],
)
def test_an_aim_that_can_not_be_taken_in_is_refused_and_commits_nothing(
    made: WorkPlace, words: str, says: str
) -> None:
    """Given a steering whose command waits on a weighing, and an aim that isn't JSON, leaves its
    schema, or neither says what the command takes next nor asks the user.
    When it's given to `steering aim`.
    Then it gives 1 saying why, and commits nothing."""
    at(made, next="weigh", entry="content-1")
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = call(made, "aim", words=words)
    assert (code, says in err, git(made.worktree, "rev-parse", "HEAD")) == (1, True, before)


def test_each_mark_is_committed_and_gives_whats_due(made: WorkPlace) -> None:
    """Given a steering whose step has each deliverable done.
    When step 1 is marked trying.
    Then it's committed with its words, and the user's try is due."""
    steering(made, rn_files.steering([rn_files.step(done=(rn_files.COMMAND, rn_files.GUIDE))]))
    assert call(made, "step", "1", "trying") == (0, f"trying\t1\t{rn_files.SETTLES}\n", "")
    assert git(made.worktree, "log", "-1", "--format=%s") == f"rn: {rn_files.SETTLES}: trying\n"


def test_the_final_checks_pass_is_committed_and_ends_the_work(made: WorkPlace) -> None:
    """Given a steering whose one step is done.
    When the inspection is marked passed.
    Then it's committed with its words, and the work's end is due."""
    steering(made, rn_files.steering([rn_files.step("done")]))
    assert call(made, "inspected") == (0, "ended\n", "")
    assert git(made.worktree, "log", "-1", "--format=%s") == "rn: the inspection passed\n"
    assert held(made)["state"]["inspected"] is True


def test_whats_due_is_read_from_the_steering(made: WorkPlace) -> None:
    """Given the walkthrough's steering.
    When `steering due` runs.
    Then the command is due to make."""
    steering(made, rn_files.steering())
    assert call(made, "due") == (0, f"make\t1\t{rn_files.COMMAND}\tcode\tgenerator\n", "")


def test_a_steering_out_of_its_schema_is_refused(made: WorkPlace) -> None:
    """Given a steering with no state.
    When `steering due` runs.
    Then it gives 1 naming the place."""
    value = rn_files.steering()
    del value["state"]
    steering(made, value)
    code, _, err = call(made, "due")
    assert (code, "/state: is required" in err) == (1, True)


def test_a_mark_on_the_work_with_no_steering_is_refused(made: WorkPlace) -> None:
    """Given the work with no steering yet.
    When a step is marked done.
    Then it gives 1 saying that no steering lies there."""
    code, _, err = call(made, "step", "1", "done")
    assert (code, "no the steering lies there" in err) == (1, True)


@pytest.mark.parametrize(
    ("argv", "says"),
    [
        (("step", "one", "done"), "isn't a step's number"),
        (("step", "1", "trying"), "isn't made yet"),
    ],
)
def test_a_mark_that_can_not_be_is_refused_and_commits_nothing(
    made: WorkPlace, argv: Sequence[str], says: str
) -> None:
    """Given the walkthrough's steering, its step not made.
    When a step is marked by a word in place of its number, or trying.
    Then it gives 1 saying why, and commits nothing."""
    steering(made, rn_files.steering())
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = call(made, *argv)
    assert (code, says in err, git(made.worktree, "rev-parse", "HEAD")) == (1, True, before)


def test_git_refusing_the_commit_cant_run(made: WorkPlace) -> None:
    """Given the walkthrough's steering, and git that refuses each commit.
    When step 1 is marked done.
    Then it gives 2 with what git said."""
    steering(made, rn_files.steering())

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return Ran(1, "", "hook refused\n") if argv[1] == "commit" else run(argv, cwd, env)

    assert call(made, "step", "1", "done", host=refusing) == (
        2,
        "",
        "steering: git commit fails: hook refused\n",
    )


@pytest.mark.parametrize("argv", [(), ("push", FOLDER), ("due",), ("aim",), ("step", FOLDER, "1")])
def test_arguments_of_another_form_give_the_usage(argv: Sequence[str]) -> None:
    """Given no subcommand, one that isn't steering's, or too few arguments.
    When steering runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN, run, str) == (2, "", USAGE)


def rounds_of(work: WorkPlace, path: str = rn_files.COMMAND) -> str:
    """The folder of the deliverable's Rounds and Fixes in step 1."""
    return os.path.join(work.rounds, "1", quote(path, safe=""))


def at(work: WorkPlace, **fields: Any) -> None:
    """Writes the walkthrough's steering, its command with the fields given."""
    value = rn_files.steering()
    value["state"]["steps"][0]["deliverables"][0].update(fields)
    steering(work, value)


def command_of(work: WorkPlace) -> Any:
    return held(work)["state"]["steps"][0]["deliverables"][0]


def practice_of(kind: str) -> str:
    return os.path.join(rn_files.PRACTICES, kind)


def test_a_round_of_content_starts_in_a_new_folder_and_again_in_the_same(made: WorkPlace) -> None:
    """Given the walkthrough's steering, its command not started.
    When its next role is started, twice, as a stop left the first with no result.
    Then each gives its generator, content-1, and the code best practice, and the steering holds
    content-1 as its entry."""
    at(made)
    folder = os.path.join(rounds_of(made), "content-1")
    want = (0, f"generator\t{folder}\t{practice_of('code')}\n", "")
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
    assert (code, out.split("\t")[1]) == (0, os.path.join(rounds_of(made), "content-3"))


def test_the_evaluator_judges_its_round_by_the_conditions_alone(made: WorkPlace) -> None:
    """Given a command whose content-1 is made, its evaluator next.
    When its next role is started.
    Then it gives the evaluator, content-1, and judges-by.json there, holding the conditions."""
    at(made, next="evaluator", entry="content-1")
    folder = os.path.join(rounds_of(made), "content-1")
    os.makedirs(folder)
    judges = os.path.join(folder, "judges-by.json")
    assert call(made, "start", rn_files.COMMAND) == (0, f"evaluator\t{folder}\t{judges}\n", "")
    with open(judges, encoding="utf-8") as f:
        assert json.load(f) == rn_files.judged_by("code")


@pytest.mark.parametrize(
    ("results", "weighed"),
    [(("generator", "evaluator"), "evaluator"), (("generator",), "generator")],
    ids=["findings", "point"],
)
def test_a_weighing_takes_the_result_to_weigh(
    made: WorkPlace, results: Sequence[str], weighed: str
) -> None:
    """Given a command waiting on the orchestrator's weighing of content-1, which holds an
    evaluator's findings, or a generator's point alone.
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
        f"fixer\t{folder}\t{practice_of('code')}\n",
        "",
    )
    with open(os.path.join(folder, "problem.md"), encoding="utf-8") as f:
        assert f.read() == "The total is off.\n"


def test_a_refactoring_takes_its_kinds_refactor_best_practice(made: WorkPlace) -> None:
    """Given a command whose Rounds are good, its refactorer next.
    When its next role is started.
    Then it gives the refactorer, refactor-1, and refactor-code."""
    at(made, next="refactorer")
    folder = os.path.join(rounds_of(made), "refactor-1")
    assert call(made, "start", rn_files.COMMAND) == (
        0,
        f"refactorer\t{folder}\t{practice_of('refactor-code')}\n",
        "",
    )


@pytest.mark.parametrize(
    ("fields", "path", "words", "says"),
    [
        ({}, "x.md", "", "no open deliverable"),
        ({"status": "done"}, rn_files.COMMAND, "", "no open deliverable"),
        ({"next": "fixer"}, rn_files.COMMAND, " ", "the problem's words are empty"),
        ({"kind": "poster"}, rn_files.COMMAND, "", "no best practice of the kind 'poster'"),
        ({"next": "evaluator"}, rn_files.COMMAND, "", "no Round to judge"),
        ({"next": "weigh", "entry": "content-1"}, rn_files.COMMAND, "", "no result to weigh"),
    ],
    ids=["unnamed", "done", "no-words", "no-practice", "no-round", "nothing-to-weigh"],
)
def test_a_start_that_can_not_be_is_refused(
    made: WorkPlace, fields: dict[str, Any], path: str, words: str, says: str
) -> None:
    """Given a command that no step names, done, mended with no words, of a kind rn has no best
    practice of, with its evaluator next and no Round made, or waiting on a weighing of a Round
    that holds no result.
    When its next role is started.
    Then it gives 1 saying why."""
    at(made, **fields)
    code, _, err = call(made, "start", path, words=words)
    assert (code, says in err) == (1, True)
