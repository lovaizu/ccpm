"""The unit cases of role/command.py, rn's hook once a role ends: an agent that isn't rn's left
alone, a role's change committed and pushed, a role's result moving its deliverable on, nothing
committed where nothing changed, a folder outside rn's work passed over, a session outside git, each
result out of its schema keeping the role going, a push with no origin or to a remote that isn't
there, and arguments of another form."""

from __future__ import annotations

import json
import os
from typing import Any

import pytest
import rn_files
from gh import gh_double
from host import Ran, run
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


@pytest.mark.parametrize("agent", ["Explore", "generator", "other:generator"])
def test_an_agent_that_isnt_rns_is_left_alone(made: WorkPlace, agent: str) -> None:
    """Given the work whose command's generator result is made.
    When an agent that isn't one of rn's ends: another, one named as a role with no plugin, or
    another plugin's of a role's name.
    Then it gives 0, and commits nothing."""
    made_round(made)
    before = git(made.worktree, "rev-parse", "HEAD")
    assert ended(made, agent) == (0, "", "")
    assert git(made.worktree, "rev-parse", "HEAD") == before


def made_round(work: WorkPlace) -> None:
    """Writes a steering whose command works in content-1, and the command with the generator's
    result made there."""
    value = rn_files.steering()
    value["state"]["steps"][0]["deliverables"][0]["entry"] = "content-1"
    rn_files.write_json(work.steering, value)
    write_files(work.worktree, {rn_files.COMMAND: "print('invoice')\n"})
    rn_files.write_json(
        os.path.join(round_of(work), "generator.json"),
        {"result": "made", "files": [rn_files.COMMAND]},
    )


def round_of(work: WorkPlace) -> str:
    """The command's content-1 in step 1."""
    return os.path.join(work.rounds, "1", "invoice%2F__main__.py", "content-1")


def test_a_roles_result_moves_its_deliverable_on_and_is_pushed_from_inside_the_worktree(
    made: WorkPlace,
) -> None:
    """Given a steering whose command works in content-1, the command and the generator's result
    made there, and a session in the work's worktree.
    When the generator ends.
    Then the steering has the command's evaluator next, and each change is committed as `rn: the
    generator ended`, and pushed."""
    made_round(made)
    assert ended(made, "rn:generator", cwd=made.worktree) == (0, "", "")
    with open(made.steering, encoding="utf-8") as f:
        assert json.load(f)["state"]["steps"][0]["deliverables"][0]["next"] == "evaluator"
    assert subject(made) == "rn: the generator ended"
    assert pushed(made) and git(made.worktree, "status", "--porcelain") == ""


def test_a_change_that_no_result_of_the_role_moved_is_left_for_its_own_role(
    made: WorkPlace,
) -> None:
    """Given the work whose command a generator is still writing, with no result yet.
    When another role ends, the evaluator, and then a generator.
    Then each gives 0, and commits nothing, as the command's own generator has yet to end."""
    rn_files.write_json(made.steering, rn_files.steering())
    write_files(made.worktree, {rn_files.COMMAND: "print('invo"})
    before = git(made.worktree, "rev-parse", "HEAD")
    assert (ended(made, "rn:evaluator"), ended(made, "rn:generator")) == ((0, "", ""),) * 2
    assert git(made.worktree, "rev-parse", "HEAD") == before


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
    """Given a steering whose command works in content-1, its generator's result there out of its
    schema or not JSON.
    When the generator ends.
    Then it gives 2 naming the place, so that the role goes on, and commits nothing."""
    made_round(made)
    with open(os.path.join(round_of(made), "generator.json"), "w", encoding="utf-8") as f:
        f.write(text)
    before = git(made.worktree, "rev-parse", "HEAD")
    code, _, err = ended(made, "rn:generator")
    assert (code, says in err, err.startswith("role: ")) == (2, True, True)
    assert git(made.worktree, "rev-parse", "HEAD") == before


def test_a_push_with_no_origin_is_said_after_the_commit(made: WorkPlace) -> None:
    """Given the work whose generator's result is made, and a repository with no origin.
    When the generator ends.
    Then it gives 1 saying so, so that the role ends, and the commit is kept."""
    git(top(made), "remote", "remove", "origin")
    made_round(made)
    code, _, err = ended(made, "rn:generator")
    assert (code, "no remote origin" in err) == (1, True)
    assert subject(made) == "rn: the generator ended"


def test_a_push_that_git_refuses_waits_for_the_next(made: WorkPlace) -> None:
    """Given the work whose generator's result is made, and origin a folder that isn't there.
    When the generator ends.
    Then it gives 0, and the commit is kept for the next push."""
    git(top(made), "remote", "set-url", "origin", os.path.join(os.path.dirname(top(made)), "x"))
    made_round(made)
    assert ended(made, "rn:generator") == (0, "", "")
    assert subject(made) == "rn: the generator ended"


def test_a_commit_that_git_refuses_is_said(made: WorkPlace) -> None:
    """Given the work whose generator's result is made, and git that refuses each commit.
    When the generator ends.
    Then it gives 1 with what git said, so that the role ends."""
    made_round(made)

    def refusing(argv: Any, cwd: str, env: Any = None) -> Any:
        return Ran(1, "", "hook refused\n") if argv[1:2] == ["commit"] else run(argv, cwd, env)

    code, _, err = ended(made, "rn:generator", host=refusing)
    assert (code, "git commit fails: hook refused" in err) == (1, True)


def test_arguments_of_another_form_give_the_usage() -> None:
    """Given no subcommand.
    When role runs.
    Then it gives 2 with the usage."""
    assert main([], "{}", rn_files.RN, gh_double.host("/unused")) == (2, "", USAGE)
