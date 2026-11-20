"""The unit cases of rn's prompts on the model, as rn's Test strategy says: each prompt alone on
Opus by `claude -p`, on the bench of the README's walkthrough, each case run RUNS times, a run a
test of its own, each a case where the prompt's description says it acts and, for up, one where it
says it doesn't. Each decides by code what the run left in the run's folder. They run on the
developer's login, so a case without it is skipped, as opus.NEEDS_LOGIN says."""

from __future__ import annotations

import glob
import json
import os
from typing import Any

import opus
import pytest
import rn_bench
from repo_files import git
from rn_bench import COMMAND, RUN, Bench

pytestmark = [
    opus.NEEDS_LOGIN,
]

# The design tree of a run's folder.
TREE = "design-tree.json"
# The folder of the command's tests, which the command's generator writes beside the command.
TESTS = "tests/"
# The fields of each kind of report to Lane, in the order that its reporter prints them.
FIELDS = {"step": ["step"], "item": ["step", "item"], "result": ["result"]}
# The runs of each case, as rn's Test strategy sets.
RUNS = 3


def run(b: Bench, tmp: str, prompt: str) -> str:
    """Runs the prompt on Opus with rn and Lane loaded in the bench's repository, keeps the run's
    record in the case's folder as record.jsonl, printing its path, which pytest shows where the
    case fails, and gives the record."""
    env = dict(b.env, CLAUDE_CONFIG_DIR=os.path.join(tmp, "config"))
    flags = ["--plugin-dir", b.rn, "--plugin-dir", b.lane, "--output-format", "stream-json"]
    record = opus.prompted(prompt, b.repo, env, [*flags, "--verbose"], 900)
    path = os.path.join(tmp, "record.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        f.write(record)
    print(f"record: {path}")
    return record


def loaded(record: str) -> list[str]:
    """Each skill that the run called by the Skill tool."""
    events = [json.loads(line) for line in record.splitlines() if line.startswith("{")]
    return [
        part["input"]["skill"]
        for event in events
        if event.get("type") == "assistant"
        for part in event["message"].get("content", [])
        if part.get("type") == "tool_use" and part.get("name") == "Skill"
    ]


def reported(tmp: str) -> list[list[str]]:
    """Each report to Lane that the run's subagent made, in its order, as the reporter's words,
    such as `["lane-step", "1"]`, from the subagent's transcript in the case's configuration
    folder. A report is a Bash call whose output is the one line of JSON that a reporter prints,
    as Lane reads it back, whatever else the command holds, such as a `cd` before it."""
    pattern = os.path.join(tmp, "config", "projects", "*", "*", "subagents", "agent-*.jsonl")
    reports = []
    for path in sorted(glob.glob(pattern)):
        with open(path, encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.startswith("{")]
        bash = {
            part["id"]
            for event in events
            if event.get("type") == "assistant"
            for part in event["message"].get("content", [])
            if part.get("type") == "tool_use" and part.get("name") == "Bash"
        }
        reports += [
            report(part.get("content"))
            for event in events
            if event.get("type") == "user" and isinstance(event["message"].get("content"), list)
            for part in event["message"]["content"]
            if part.get("type") == "tool_result" and part.get("tool_use_id") in bash
        ]
    return [words for words in reports if words]


def report(output: Any) -> list[str]:
    """The reporter's words of a Bash call's output that is a report to Lane, such as
    `["lane-item", "3", "N1"]`; [] for any other output."""
    try:
        given = json.loads(output) if isinstance(output, str) else None
    except ValueError:
        return []
    if not isinstance(given, dict):
        return []
    fields = [key for key in given if key != "kind"]
    if fields != FIELDS.get(str(given.get("kind"))):
        return []
    return [f"lane-{given['kind']}", *(str(given[f]) for f in fields)]


def started(role: str, cut: str) -> str:
    """The prompt by which the case's main conversation starts the role with its Cut alone, passing
    on what a run may not do, as the role gets nothing of the main conversation's system prompt."""
    told = f"telling it: {opus.RULE}"
    return f"Use the rn:{role} agent with its Cut {cut}, {told} Wait for it to end."


def changed_beside(b: Bench, paths: tuple[str, ...]) -> list[str]:
    """Each file of the bench's repository that differs from its last commit, or that git doesn't
    know, beside the paths given, a path ending with `/` naming a folder, and beside the
    __pycache__ that running Python leaves, which invoicer's own repository would ignore."""
    lines = git(b.repo, "status", "--porcelain", "-uall").splitlines()
    files = [line[3:] for line in lines]
    return [f for f in files if not f.startswith(paths) and "/__pycache__/" not in f"/{f}"]


def result(b: Bench, cut: str) -> Any:
    """The result that the role wrote beside its Cut."""
    with open(os.path.join(b.repo, cut.removesuffix(".cut.json") + ".json"), encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
@pytest.mark.parametrize("each", range(RUNS))
def test_up_starts_a_run_for_a_request_in_words(tmp_path: Any, each: int):
    """Given invoicer with no run's folder
    When the person asks in words for a command with which the accounting team prints invoices
    Then the run calls rn:up, and commits in rn's worktree of the run a run's folder whose design
    tree states a goal"""
    b = rn_bench.bench(str(tmp_path))
    git(b.repo, "rm", "-r", "-q", RUN)
    git(b.repo, "commit", "-q", "-m", "No run")
    record = run(
        b, str(tmp_path), "rn, make a command with which our accounting team prints invoices"
    )
    assert "rn:up" in loaded(record)
    trees = glob.glob(os.path.join(b.repo, ".claude", "worktrees", "rn-*", ".rn", "*", TREE))
    assert len(trees) == 1, each
    worktree = os.path.dirname(os.path.dirname(os.path.dirname(trees[0])))
    committed = json.loads(git(worktree, "show", f"HEAD:{os.path.relpath(trees[0], worktree)}"))
    assert committed["goal"]["decided"]


@pytest.mark.supports("test_an_edit_of_the_design_tree_is_committed_with_its_ground")
@pytest.mark.parametrize("each", range(RUNS))
def test_up_stays_out_of_a_fix_of_one_line(tmp_path: Any, each: int):
    """Given invoicer
    When the person asks to fix the spelling of one word in docs/architecture.md
    Then the run calls no skill of rn's"""
    b = rn_bench.bench(str(tmp_path))
    record = run(b, str(tmp_path), "Fix the spelling of 'invocie' in docs/architecture.md")
    assert not [skill for skill in loaded(record) if skill.startswith("rn:")], each


@pytest.mark.supports("test_a_generators_result_that_carries_out_each_decision_passes_its_check")
@pytest.mark.parametrize("each", range(RUNS))
def test_the_generator_makes_the_command_from_its_cut(tmp_path: Any, each: int):
    """Given the command's generator's Cut of round 1, the command with its tests in tests/
    When the generator runs alone with it
    Then it writes the command and its result made, with a place for each decision of its Cut,
    changes no file but the command, its tests, and the run's folder, and reports to Lane each of
    its steps 1 to 4 done in their order, each practice of the code best practice taken while
    deciding as an item of step 2 and each taken while making as one of step 3, and the result
    made last"""
    b = rn_bench.bench(str(tmp_path))
    tree = b.tree()
    tree["deliverables"][0]["more_paths"] = [TESTS]
    b.write_tree(tree)
    cut = b.cut("generator")
    run(b, str(tmp_path), started("generator", cut))
    written = result(b, cut)
    assert written["result"] == "made", each
    assert {d["about"] for d in written["carried_out"]} == {"The tax rate", "The lines"}
    assert os.path.exists(os.path.join(b.repo, COMMAND))
    assert changed_beside(b, (COMMAND, TESTS, RUN + "/")) == []
    calls = reported(str(tmp_path))
    assert [w[1:] for w in calls if w[0] == "lane-step"] == [["1"], ["2"], ["3"], ["4"]]
    for step, at in (("2", "decide"), ("3", "make")):
        items = [w[2] for w in calls if w[0] == "lane-item" and w[1:2] == [step]]
        assert sorted(set(items)) == sorted(rn_bench.practices("code", at)), step
    assert calls[-1] == ["lane-result", "made"]


@pytest.mark.supports(
    "test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check"
)
@pytest.mark.parametrize("each", range(RUNS))
def test_the_evaluator_answers_each_condition_of_its_group(tmp_path: Any, each: int):
    """Given the command made, and an evaluator's Cut of the group C1
    When the evaluator runs alone with it
    Then it answers N1, N2, and N3 each once, good with its lines or more with its good_when,
    changes no file but those of the run's folder, leaving the command as it was made, and reports
    to Lane each of its steps 1 to 4 done in their order, each condition as an item of
    step 3, and the result judged last"""
    b = rn_bench.bench(str(tmp_path))
    rn_bench.made(b)
    cut = b.cut("evaluator")
    run(b, str(tmp_path), started("evaluator", cut))
    written = result(b, cut)
    answered = [a["condition"] for a in written["good"] + written["more"]]
    assert sorted(answered) == ["N1", "N2", "N3"], each
    assert changed_beside(b, (COMMAND, RUN + "/")) == []
    calls = reported(str(tmp_path))
    assert [w[1:] for w in calls if w[0] == "lane-step"] == [["1"], ["2"], ["3"], ["4"]]
    items = [w[2] for w in calls if w[0] == "lane-item" and w[1:2] == ["3"]]
    assert sorted(set(items)) == ["N1", "N2", "N3"]
    assert calls[-1] == ["lane-result", "judged"]
