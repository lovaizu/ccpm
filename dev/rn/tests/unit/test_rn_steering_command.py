"""The unit cases of steering/command.py, steering's command line as the orchestrator runs it: the
pruner's first result committed and pushed, a later one, each mark committed, the inspection's
pass committed, what's due read, and each
refusal: a result missing, not JSON, or out of its schema, a step's number that isn't one, a mark
that the steering refuses, git refusing the commit, and arguments of another form."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from typing import Any

import pytest
import rn_files
from gh import gh_double
from host import Ran, run
from place import RunPlace
from repo_files import git
from steering.command import USAGE, main

NAME = "20261126-invoice-from-statement"
FOLDER = f".rn/{NAME}"
STEP = rn_files.WAY


@pytest.fixture
def made(tmp_path: Any) -> RunPlace:
    """A run of the user's repository with origin, its worktree on the work's branch, its folder
    empty."""
    repo = rn_files.repository(str(tmp_path / "accounting"))
    rn_files.with_origin(repo, str(tmp_path / "origin.git"))
    held = RunPlace(repo, NAME)
    git(repo, "worktree", "add", "-q", "-b", held.branch, held.worktree)
    os.makedirs(held.folder)
    return held


def steering(run_: RunPlace, value: Any) -> None:
    """Writes the steering, and commits it on the work's branch."""
    rn_files.write_json(run_.steering, value)
    git(run_.worktree, "add", "-A")
    git(run_.worktree, "commit", "-q", "-m", "steering")


def call(run_: RunPlace, *argv: str, host: Any = None) -> tuple[int, str, str]:
    """What `steering` gives with the arguments on the run, with git run for real and gh from its
    records, unless another host is given."""
    gh = host or gh_double.host(os.path.join(os.path.dirname(run_.repository), "gh"))
    return main(argv[:1] + (FOLDER,) + argv[1:], run_.worktree, rn_files.RN, gh)


def held(run_: RunPlace) -> Any:
    with open(run_.steering, encoding="utf-8") as f:
        return json.load(f)


def test_the_pruners_first_result_is_committed_as_the_steering(made: RunPlace) -> None:
    """Given a run with no steering, and the pruner's result with the pick still asked.
    When `steering commit` runs.
    Then the steering holds the result's tree, is committed alone as `rn: <message>`, the result
    is gone, and the hash and the question are printed."""
    rn_files.write_json(
        made.pruner,
        {
            "message": "the needs, with the pick asked",
            "ost": rn_files.ost(target=None, questions=["Which need first?"]),
        },
    )
    code, out, err = call(made, "commit")
    assert (code, err) == (0, "")
    assert out == f"{git(made.worktree, 'rev-parse', 'HEAD')}question\tWhich need first?\n"
    assert git(made.worktree, "log", "-1", "--format=%s") == "rn: the needs, with the pick asked\n"
    assert git(made.worktree, "show", "--name-only", "--format=") == f"{FOLDER}/steering.json\n"
    assert not os.path.exists(made.pruner)
    assert held(made)["ost"]["questions"] == ["Which need first?"]


def test_a_later_result_takes_in_the_steps_and_keeps_the_issues(made: RunPlace) -> None:
    """Given a steering with its issues and no step, and a result with the pick and the steps.
    When `steering commit` runs.
    Then the steering holds the steps open and the issues kept, and the first deliverable is due."""
    steering(made, rn_files.steering([]))
    rn_files.write_json(
        made.pruner, {"message": "the user picked printing", "ost": rn_files.ost(), "steps": [STEP]}
    )
    code, out, _ = call(made, "commit")
    assert (code, out.split("\n")[1]) == (0, f"make\t1\t{rn_files.COMMAND}\tcode")
    assert held(made) == rn_files.steering()


@pytest.mark.parametrize(
    ("text", "says"),
    [
        (None, "no the pruner's result lies there"),
        ("{", "isn't JSON"),
        (json.dumps({"ost": {}}), "leaves its schema, pruner.schema.json: /message: is required"),
    ],
)
def test_a_result_missing_not_json_or_out_of_its_schema_is_refused(
    made: RunPlace, text: str | None, says: str
) -> None:
    """Given a run whose pruner's result is missing, isn't JSON, or lacks its message.
    When `steering commit` runs.
    Then it gives 1 saying what's wrong, and writes and commits nothing."""
    if text is not None:
        with open(made.pruner, "w", encoding="utf-8") as f:
            f.write(text)
    code, out, err = call(made, "commit")
    assert (code, out, says in err, os.path.exists(made.steering)) == (1, "", True, False)


def test_each_mark_is_committed_and_gives_whats_due(made: RunPlace) -> None:
    """Given a steering whose step is open.
    When the command and the guide are marked done, then step 1 trying.
    Then each is committed with its words, and what's due follows each."""
    steering(made, rn_files.steering())
    assert call(made, "deliverable", rn_files.COMMAND, "done") == (
        0,
        f"make\t1\t{rn_files.GUIDE}\treadme\n",
        "",
    )
    assert call(made, "deliverable", rn_files.GUIDE, "done") == (
        0,
        f"hand-over\t1\t{rn_files.SETTLES}\n",
        "",
    )
    assert call(made, "step", "1", "trying") == (0, f"trying\t1\t{rn_files.SETTLES}\n", "")
    assert git(made.worktree, "log", "-3", "--format=%s").split("\n")[:3] == [
        f"rn: {rn_files.SETTLES}: trying",
        f"rn: {rn_files.GUIDE}: done",
        f"rn: {rn_files.COMMAND}: done",
    ]


def test_the_final_checks_pass_is_committed_and_gives_the_runs_end(made: RunPlace) -> None:
    """Given a steering whose one step is done.
    When the inspection is marked passed.
    Then it's committed with its words, and the run's end is due."""
    steering(made, rn_files.steering([rn_files.step("done")]))
    assert call(made, "inspected") == (0, "ended\n", "")
    assert git(made.worktree, "log", "-1", "--format=%s") == "rn: the inspection passed\n"
    assert held(made)["state"]["inspected"] is True


def test_whats_due_is_read_from_the_steering(made: RunPlace) -> None:
    """Given the walkthrough's steering.
    When `steering due` runs.
    Then the command is due to make."""
    steering(made, rn_files.steering())
    assert call(made, "due") == (0, f"make\t1\t{rn_files.COMMAND}\tcode\n", "")


def test_a_steering_out_of_its_schema_is_refused(made: RunPlace) -> None:
    """Given a steering with no state.
    When `steering due` runs.
    Then it gives 1 naming the place."""
    value = rn_files.steering()
    del value["state"]
    steering(made, value)
    code, _, err = call(made, "due")
    assert (code, "/state: is required" in err) == (1, True)


@pytest.mark.parametrize(
    ("argv", "says"),
    [
        (("step", "one", "done"), "isn't a step's number"),
        (("step", "1", "trying"), "isn't made yet"),
    ],
)
def test_a_mark_that_can_not_be_is_refused_and_commits_nothing(
    made: RunPlace, argv: Sequence[str], says: str
) -> None:
    """Given the walkthrough's steering, its step not made.
    When a step is marked by a word in place of its number, or trying.
    Then it gives 1 saying why, and commits nothing."""
    steering(made, rn_files.steering())
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = call(made, *argv)
    assert (code, says in err, git(made.worktree, "rev-parse", "HEAD")) == (1, True, before)


def test_git_refusing_the_commit_cant_run(made: RunPlace) -> None:
    """Given the walkthrough's steering, and git that refuses each commit.
    When a deliverable is marked done.
    Then it gives 2 with what git said."""
    steering(made, rn_files.steering())

    def refusing(argv: Sequence[str], cwd: str, env: Mapping[str, str] | None = None) -> Ran:
        return Ran(1, "", "hook refused\n") if argv[1] == "commit" else run(argv, cwd, env)

    assert call(made, "deliverable", rn_files.COMMAND, "done", host=refusing) == (
        2,
        "",
        "steering: git commit fails: hook refused\n",
    )


@pytest.mark.parametrize("argv", [(), ("push", FOLDER), ("due",), ("step", FOLDER, "1")])
def test_arguments_of_another_form_give_the_usage(argv: Sequence[str]) -> None:
    """Given no subcommand, one that isn't steering's, or too few arguments.
    When steering runs.
    Then it gives 2 with the usage."""
    assert main(argv, "/", rn_files.RN, run) == (2, "", USAGE)
