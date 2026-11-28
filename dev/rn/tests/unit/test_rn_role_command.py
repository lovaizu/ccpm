"""The unit cases of role/command.py, rn's hook once a role ends: an agent that isn't rn's left
alone, a role's result moving its task on with nothing committed, a task that ends completed
into the closed tasks, a session outside git, each
result out of its schema keeping the role going, a role that ends with no result kept going, work
in another worktree left alone, the work ended and the work of an earlier rn left alone, the
trials' folders removed, the inspector left alone, and arguments of another form."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from host import run
from place import WorkPlace
from repo_files import git, write_files
from role.command import USAGE, main

NAME = "20261126-invoice-from-statement"


@pytest.fixture
def made(tmp_path: Any) -> WorkPlace:
    """The work in the user's repository with origin, in its own worktree on the work's branch, its
    folder empty."""
    return rn_files.work_with_origin(str(tmp_path), NAME)


def top(work: WorkPlace) -> str:
    """The user's repository, beside the work's worktree."""
    return os.path.join(os.path.dirname(work.worktree), "accounting")


def ended(work: WorkPlace, agent: str, cwd: str = "") -> tuple[int, str, str]:
    """What the hook gives once the agent ends in the session's folder, the work's worktree, where
    rn runs, unless another is given."""
    given = json.dumps(
        {
            "session_id": "abc123",
            "cwd": cwd or work.worktree,
            "hook_event_name": "SubagentStop",
            "stop_hook_active": False,
            "agent_id": "a1",
            "agent_type": agent,
            "agent_transcript_path": "/t/a1.jsonl",
            "last_assistant_message": "done",
        }
    )
    return main(["ended"], given, rn_files.RN, run)


def test_an_agent_that_isnt_rns_is_left_alone(made: WorkPlace) -> None:
    """Given the work whose worktree holds a change.
    When an agent that isn't one of rn's ends.
    Then it gives 0, and commits nothing."""
    write_files(made.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, "Explore") == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_a_roles_result_moves_its_task_on_in_the_steering(made: WorkPlace) -> None:
    """Given a steering whose command works in 01-content, and the generator's result made there.
    When the generator ends.
    Then the steering has the command's evaluator next, not committed, as the orchestrator
    commits, and no task is closed."""
    value = rn_files.steering()
    value["tasks"][0]["entry"] = "01-content"
    rn_files.write_json(made.steering, value)
    folder = os.path.join(made.tasks, rn_files.COMMAND_ID, "01-content")
    rn_files.write_json(
        os.path.join(folder, "generator.json"), {"result": "made", "files": [rn_files.COMMAND]}
    )
    assert ended(made, "rn:generator") == (0, "", "")
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f)["tasks"][0]["next"] == "evaluator"
    assert git(made.worktree, "log", "--format=%s") == "accounting\n"
    assert not os.path.exists(made.closed)


def test_a_task_that_ends_is_completed_into_the_closed_tasks(made: WorkPlace) -> None:
    """Given a steering whose command, with no refactoring to take, waits on its evaluator in
    01-content, and the evaluator's result with nothing more to mend there.
    When the evaluator ends.
    Then the steering holds the guide alone, and closed.json holds the command, completed."""
    value = rn_files.steering()
    del value["tasks"][0]["refactor"]
    value["tasks"][0].update(next="evaluator", entry="01-content")
    rn_files.write_json(made.steering, value)
    folder = os.path.join(made.tasks, rn_files.COMMAND_ID, "01-content")
    rn_files.write_json(
        os.path.join(folder, "generator.json"), {"result": "made", "files": [rn_files.COMMAND]}
    )
    good = {"result": "evaluated", "good": [], "more": []}
    rn_files.write_json(os.path.join(folder, "evaluator.json"), good)
    assert ended(made, "rn:evaluator") == (0, "", "")
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f)["tasks"] == rn_files.tasks((rn_files.GUIDE_ID,))
    with open(made.closed, encoding="utf-8") as f:
        closed = json.load(f)["tasks"]
    assert [(each["id"], each["closed"], each["evaluated"]) for each in closed] == [
        (rn_files.COMMAND_ID, "completed", 1)
    ]


def test_nothing_is_committed_where_nothing_changed(made: WorkPlace) -> None:
    """Given the work whose steering is committed, and nothing changed since.
    When the evaluator ends.
    Then it gives 0, and commits nothing."""
    rn_files.committed_steering(made.worktree, made.name, rn_files.steering())
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, "rn:evaluator") == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_the_work_before_its_first_aim_keeps_nothing(made: WorkPlace) -> None:
    """Given the work with no steering yet, its folder holding a note of the hearing.
    When a role ends.
    Then it gives 0, and commits nothing, as the orchestrator's first aim makes the steering."""
    write_files(made.folder, {"hearing.md": "for the accountants\n"})
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, "rn:generator") == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_a_session_outside_git_is_left_alone(made: WorkPlace, tmp_path: Any) -> None:
    """Given a session whose folder lies in no git repository.
    When the fixer ends.
    Then it gives 0."""
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    assert ended(made, "rn:fixer", cwd=str(outside)) == (0, "", "")


@pytest.mark.parametrize(
    ("text", "says"),
    [
        ('{"result": "x"}', "generator-round.schema.json"),
        ("{", "the generator's result isn't JSON"),
    ],
    ids=["schema", "not-json"],
)
def test_a_result_out_of_its_schema_keeps_the_role_going(
    made: WorkPlace, text: str, says: str
) -> None:
    """Given the work whose Round's result leaves its schema or isn't JSON.
    When the role ends.
    Then it gives 2 naming the place, so that the role goes on, and commits nothing."""
    target = os.path.join(made.tasks, "001", "01-content", "generator.json")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = ended(made, "rn:generator")
    assert (code, says in err, err.startswith("role: ")) == (2, True, True)
    assert git(made.worktree, "rev-parse", "HEAD") == before


@pytest.mark.parametrize(("agent", "code"), [("rn:generator", 2), ("rn:evaluator", 0)])
def test_a_role_that_ends_with_no_result_keeps_going(
    made: WorkPlace, agent: str, code: int
) -> None:
    """Given a steering whose command's generator works in 01-content, which holds no result yet.
    When the generator ends, or another role.
    Then the generator's end gives 2 naming the result to write, so that it goes on, and the other
    role's gives 0, and the steering stays as it is."""
    value = rn_files.steering()
    value["tasks"][0]["entry"] = "01-content"
    rn_files.write_json(made.steering, value)
    os.makedirs(os.path.join(made.tasks, rn_files.COMMAND_ID, "01-content"))
    given, _, err = ended(made, agent)
    assert (given, "holds no generator.json" in err) == (code, code == 2)
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f) == value


def test_the_hook_leaves_work_in_another_worktree_alone(made: WorkPlace, tmp_path: Any) -> None:
    """Given the work with its steering, and other work in another worktree whose role is still
    writing its result.
    When the generator ends in the work's worktree.
    Then it gives 0, leaving the other's result unchecked."""
    rn_files.write_json(made.steering, rn_files.steering())
    other = WorkPlace(
        rn_files.worktree_of(top(made), str(tmp_path / "rules"), "rules"), "20261127-invoice-rules"
    )
    write_files(other.folder, {"tasks/001/01-content/generator.json": "{"})
    assert ended(made, "rn:generator") == (0, "", "")


def test_the_hook_leaves_the_work_ended_and_an_earlier_rns_alone(made: WorkPlace) -> None:
    """Given the work with its steering, and in the same `.rn/` a piece of work ended and one of an
    earlier rn, whose steering is in another form, each with a result out of its schema.
    When the generator ends.
    Then it gives 0, leaving both unchecked and their steering as it was."""
    rn_files.write_json(made.steering, rn_files.steering())
    done = WorkPlace(made.worktree, "20261125-print")
    rn_files.write_json(done.steering, rn_files.steering(ids=(), stage="inspected"))
    earlier = WorkPlace(made.worktree, "20261124-receipts")
    old = {"ost": {"target": "O1"}, "state": {"steps": []}}
    rn_files.write_json(earlier.steering, old)
    for each in (done, earlier):
        write_files(each.folder, {"tasks/001/01-content/generator.json": "{"})
    assert ended(made, "rn:generator") == (0, "", "")
    with open(earlier.steering, encoding="utf-8") as f:
        assert json.load(f) == old


def test_the_trials_of_the_work_are_removed_once_its_role_ends(made: WorkPlace, temp: str) -> None:
    """Given the work with its steering, and a trial's folder of it left in the temporary folder.
    When the evaluator ends.
    Then the trial's folder is gone."""
    rn_files.committed_steering(made.worktree, made.name, rn_files.steering())
    trials = os.path.join(temp, f"rn-trial-{made.name}")
    write_files(os.path.join(trials, "001-01-content"), {"README.md": "# Accounting\n"})
    assert ended(made, "rn:evaluator") == (0, "", "")
    assert not os.path.exists(trials)


def test_the_inspector_that_writes_no_result_is_left_alone(made: WorkPlace) -> None:
    """Given the work whose worktree holds a change.
    When the inspector ends.
    Then it gives 0, and commits nothing, as it writes no result to move the work on."""
    rn_files.write_json(made.steering, rn_files.steering())
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, "rn:inspector") == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_arguments_of_another_form_give_the_usage() -> None:
    """Given no subcommand.
    When role runs.
    Then it gives 2 with the usage."""
    assert main([], "{}", rn_files.RN, run) == (2, "", USAGE)
