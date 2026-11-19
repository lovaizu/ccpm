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
    """Given the command's generator's Cut of round 1
    When the generator runs alone with it
    Then it writes the command and its result made, with a place for each decision of its Cut"""
    b = rn_bench.bench(str(tmp_path))
    cut = b.cut("generator")
    run(b, str(tmp_path), f"Use the rn:generator agent with its Cut {cut}, and wait for it to end")
    written = result(b, cut)
    assert written["result"] == "made", each
    assert {d["about"] for d in written["carried_out"]} == {"The tax rate", "The lines"}
    assert os.path.exists(os.path.join(b.repo, COMMAND))


@pytest.mark.supports(
    "test_an_evaluators_result_that_answers_each_condition_of_its_group_passes_its_check"
)
@pytest.mark.parametrize("each", range(RUNS))
def test_the_evaluator_answers_each_condition_of_its_group(tmp_path: Any, each: int):
    """Given the command made, and an evaluator's Cut of the group C1
    When the evaluator runs alone with it
    Then it answers N1, N2, and N3 each once, good with its lines or more with its good_when"""
    b = rn_bench.bench(str(tmp_path))
    rn_bench.made(b)
    cut = b.cut("evaluator")
    run(b, str(tmp_path), f"Use the rn:evaluator agent with its Cut {cut}, and wait for it to end")
    written = result(b, cut)
    answered = [a["condition"] for a in written["good"] + written["more"]]
    assert sorted(answered) == ["N1", "N2", "N3"], each
