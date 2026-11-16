"""The unit cases of rn's prompts on the model, as rn's Test strategy says: each skill with the
orchestrator's part, and each role with its part, alone on Opus by `claude -p`, in a throwaway copy
of invoicer from the walkthrough's bench, each case run RUNS times, a run a test of its own, and the
developer adds runs until one more changes no case's count. For each kind of request, a case where
the prompt's description says it acts and one where it says it doesn't, each read by code from
what the run left: rn's worktree, the run's records, its sign-offs, and what Claude Code printed.
They run on the developer's login, so a case without one is skipped, as opus.NEEDS_LOGIN says."""

from __future__ import annotations

import glob
import json
import os
import subprocess
from typing import Any

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.tests import opus

pytestmark = opus.NEEDS_LOGIN

# Why a case beyond the walking skeleton still fails: the steps of a prompt it runs aren't written.
LATER = pytest.mark.xfail(strict=True, reason="rn's prompts' steps are empty")
# Why the generator's case still fails: the walkthrough's deliverable is checked by mypy --strict,
# which the bench lacks, so the generator ends with lacks before it writes its Made.
NO_MYPY = pytest.mark.xfail(
    strict=True, reason="mypy, which the walkthrough's check runs, isn't installed"
)

# Why the case of a deliverable done before still fails: the Cut doesn't yet give the commit it was
# done at, as cut._generator doesn't and branch.done_at has an empty body, and the generator's steps
# don't yet say to read each input's change since then.
NOT_DONE_AT = pytest.mark.xfail(
    strict=True, reason="the generator's Cut doesn't yet give done_at, nor its steps read by it"
)

RUNS = 5
# A change to the design tree that changes nothing.
NOTHING: dict[str, Any] = {"nodes": {}, "more": []}


def claude(b: w.Bench, folder: str, prompt: str, agent: str | None = None) -> str:
    """Runs the prompt on Opus with rn and Lane loaded, in the folder, as the role `agent` where
    given, and gives what Claude Code printed."""
    env = dict(b.env, CLAUDE_CONFIG_DIR=os.path.join(b.temp, "config"))
    flags = ["--plugin-dir", b.lane, "--plugin-dir", b.rn]
    flags += ["--agent", agent] if agent else []
    return opus.prompted(prompt, folder, env, flags, 1800)


def worktrees(b: w.Bench) -> list[str]:
    """Each worktree of a run of rn in invoicer."""
    return glob.glob(os.path.join(b.repo, ".claude", "worktrees", "rn-*"))


def entries(path: str) -> list[dict[str, Any]]:
    """Each entry of the record at the path, none where it isn't there."""
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)["entries"]


def tree_py(b: w.Bench, *args: str, cwd: str, given: str = "") -> str:
    """What rn's tree.py printed for the arguments, run in the folder with the input given."""
    done = subprocess.run(
        ["python3", os.path.join(b.rn, "scripts", "tree.py"), *args],
        cwd=cwd,
        input=given,
        env=dict(os.environ, **b.env),
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def planned_run(b: w.Bench, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    """A run of the walkthrough set up by rn's own scripts: started, its goal and the plan, the
    walkthrough's by default, written, and its plan put up for the user's sign-off; gives what
    tree.py start printed."""
    run = json.loads(tree_py(b, "start", w.GOAL_NAME, cwd=b.repo))
    tree_py(
        b,
        "write",
        run["record"],
        "The goal drafted, and the plan.",
        cwd=run["worktree"],
        given=json.dumps(plan or w.walkthrough_plan()),
    )
    tree_py(b, "put-up", "plan", cwd=run["worktree"])
    return run


def signed_off(b: w.Bench, run: dict[str, Any]) -> None:
    """The plan of the run approved, and the tree-keeper's write of the sign-off, which marks each
    deliverable whose turn came doing, as S3 draws after /rn:ty."""
    tree_py(b, "approve", cwd=run["worktree"])
    tree_py(
        b, "write", run["record"], "Signed off.", cwd=run["worktree"], given=json.dumps(NOTHING)
    )


def generator_text(b: w.Bench, run: dict[str, Any]) -> str:
    """The text of the generator's next start, as its adapter gives it with no start running."""
    adapter = subprocess.run(
        ["python3", os.path.join(b.rn, "hooks", "adapters", "text.py"), "generator"],
        cwd=run["worktree"],
        input='{"running": []}',
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(adapter.stdout)["text"]


def bash_run(b: w.Bench) -> list[str]:
    """Each command that a run of Claude Code on the bench ran by Bash, from its transcripts."""
    commands = []
    for path in glob.glob(
        os.path.join(b.temp, "config", "projects", "**", "*.jsonl"), recursive=True
    ):
        with open(path, encoding="utf-8") as f:
            for line in f:
                content = json.loads(line).get("message", {}).get("content")
                for each in content if isinstance(content, list) else []:
                    if each.get("type") == "tool_use" and each.get("name") == "Bash":
                        commands.append(each["input"].get("command", ""))
    return commands


@pytest.mark.supports("test_a_request_starts_a_run_anew_with_the_tree_keepers_start_first")
@pytest.mark.parametrize("prompt", [f"/rn:up {w.WORDS}", f"Have rn make {w.WORDS}."])
@pytest.mark.parametrize("run", range(RUNS))
def test_up_acts_on_a_request_typed_or_asked_for(tmp_path: Any, prompt: str, run: int) -> None:
    """Given: invoicer with rn installed, and no run.
    When: the person types /rn:up with the walkthrough's request, or asks rn for it in words.
    Then: the orchestrator starts one run, and its record holds the steps of up."""
    b = w.bench(str(tmp_path))
    claude(b, b.repo, prompt)
    [made] = worktrees(b)
    record = glob.glob(os.path.join(made, ".rn", "*", "records", "*.json"))
    assert any(e["of"] == "up" for path in record for e in entries(path))


@LATER
@pytest.mark.supports("test_up_alone_with_no_run_left_says_so_and_starts_no_role")
@pytest.mark.parametrize("prompt", ["What does invoicer's total take?", "/rn:up"])
@pytest.mark.parametrize("run", range(RUNS))
def test_up_starts_no_run_on_a_question_or_with_nothing_to_pick_up(
    tmp_path: Any, prompt: str, run: int
) -> None:
    """Given: invoicer with rn installed, and no run.
    When: the person asks a question of the code, or types /rn:up alone.
    Then: no run starts, and /rn:up alone says that rn has no run to pick up."""
    b = w.bench(str(tmp_path))
    printed = claude(b, b.repo, prompt)
    assert worktrees(b) == []
    assert prompt != "/rn:up" or w.NO_RUN_SHOWN in printed


@LATER
@pytest.mark.supports("test_ty_approves_the_plan_and_starts_the_work_resting_on_it")
@pytest.mark.parametrize(
    ("prompt", "state"), [("/rn:ty", "signed off"), ("Looks fine, go on.", "waiting")]
)
@pytest.mark.parametrize("run", range(RUNS))
def test_only_the_typed_ty_signs_off_the_plan(
    tmp_path: Any, prompt: str, state: str, run: int
) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the person types /rn:ty in the run's worktree, or says in words that it looks fine.
    Then: the plan is signed off, or still waits."""
    b = w.bench(str(tmp_path))
    started = planned_run(b)
    claude(b, started["worktree"], prompt)
    path = os.path.join(started["worktree"], started["folder"], "sign-offs.json")
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["sign_offs"][0]["state"] == state


@LATER
@pytest.mark.supports("test_gm_with_words_sends_the_plan_back_to_the_decision_it_changes")
@pytest.mark.parametrize(
    ("prompt", "state"),
    [
        ("/rn:gm only the functions that callers import", "sent back"),
        ("Hmm, maybe fewer files?", "waiting"),
    ],
)
@pytest.mark.parametrize("run", range(RUNS))
def test_only_the_typed_gm_sends_the_plan_back(
    tmp_path: Any, prompt: str, state: str, run: int
) -> None:
    """Given: the walkthrough's plan put up for the user's sign-off.
    When: the person types /rn:gm with what to change, or wonders in words about it.
    Then: the plan is sent back, or still waits."""
    b = w.bench(str(tmp_path))
    started = planned_run(b)
    claude(b, started["worktree"], prompt)
    path = os.path.join(started["worktree"], started["folder"], "sign-offs.json")
    with open(path, encoding="utf-8") as f:
        assert json.load(f)["sign_offs"][0]["state"] == state


@LATER
@pytest.mark.supports("test_dn_stops_the_generator_and_pushes_its_work_with_the_step_it_stood_at")
@pytest.mark.parametrize(("prompt", "pushed"), [("/rn:dn", True), ("I'll stop for today.", False)])
@pytest.mark.parametrize("run", range(RUNS))
def test_only_the_typed_dn_pauses_the_run(
    tmp_path: Any, prompt: str, pushed: bool, run: int
) -> None:
    """Given: the walkthrough's plan put up, its run's branch on no remote yet.
    When: the person types /rn:dn in the run's worktree, or says in words they'll stop.
    Then: the remote holds the work's branch after /rn:dn alone."""
    b = w.bench(str(tmp_path))
    started = planned_run(b)
    claude(b, started["worktree"], prompt)
    branch = w.git(started["worktree"], "branch", "--show-current").strip()
    assert bool(w.git(b.repo, "ls-remote", "origin", branch).strip()) is pushed


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
@pytest.mark.parametrize("role", ["tree-keeper", "generator", "evaluator"])
@pytest.mark.parametrize("run", range(RUNS))
def test_no_role_starts_for_a_request_made_without_rn(tmp_path: Any, role: str, run: int) -> None:
    """Given: invoicer with rn installed, and no run.
    When: the person asks Claude Code itself to add type hints to invoicer/totals.py, naming no rn.
    Then: no run of rn starts and no record of the role is made, as each role says it's started by
    /rn:up alone."""
    b = w.bench(str(tmp_path))
    claude(b, b.repo, "Add type hints to invoicer/totals.py.")
    assert worktrees(b) == []
    assert not glob.glob(os.path.join(b.repo, "**", f"*{role}*.json"), recursive=True)


@NO_MYPY
@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_generator_started_with_its_cut_records_and_writes_its_made(
    tmp_path: Any, run: int
) -> None:
    """Given: the walkthrough's plan signed off, and the generator's Cut of "Type hints in each file
    of invoicer" as its adapter gives it.
    When: the generator runs alone with the Cut as its prompt.
    Then: its record holds each step of its part, and its Made names the user's decision."""
    b = w.bench(str(tmp_path))
    started = planned_run(b)
    signed_off(b, started)
    text = generator_text(b, started)
    cut = w.cut_of(text)
    claude(b, started["worktree"], text, "rn:generator")
    recorded = {
        e["step"] for e in entries(os.path.join(started["worktree"], cut["record"])) if "step" in e
    }
    assert recorded == set(w.steps_of(b.rn, "domain/generator.md"))
    with open(os.path.join(started["worktree"], cut["made"]), encoding="utf-8") as f:
        made = json.load(f)
    assert [d["path"] for d in made["decisions"]] == [
        e["decision"]["path"] for e in cut["cut"]["decisions"]
    ]


@NOT_DONE_AT
@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_generator_reworking_a_deliverable_done_before_reads_the_change_since_then(
    tmp_path: Any, run: int
) -> None:
    """Given: "Type hints in each file of invoicer", which takes pyproject.toml as its input, marked
    done; then pyproject.toml changed, and the deliverable open again with the user's decision on
    which files changed; and the generator's Cut of it, as its adapter gives it.
    When: the generator runs alone with the Cut as its prompt.
    Then: the Cut gives the commit that marked the deliverable done, and the generator runs a
    command that names that commit, as it reads each input's change since then."""
    b = w.bench(str(tmp_path))
    started = planned_run(b, w.plan(w.hints_from_pyproject()))
    signed_off(b, started)
    worktree, record = started["worktree"], started["record"]
    done = {"nodes": {"deliverables/0": w.hints_done()}, "more": []}
    tree_py(b, "write", record, "The user signed it off.", cwd=worktree, given=json.dumps(done))
    done_at = w.last_tree_commit(worktree, started["folder"])
    w.pyproject_changed(worktree)
    again = {"nodes": {"deliverables/0": w.hints_from_pyproject(w.BUT_THE_TESTS)}, "more": []}
    tree_py(
        b, "write", record, "The user leaves out the tests.", cwd=worktree, given=json.dumps(again)
    )
    text = generator_text(b, started)
    assert w.cut_of(text)["cut"]["done_at"] == done_at
    claude(b, worktree, text, "rn:generator")
    assert any(done_at[:7] in command for command in bash_run(b))
