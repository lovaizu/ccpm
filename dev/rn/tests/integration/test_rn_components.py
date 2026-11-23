"""The integration cases of each component's decisions and of each handoff with its data, as rn's
architecture draws them under Components and Concept model: each command an entry to the
orchestrator, the Cut and the checks of the generator, and the best practice each role takes. Each
runs rn's scripts as the orchestrator and each role run them, with the double of gh, and a double
of each prompt's work."""

from __future__ import annotations

import json
import os
import shutil

import pytest
import rn_files
from gh import gh_double
from repo_files import git
from rn_bench import (
    Bench,
    command_signed,
    confirmed,
    cut_move,
    cut_of,
    planned_tree,
    requested,
    resulted,
    reviewed,
    signed,
    signed_plan,
    to_plan_signoff,
    trial_made,
    wrote,
)
from rn_files import COMMAND, GOAL, GUIDE

# The orchestrator: each command an entry.

COMMANDS = ("on", "up", "dn", "ty", "gm")
# Each command, and whether only the user may call it, as it approves what rn put up.
APPROVES = [(each, each in ("ty", "gm")) for each in COMMANDS]


def skill(b: Bench, command: str) -> str:
    """The text of the command's SKILL.md, as Claude Code loads it."""
    with open(os.path.join(b.rn, "skills", command, "SKILL.md"), encoding="utf-8") as f:
        return f.read()


@pytest.mark.supports("orchestrator")
@pytest.mark.parametrize("command", COMMANDS)
def test_each_command_points_to_the_orchestrators_steps(b: Bench, command: str):
    """Given rn's command
    When Claude Code loads its SKILL.md
    Then it points to domain/orchestrator.md under rn's folder, which the bench's copy holds"""
    assert "${CLAUDE_PLUGIN_ROOT}/domain/orchestrator.md" in skill(b, command)
    assert os.path.isfile(os.path.join(b.rn, "domain", "orchestrator.md"))


@pytest.mark.supports("orchestrator")
@pytest.mark.parametrize(("command", "refused"), APPROVES)
def test_an_ai_calls_the_commands_that_give_out_work_and_never_those_that_approve(
    b: Bench, command: str, refused: bool
):
    """Given rn's command
    When an AI that gives out work would call it by the Skill tool
    Then the frontmatter of /rn:ty and /rn:gm holds disable-model-invocation true, as only the
    user approves, and that of /rn:on, /rn:up, and /rn:dn holds none"""
    front = skill(b, command).split("---")[1]
    assert ("disable-model-invocation: true" in front) == refused


# The generator: its Cut, and the checks before its end.


@pytest.mark.supports("generator", "Cut", "Best practice")
def test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice(b: Bench):
    """Given a run whose plan the user signed off
    When the orchestrator writes the command's Cut
    Then the Cut holds the goal, the deliverables' language, the command's node as the tree holds
    it, the run's worktree, the path of invoicer's lines in the worktree as its one input, rn's
    light best practice, Round content-1, and no findings or good of an earlier Round"""
    given = cut_of(b, signed_plan(b))
    node = next(each for each in b.tree()["deliverables"] if each["path"] == COMMAND)
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert given["goal"] == GOAL
    assert given["language"] == rn_files.DELIVERABLES_LANGUAGE
    assert given["deliverable"] == node
    assert os.path.normpath(os.path.join(b.repo, given["worktree"])) == b.worktree
    assert [os.path.normpath(os.path.join(b.repo, each)) for each in given["inputs"]] == [
        os.path.join(b.worktree, "invoicer", "lines.py")
    ]
    assert os.path.normpath(os.path.join(b.repo, given["best_practice"])) == os.path.join(
        b.rn, "domain", "best-practices", "light"
    )
    assert (given["stage"], given["number"]) == ("content", 1)
    assert os.path.normpath(os.path.join(b.repo, given["round"])) == first
    assert (given["findings"], given["last_good"]) == (None, None)
    assert os.path.isabs(given["trial"])


@pytest.mark.supports("generator", "scripts")
def test_the_generators_try_puts_the_peoples_files_in_its_folder_outside_the_work(b: Bench):
    """Given a run whose command's generator wrote the command
    When it runs repository.py trial for its Round
    Then the folder it prints is the Cut's trial, outside the run's worktree, holding the
    command"""
    cut_path = signed_plan(b)
    wrote(b, {COMMAND: "print('invoice')\n"})
    trial = trial_made(b, cut_path)
    assert os.path.samefile(trial, cut_of(b, cut_path)["trial"])
    assert not os.path.realpath(trial).startswith(os.path.realpath(b.worktree) + os.sep)
    assert os.path.isfile(os.path.join(trial, COMMAND))


def checked(b: Bench, cut_path: str, files: dict[str, str], result: dict) -> tuple[int, str]:
    """The generator writes the files and its result, and runs check.py generator; gives its exit
    code and what it printed."""
    wrote(b, files)
    resulted(b, cut_path, "generator", result)
    done = b.script("check", "generator", cut_path)
    return done.code, done.out + done.err


@pytest.mark.supports("generator", "Round")
def test_a_generators_good_of_a_condition_its_deliverable_lacks_is_refused(b: Bench):
    """Given a run whose command's generator wrote the command
    When its result names good a condition N9 that light doesn't hold, and it runs check.py
    Then check.py gives 1 naming N9"""
    result = rn_files.made([("N9", ["print('invoice')"])], [COMMAND])
    code, said = checked(b, signed_plan(b), {COMMAND: "print('invoice')\n"}, result)
    assert code == 1
    assert "N9" in said


@pytest.mark.supports("generator", "Round")
def test_a_generators_good_quoting_a_line_no_file_holds_is_refused(b: Bench):
    """Given a run whose command's generator wrote the command
    When its good of N1 quotes a line that the command doesn't hold, and it runs check.py
    Then check.py gives 1 naming the line"""
    result = rn_files.made([("N1", ["print('receipt')"])], [COMMAND])
    code, said = checked(b, signed_plan(b), {COMMAND: "print('invoice')\n"}, result)
    assert code == 1
    assert "print('receipt')" in said


@pytest.mark.supports("generator", "scripts")
def test_a_generators_check_whose_runs_folder_is_gone_gives_2_saying_what_it_couldnt_check(
    b: Bench,
):
    """Given a run whose command's generator wrote the command and its result
    When the user deletes the run's folder, as in dropping the run, and the generator runs
    check.py
    Then check.py gives 2 saying that it couldn't check the generator's result, as its Cut can't
    be read, so that the generator ends saying so"""
    cut_path = signed_plan(b)
    wrote(b, {COMMAND: "print('invoice')\n"})
    resulted(b, cut_path, "generator", rn_files.made([("N1", ["print('invoice')"])], [COMMAND]))
    shutil.rmtree(b.folder)
    done = b.script("check", "generator", cut_path)
    assert done.code == 2
    assert done.err.startswith("check.py: couldn't check the generator's result, as its Cut ")


@pytest.mark.supports("generator", "Best practice")
def test_a_generators_end_with_its_deliverable_off_its_template_is_held(b: Bench):
    """Given a run whose guide's generator, of the kind readme, wrote the guide
    When the guide holds none of the readme template's sections, and it runs check.py
    Then check.py gives 1 with the template check's places, each `docs/guide.md:<line>: ...`"""
    text = "# Print an invoice\n\nSave the lines as lines.csv, and type the command.\n"
    result = rn_files.made([("N1", ["# Print an invoice"])], [GUIDE])
    code, said = checked(b, command_signed(b), {GUIDE: text}, result)
    assert code == 1
    assert f"{GUIDE}:" in said


@pytest.mark.supports("generator", "scripts")
def test_the_generators_checks_give_the_repositorys_commit_check_findings(b: Bench):
    """Given invoicer's repository with a pre-commit hook that refuses each commit of the command,
    saying `invoicer/__main__.py: no tests`, and a run whose command's generator wrote the command
    When it runs repository.py checks on the command
    Then it gives 1 with the hook's line, and the repository's own index is as it was"""
    hook = os.path.join(b.repo, ".git", "hooks", "pre-commit")
    with open(hook, "w", encoding="utf-8") as f:
        f.write(
            "#!/bin/sh\n"
            "git diff --cached --name-only | grep -qx 'invoicer/__main__.py' || exit 0\n"
            "echo 'invoicer/__main__.py: no tests'\n"
            "exit 1\n"
        )
    os.chmod(hook, 0o755)
    signed_plan(b)
    wrote(b, {COMMAND: "print('invoice')\n"})
    found = b.script("repository", "checks", b.run, COMMAND)
    assert found.code == 1
    assert "invoicer/__main__.py: no tests" in found.out
    assert git(b.repo, "diff", "--cached", "--name-only").strip() == ""


def cache_left(b: Bench) -> tuple[str, str]:
    """The generator wrote the command, and its tests left a cache beside it; gives its Cut, and
    the cache's folder from the repository's top, as the generator names it."""
    cut_path = signed_plan(b)
    wrote(b, {COMMAND: "print('invoice')\n", "invoicer/__pycache__/__main__.pyc": "cache\n"})
    return cut_path, os.path.relpath(os.path.join(b.worktree, "invoicer", "__pycache__"), b.repo)


@pytest.mark.supports("generator", "scripts")
def test_a_makers_clean_up_by_remove_py_removes_each_exact_path_it_made(b: Bench):
    """Given a run whose command's generator wrote the command, left a cache of its tests beside
    it, and made its folder of the people's starting state by repository.py trial
    When it runs remove.py on the cache's folder and the trial's, one argument each
    Then remove.py gives 0, both are gone, and the command stays"""
    cut_path, cache = cache_left(b)
    trial = trial_made(b, cut_path)
    assert b.script("remove", cache, trial).code == 0
    assert not os.path.lexists(os.path.join(b.repo, cache))
    assert not os.path.lexists(trial)
    assert os.path.isfile(os.path.join(b.worktree, COMMAND))


@pytest.mark.supports("generator", "scripts")
def test_a_makers_clean_up_by_a_wildcard_is_refused_with_how_to_use_remove_py(b: Bench):
    """Given a run whose command's generator wrote the command and left a cache of its tests
    beside it
    When it runs remove.py on `<cache>/*.pyc`, which no shell expanded
    Then remove.py gives 2 with its usage and the pattern named, and the cache stays"""
    cache = cache_left(b)[1]
    refused = b.script("remove", f"{cache}/*.pyc")
    assert refused.code == 2
    assert refused.err.startswith("usage: remove.py")
    assert f"{cache}/*.pyc" in refused.err
    assert os.path.isfile(os.path.join(b.repo, cache, "__main__.pyc"))


def bash_hook(b: Bench) -> str:
    """The command of rn's hook before each Bash call, as hooks/hooks.json names it."""
    with open(os.path.join(b.rn, "hooks", "hooks.json"), encoding="utf-8") as f:
        (before,) = json.load(f)["hooks"]["PreToolUse"]
    assert before["matcher"] == "Bash"
    (hook,) = before["hooks"]
    return hook["command"]


def bash_called(b: Bench, command: str, agent: str | None) -> str:
    """The hook's input of a Bash call of the command by the agent, or by the main conversation
    where none is named, as Claude Code gives it."""
    called = {
        "session_id": "abc123",
        "cwd": b.repo,
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_use_id": "toolu_01",
    }
    if agent is not None:
        called.update({"agent_id": "a1", "agent_type": agent})
    return json.dumps(called)


@pytest.mark.supports("generator", "scripts")
def test_a_makers_delete_by_rm_is_denied_pointing_to_remove_py(b: Bench):
    """Given rn's hook before each Bash call, and a run whose command's generator left a cache of
    its tests beside the command
    When the generator calls Bash with `rm -r "$W/$p/__pycache__"`, and Claude Code runs the hook
    Then the hook denies the call, its reason giving remove.py's command by its path in rn's
    folder, and that command removes the cache"""
    assert "${CLAUDE_PLUGIN_ROOT}/scripts/hook.py" in bash_hook(b)
    cache = cache_left(b)[1]
    hooked = b.script("hook", given=bash_called(b, 'rm -r "$W/$p/__pycache__"', "rn:generator"))
    assert (hooked.code, hooked.err) == (0, "")
    output = json.loads(hooked.out)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"
    remove = os.path.join(b.rn, "scripts", "remove.py")
    assert f"python3 {remove} <exact path>" in output["permissionDecisionReason"]
    assert b.script("remove", cache).code == 0
    assert not os.path.lexists(os.path.join(b.repo, cache))


@pytest.mark.supports("orchestrator", "scripts")
def test_a_delete_by_the_main_conversation_passes_the_hook(b: Bench):
    """Given rn's hook before each Bash call
    When the main conversation, which names no agent, calls Bash with `rm -r build`
    Then the hook gives 0 and prints nothing, so that the call goes on as without rn"""
    hooked = b.script("hook", given=bash_called(b, "rm -r build", None))
    assert hooked == (0, "", "")


# The scripts: the best practice each role takes, and a refusal before any push.


@pytest.mark.supports("scripts", "Best practice")
def test_a_runs_own_best_practice_is_taken_before_rns(b: Bench):
    """Given a run whose worktree holds its own best practice of the kind light, at
    .rn/best-practices/light/, and whose plan the user signed off
    When the orchestrator writes the command's Cut
    Then the Cut's best practice is the run's own folder"""
    to_plan_signoff(b)
    own = os.path.join(b.worktree, ".rn", "best-practices", "light")
    shutil.copytree(os.path.join(b.rn, "domain", "best-practices", "light"), own)
    cut_path = signed(b, [cut_move(b, "generator", COMMAND)])[0].strip()
    assert os.path.normpath(os.path.join(b.repo, cut_of(b, cut_path)["best_practice"])) == own


@pytest.mark.supports("scripts", "Design tree")
def test_a_put_up_without_a_login_of_gh_is_refused_before_any_push(b: Bench):
    """Given a run whose plan has each condition good, and gh with no login
    When the orchestrator puts the plan up by repository.py put-up
    Then it gives 1 with what gh auth status said, gh was asked nothing after it, and the remote
    holds no branch of the run"""
    requested(b)
    confirmed(b)
    reviewed(b, planned_tree(b, answered=True), "The user's answer.")
    gh_double.logged_out(b.gh)
    refused = b.script("repository", "put-up", b.run, rn_files.plan_path(b.name()))
    assert refused.code == 1
    assert "You are not logged into any GitHub hosts." in refused.err
    assert [each[:3] for each in b.asked_gh()] == [["gh", "auth", "status"]]
    assert f"rn-{b.name()}" not in git(b.origin, "branch", "--list").split()
