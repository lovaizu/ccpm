"""The unit cases of role/command.py, rn's hook once a role ends: an agent that isn't rn's left
alone, the pruner's first result taken into the steering, committed, and pushed, a later one
keeping the issues, a role's change committed and pushed, nothing committed where nothing
changed, a folder outside rn's work passed over, a session outside git, each result out of its
schema keeping the role going, a push with no origin or to a remote that isn't there, and
arguments of another form."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from gh import gh_double
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


def ended(work: WorkPlace, agent: str, cwd: str = "", host: Any = None) -> tuple[int, str, str]:
    """What the hook gives once the agent ends in the session's folder, the repository's top
    unless another is given."""
    given = json.dumps(
        {
            "session_id": "abc123",
            "cwd": cwd or top(work),
            "hook_event_name": "SubagentStop",
            "stop_hook_active": False,
            "agent_id": "a1",
            "agent_type": agent,
            "agent_transcript_path": "/t/a1.jsonl",
            "last_assistant_message": "done",
        }
    )
    gh = host or gh_double.host(os.path.join(os.path.dirname(top(work)), "gh"))
    return main(["ended"], given, rn_files.RN, gh)


def subject(work: WorkPlace) -> str:
    return git(work.worktree, "log", "-1", "--format=%s").strip()


def pushed(work: WorkPlace) -> bool:
    origin = os.path.join(os.path.dirname(top(work)), "origin.git")
    remote = git(origin, "rev-parse", "invoices").strip()
    return remote == git(work.worktree, "rev-parse", "HEAD").strip()


def test_an_agent_that_isnt_rns_is_left_alone(made: WorkPlace) -> None:
    """Given the work whose worktree holds a change.
    When an agent that isn't one of rn's ends.
    Then it gives 0, and commits nothing."""
    write_files(made.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, "Explore") == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_the_pruners_first_result_is_taken_into_the_steering_and_pushed(made: WorkPlace) -> None:
    """Given the work with no steering, and the pruner's result with the pick still asked.
    When the pruner ends.
    Then the steering holds the result's tree and its question, committed as `rn: <message>` and
    pushed, and the result is gone."""
    rn_files.write_json(
        made.pruner,
        {
            "message": "the needs, with the pick asked",
            "ost": rn_files.ost(target=None, questions=["Which need first?"]),
        },
    )
    assert ended(made, "rn:pruner") == (0, "", "")
    assert subject(made) == "rn: the needs, with the pick asked"
    assert pushed(made) and not os.path.exists(made.pruner)
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f)["ost"]["questions"] == ["Which need first?"]


def test_a_later_result_takes_in_the_steps_and_keeps_the_issues(made: WorkPlace) -> None:
    """Given a steering with its issues and no step, and a result with the pick and the steps.
    When the pruner ends.
    Then the steering holds the steps open and the issues kept."""
    rn_files.write_json(made.steering, rn_files.steering([]))
    rn_files.write_json(
        made.pruner,
        {"message": "the user picked printing", "ost": rn_files.ost(), "steps": [rn_files.WAY]},
    )
    assert ended(made, "pruner")[0] == 0
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f) == rn_files.steering()


def test_a_roles_change_is_committed_and_pushed_from_inside_the_worktree_of_the_work(
    made: WorkPlace,
) -> None:
    """Given the work with its steering, whose generator wrote the command, and a session in the
    work's worktree.
    When the generator ends.
    Then the change is committed as `rn: the generator ended`, and pushed."""
    rn_files.write_json(made.steering, rn_files.steering())
    write_files(made.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    assert ended(made, "rn:generator", cwd=made.worktree) == (0, "", "")
    assert subject(made) == "rn: the generator ended"
    assert pushed(made)


def test_a_roles_result_moves_its_deliverable_on_in_the_steering(made: WorkPlace) -> None:
    """Given a steering whose command works in content-1, and the generator's result made there.
    When the generator ends.
    Then the steering has the command's evaluator next, committed and pushed."""
    value = rn_files.steering()
    value["state"]["steps"][0]["deliverables"][0]["entry"] = "content-1"
    rn_files.write_json(made.steering, value)
    folder = os.path.join(made.rounds, "1", "invoice%2F__main__.py", "content-1")
    rn_files.write_json(
        os.path.join(folder, "generator.json"), {"result": "made", "files": [rn_files.COMMAND]}
    )
    assert ended(made, "rn:generator") == (0, "", "")
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f)["state"]["steps"][0]["deliverables"][0]["next"] == "evaluator"
    assert pushed(made)


def test_a_pruners_result_the_steering_refuses_keeps_it_going(made: WorkPlace) -> None:
    """Given a steering whose command waits on a weighing, and a pruner's result that neither says
    what it takes next nor asks the user.
    When the pruner ends.
    Then it gives 2 naming the command, and commits nothing."""
    value = rn_files.steering()
    value["state"]["steps"][0]["deliverables"][0].update(next="weigh", entry="content-1")
    rn_files.write_json(made.steering, value)
    rn_files.write_json(
        made.pruner, {"message": "m", "ost": rn_files.ost(), "steps": [rn_files.WAY]}
    )
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = ended(made, "rn:pruner")
    assert (code, rn_files.COMMAND in err) == (2, True)
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_nothing_is_committed_where_nothing_changed(made: WorkPlace) -> None:
    """Given the work whose steering is committed, and nothing changed since.
    When the evaluator ends.
    Then it gives 0, and commits nothing."""
    rn_files.committed_steering(made.worktree, made.name, rn_files.steering())
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, "rn:evaluator") == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_the_work_before_its_first_weighing_keeps_nothing(made: WorkPlace) -> None:
    """Given the work with no steering yet, its folder holding a note of the hearing.
    When a role ends.
    Then it gives 0, and commits nothing, as the pruner's first result makes the steering."""
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
    ("path", "text", "says"),
    [
        ("pruner.json", json.dumps({"ost": {}}), "pruner.schema.json: /message: is required"),
        ("pruner.json", "{", "the pruner's result isn't JSON"),
        ("rounds/1/a/content-1/generator.json", '{"result": "x"}', "generator-round.schema.json"),
    ],
    ids=["pruner", "pruner-not-json", "round"],
)
def test_a_result_out_of_its_schema_keeps_the_role_going(
    made: WorkPlace, path: str, text: str, says: str
) -> None:
    """Given the work whose pruner's result leaves its schema or isn't JSON, or a Round's result
    leaves its schema.
    When the role ends.
    Then it gives 2 naming the place, so that the role goes on, and commits nothing."""
    target = os.path.join(made.folder, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = ended(made, "rn:pruner")
    assert (code, says in err, err.startswith("role: ")) == (2, True, True)
    assert git(made.worktree, "rev-parse", "HEAD") == before


@pytest.mark.parametrize(
    ("origin", "code", "says"),
    [(None, 1, "no remote origin"), ("gone.git", 2, "can't push the work")],
    ids=["no-origin", "gone"],
)
def test_a_push_that_fails_is_said_after_the_commit(
    made: WorkPlace, origin: str | None, code: int, says: str
) -> None:
    """Given the work with its steering whose change can't be pushed, as it has no origin, or one
    that isn't there.
    When the generator ends.
    Then it gives 1 or 2 saying why, and the commit is kept."""
    git(top(made), "remote", "remove", "origin")
    if origin:
        gone = os.path.join(os.path.dirname(top(made)), origin)
        git(top(made), "remote", "add", "origin", gone)
    rn_files.write_json(made.steering, rn_files.steering())
    write_files(made.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    given, _, err = ended(made, "rn:generator")
    assert (given, says in err) == (code, True)
    assert subject(made) == "rn: the generator ended"


def test_arguments_of_another_form_give_the_usage() -> None:
    """Given no subcommand.
    When role runs.
    Then it gives 2 with the usage."""
    assert main([], "{}", rn_files.RN, gh_double.host("/unused")) == (2, "", USAGE)
