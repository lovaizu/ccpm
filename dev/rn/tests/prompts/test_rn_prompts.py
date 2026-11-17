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
import re
import subprocess
import uuid
from typing import Any

import pytest

from dev.rn.tests import rn_walkthrough as w
from dev.tests import opus

pytestmark = opus.NEEDS_LOGIN

RUNS = 5
# A deliverable that Python alone tries, and the user's decision under it, which the generator's
# Made names.
VERSIONED = "A caller reads which invoicer they run as invoicer.__version__"
SAME_VERSION = {
    "about": "the version it gives",
    "decided": "the version that pyproject.toml gives, kept beside it in invoicer/__init__.py",
    "by": "user",
}
# A change to the design tree that changes nothing.
NOTHING: dict[str, Any] = {"nodes": {}, "more": []}


def claude(
    b: w.Bench, folder: str, prompt: str, agent: str | None = None, talk: tuple[str, ...] = ()
) -> str:
    """Runs the prompt on Opus with rn and Lane loaded, in the folder, as the role `agent` where
    given, in the conversation that `talk`'s flags start or resume where given, as the orchestrator
    resumes a role, and gives what Claude Code printed."""
    env = dict(b.env, CLAUDE_CONFIG_DIR=os.path.join(b.temp, "config"))
    flags = ["--plugin-dir", b.lane, "--plugin-dir", b.rn, *talk]
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


def start_text(b: w.Bench, run: dict[str, Any], role: str = "generator") -> str:
    """The text of the role's next start, as its adapter gives it with no start running."""
    adapter = subprocess.run(
        ["python3", os.path.join(b.rn, "hooks", "adapters", "text.py"), role],
        cwd=run["worktree"],
        input='{"running": []}',
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(adapter.stdout)["text"]


def keeper_resumed(b: w.Bench, run: dict[str, Any], grounds: str, change: Any) -> str:
    """The tree-keeper started alone with its Cut, as its adapter gives it, then resumed in the
    same conversation with the change and its grounds, as the orchestrator resumes it; gives what
    Claude Code printed at the resume."""
    session = str(uuid.uuid4())
    text = start_text(b, run, "tree-keeper")
    claude(b, run["worktree"], text, "rn:tree-keeper", ("--session-id", session))
    resume = w.resume_text(grounds, None, change)
    return claude(b, run["worktree"], resume, "rn:tree-keeper", ("--resume", session))


def tree_of(run: dict[str, Any]) -> str:
    """The text of the run's design tree, or none where it isn't there."""
    path = os.path.join(run["worktree"], run["folder"], "design-tree.json")
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def results_of(b: w.Bench, role: str) -> list[str]:
    """Each result the role gave by Lane's result.py in a run on the bench, in order."""
    return [found for c in bash_run(b) for found in re.findall(rf"result\.py {role} (\w+)", c)]


def calls(b: w.Bench) -> list[tuple[str, dict[str, Any]]]:
    """Each tool call of a run of Claude Code on the bench, by the tool's name with its input, from
    its transcripts."""
    made = []
    for path in glob.glob(
        os.path.join(b.temp, "config", "projects", "**", "*.jsonl"), recursive=True
    ):
        with open(path, encoding="utf-8") as f:
            for line in f:
                content = json.loads(line).get("message", {}).get("content")
                for each in content if isinstance(content, list) else []:
                    if each.get("type") == "tool_use":
                        made.append((each.get("name", ""), each.get("input", {})))
    return made


def bash_run(b: w.Bench) -> list[str]:
    """Each command that a run of Claude Code on the bench ran by Bash."""
    return [str(given.get("command", "")) for name, given in calls(b) if name == "Bash"]


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
    When: the person asks Claude Code itself to round the tax in invoicer/tax.py half to even,
    naming no rn.
    Then: no run of rn starts and no record of the role is made, as each role says it's started by
    /rn:up alone."""
    b = w.bench(str(tmp_path))
    claude(b, b.repo, "Round the tax in invoicer/tax.py half to even.")
    assert worktrees(b) == []
    assert not glob.glob(os.path.join(b.repo, "**", f"*{role}*.json"), recursive=True)


@pytest.mark.supports("test_the_generator_starts_with_its_cut_of_the_first_deliverable_doing")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_generator_started_with_its_cut_records_and_writes_its_made(
    tmp_path: Any, run: int
) -> None:
    """Given: a plan of invoicer.__version__, with the user's decision on the version it gives,
    signed off, and the generator's Cut of it as its adapter gives it, as Python alone tries it.
    When: the generator runs alone with the Cut as its prompt.
    Then: its record holds each step of its part, and its Made names the user's decision."""
    b = w.bench(str(tmp_path))
    versioned = w.deliverable(VERSIONED, "invoicer/__init__.py")
    versioned["necessary_conditions"][0]["decisions"] = [SAME_VERSION]
    started = planned_run(b, w.plan(versioned))
    signed_off(b, started)
    text = start_text(b, started)
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


@pytest.mark.supports("test_a_deliverable_done_before_is_reworked_from_the_commit_it_was_done_at")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_generator_reworking_a_deliverable_done_before_reads_the_change_since_then(
    tmp_path: Any, run: int
) -> None:
    """Given: the command, which takes pyproject.toml as its input, marked done; then
    pyproject.toml changed, and the deliverable open again with the user's decision on how the tax
    rate is given changed; and the generator's Cut of it, as its adapter gives it.
    When: the generator runs alone with the Cut as its prompt.
    Then: the Cut gives the commit that marked the deliverable done, and the generator runs a
    command that names that commit, as it reads each input's change since then."""
    b = w.bench(str(tmp_path))
    started = planned_run(b, w.plan(w.command_from_pyproject()))
    signed_off(b, started)
    worktree, record = started["worktree"], started["record"]
    done = {"nodes": {"deliverables/0": w.command_done()}, "more": []}
    tree_py(b, "write", record, "The user signed it off.", cwd=worktree, given=json.dumps(done))
    done_at = w.last_tree_commit(worktree, started["folder"])
    w.pyproject_changed(worktree)
    again = {"nodes": {"deliverables/0": w.command_from_pyproject(w.OR_THE_DEFAULT)}, "more": []}
    tree_py(
        b,
        "write",
        record,
        "The user lets the rate default to pyproject.toml's.",
        cwd=worktree,
        given=json.dumps(again),
    )
    text = start_text(b, started)
    assert w.cut_of(text)["cut"]["done_at"] == done_at
    claude(b, worktree, text, "rn:generator")
    assert any(done_at[:7] in command for command in bash_run(b))


@pytest.mark.supports("test_the_goal_and_the_plan_reach_the_design_tree_through_the_tree_keeper")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_tree_keeper_writes_the_change_it_is_resumed_with(tmp_path: Any, run: int) -> None:
    """Given: the walkthrough's run started, with no design tree yet.
    When: the tree-keeper starts alone with its Cut, then is resumed with the goal drafted and the
    walkthrough's plan.
    Then: the run's design tree holds the plan, committed with the grounds word for word as its
    message, and the tree-keeper ends with done."""
    b = w.bench(str(tmp_path))
    started = json.loads(tree_py(b, "start", w.GOAL_NAME, cwd=b.repo))
    grounds = "The goal drafted from the request, and the plan of its two deliverables."
    keeper_resumed(b, started, grounds, w.walkthrough_plan())
    tree = json.loads(tree_of(started) or "{}")
    assert [d["name"] for d in tree.get("deliverables", [])] == [w.COMMAND, w.GUIDE]
    path = os.path.join(started["folder"], "design-tree.json")
    assert w.git(started["worktree"], "log", "-1", "--format=%B", "--", path).strip() == grounds
    assert results_of(b, "tree-keeper")[-1:] == ["done"]


@pytest.mark.supports("test_a_more_kept_with_no_decision_changed_is_refused")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_tree_keeper_gives_refused_for_a_more_whose_decision_didnt_change(
    tmp_path: Any, run: int
) -> None:
    """Given: the plan of the command, with the user's decision on how the tax rate is given,
    signed off, and its first round opened by the generator's first step's commit.
    When: the tree-keeper is resumed with the more of N2 of code to keep, naming the user's
    decision, which the change leaves as it was.
    Then: the design tree is as it was, and the tree-keeper ends with refused, naming the code
    best practice and N2."""
    b = w.bench(str(tmp_path))
    started = planned_run(b, w.plan(w.command_from_pyproject(w.WITH_EACH)))
    signed_off(b, started)
    cut = w.cut_of(start_text(b, started))
    tree_py(b, "commit", cut["record"], "1", cwd=started["worktree"])
    before = tree_of(started)
    decision = "deliverables/0/necessary_conditions/0/decisions/0"
    change = {"nodes": {}, "more": [w.n2_more(decision)]}
    printed = keeper_resumed(b, started, "The people fall short by N2.", change)
    assert tree_of(started) == before
    assert results_of(b, "tree-keeper")[-1:] == ["refused"]
    assert "code" in printed and "N2" in printed


@pytest.mark.supports("test_tree_py_refuses_a_change_that_leaves_the_design_trees_form")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_tree_keeper_hands_back_a_change_out_of_form_unwritten(tmp_path: Any, run: int) -> None:
    """Given: the walkthrough's plan written.
    When: the tree-keeper is resumed with a status that the design tree's form has no place for.
    Then: the design tree is as it was, and the tree-keeper ends with done, not refused, naming
    the path, as no more was refused."""
    b = w.bench(str(tmp_path))
    started = planned_run(b)
    before = tree_of(started)
    change = {"nodes": {"deliverables/0/status": "finished"}, "more": []}
    printed = keeper_resumed(b, started, "The first deliverable is finished.", change)
    assert tree_of(started) == before
    assert results_of(b, "tree-keeper")[-1:] == ["done"]
    assert "deliverables/0/status" in printed


@pytest.mark.supports("test_an_evaluator_starts_with_only_what_the_deliverables_people_have")
@pytest.mark.parametrize("run", range(RUNS))
def test_the_evaluator_answers_its_group_with_only_what_the_people_have(
    tmp_path: Any, run: int
) -> None:
    """Given: a plan of invoicer.__version__, with the user's decision on the version it gives,
    signed off; its generator's work, the version in invoicer/__init__.py, committed, with its
    Made; and the first evaluator's Cut, as its adapter gives it.
    When: the evaluator runs alone with the Cut as its prompt.
    Then: its Answers answer each condition of its group, and it opened none of the design tree,
    the Made, and the records but by rn's scripts, as the people never see what the maker meant."""
    b = w.bench(str(tmp_path))
    versioned = w.deliverable(VERSIONED, "invoicer/__init__.py")
    versioned["necessary_conditions"][0]["decisions"] = [SAME_VERSION]
    started = planned_run(b, w.plan(versioned))
    signed_off(b, started)
    worktree, cut = started["worktree"], w.cut_of(start_text(b, started))
    with open(os.path.join(worktree, "invoicer", "__init__.py"), "a", encoding="utf-8") as f:
        f.write('\n__version__ = "1.4.0"\n')
    tree_py(b, "commit", cut["record"], "4", cwd=worktree)
    decided = [
        {"path": e["decision"]["path"], "where": cut["deliverable"]}
        for e in cut["cut"]["decisions"]
    ]
    made = {"decisions": decided, "more": [], "settled": []}
    with open(os.path.join(worktree, cut["made"]), "w", encoding="utf-8") as f:
        json.dump(made, f)
    tree_py(b, "commit", cut["record"], "6", cwd=worktree)
    text = start_text(b, started, "evaluator")
    judged = w.cut_of(text)
    claude(b, worktree, text, "rn:evaluator")
    with open(os.path.join(worktree, judged["answers"]), encoding="utf-8") as f:
        answers = json.load(f)
    answered = {each["question"] for each in answers["good"] + answers["more"]}
    assert answered == set(judged["conditions"])
    assert not opened_of_the_maker(b)


def opened_of_the_maker(b: w.Bench) -> list[str]:
    """Each call of a run on the bench that opens the design tree, a Made, or a record but by
    rn's own scripts: a read by a tool, or a part of a Bash command, its variables filled in."""
    maker = ("design-tree.json", "made.json", "/records/")
    found = []
    for name, given in calls(b):
        if name in ("Read", "Grep", "Glob"):
            parts = [json.dumps(given)]
        elif name == "Bash":
            parts = command_parts(str(given.get("command", "")))
        else:
            continue
        found += [p for p in parts if any(m in p for m in maker)]
    return found


def command_parts(command: str) -> list[str]:
    """Each part of a Bash command that runs a program other than rn's record.py and tree.py, each
    variable that an earlier part sets filled in."""
    values: dict[str, str] = {}
    parts = []
    for part in re.split(r"&&|\|\||;|\||\n", command):
        part = part.strip()
        set_here = re.fullmatch(r"(\w+)=(\S+)", part)
        if set_here:
            values[set_here[1]] = set_here[2].strip("'\"")
            continue
        for key, value in values.items():
            part = part.replace(f"${key}", value).replace(f"${{{key}}}", value)
        if part and not re.search(r"(record|tree)\.py\b", part):
            parts.append(part)
    return parts
