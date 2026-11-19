"""The integration cases of each component of rn's architecture and each data it hands on: each
decision that a component's Strategies give it, and each handoff with the data that Data model
names, on the bench of the README's walkthrough through the double of Claude Code."""

from __future__ import annotations

import os

import pytest
from rn_bench import COMMAND, GUIDE, RN, Bench, command_done, decided, judged, made, read_json

# Why a case is xfail where its premise is gone.
GONE_NONE = (
    "Lane takes the starts due in its own form, so start.py's none, which the case asks, is gone"
)


def judge_all(b: Bench, more: dict[str, str]) -> list[str]:
    """Each evaluator due judges, more on each condition named, and gives each group judged."""
    return [group for group, _ in judged(b, more)]


@pytest.mark.supports("orchestrator")
def test_the_main_conversation_is_the_orchestrator(b: Bench):
    """Given rn's plugin
    When the person types /rn:up with a request
    Then the main conversation reads the orchestrator's part, and rn holds no agent of an
    orchestrator, as the main conversation leads the run"""
    answer = b.converse().type("/rn:up a command that prints an invoice from its lines")
    assert "domain/orchestrator.md" in answer.output
    assert sorted(os.listdir(os.path.join(RN, "agents"))) == ["evaluator.md", "generator.md"]


@pytest.mark.xfail(strict=True, reason=GONE_NONE)
@pytest.mark.supports("generator")
def test_one_generator_runs_for_each_deliverable(b: Bench):
    """Given the command's generator running
    When Lane asks rn's adapter of the starts due for another generator's start, beside it
    Then none is due, as the guide's input, the command, isn't done"""
    cut = b.cut("generator")
    running = [{"kind": "start", "role": "rn:generator", "prompt": f"Your Cut is at {cut}"}]
    code, printed, _ = b.due(moves=running)
    assert (code, list(printed)) == (0, ["none"])


@pytest.mark.supports("evaluator")
def test_a_later_round_judges_only_the_groups_whose_decisions_changed(b: Bench):
    """Given round 1 of the command judged with more on N2, and a decision under N2 changed
    When round 2's generator ends and the orchestrator runs rn's script of each evaluator's Cut
    Then only the group C1, which holds N2, is judged"""
    made(b)
    assert judge_all(b, {"N2": "The team sees a wrong line named"}) == ["C1", "C2", "C3"]
    decided(
        b,
        1,
        {"about": "A wrong line", "decided": "named by its number", "by": "reasoning"},
        "A wrong line named by its number",
    )
    made(b)
    assert judge_all(b, {}) == ["C1"]


@pytest.mark.supports("Design tree")
def test_an_item_of_work_before_an_input_not_done_is_refused(b: Bench):
    """Given the orchestrator's edit that puts the guide first in the work, before the command it
    takes as input
    When it runs tree.py commit
    Then it gives 1 naming the guide and the command"""
    tree = b.tree()
    tree["work"].reverse()
    b.write_tree(tree)
    answer = b.commit(b.converse(), "The guide first")
    assert answer.exit_code == 1
    assert GUIDE in answer.output and COMMAND in answer.output


@pytest.mark.supports("Design tree")
def test_a_deliverable_done_with_a_condition_not_good_is_refused(b: Bench):
    """Given the orchestrator's edit that marks the command done while N1 isn't good, as a node
    with no file, which keeps its conditions once done
    When it runs tree.py commit
    Then it gives 1 naming the command"""
    tree = b.tree()
    node = tree["deliverables"][0]
    node.update(status="done", file=False)
    node.pop("inputs")
    b.write_tree(tree)
    answer = b.commit(b.converse(), "The command done")
    assert answer.exit_code == 1
    assert COMMAND in answer.output


@pytest.mark.supports("Design tree")
def test_a_deliverable_whose_inputs_leave_out_a_kind_its_best_practice_takes_is_refused(b: Bench):
    """Given the orchestrator's edit that takes docs/test-design.md out of the command's inputs
    When it runs tree.py commit
    Then it gives 1 naming the command and the kind test-design"""
    tree = b.tree()
    tree["deliverables"][0]["inputs"].remove("docs/test-design.md")
    b.write_tree(tree)
    answer = b.commit(b.converse(), "Fewer inputs")
    assert answer.exit_code == 1
    assert COMMAND in answer.output and "test-design" in answer.output


@pytest.mark.supports("Cut")
def test_each_cut_holds_its_role_deliverable_best_practice_and_goal(b: Bench):
    """Given the command made
    When the orchestrator runs rn's script of the generator's and an evaluator's Cut
    Then each Cut names its role, the command with its name and kind, the best practice its round
    works by, and the goal"""
    cuts = [made(b), b.cut("evaluator")]
    for cut, role in zip(cuts, ("generator", "evaluator")):
        written = read_json(b, cut)
        assert written["role"] == role
        assert written["deliverable"] == {
            "name": b.tree()["deliverables"][0]["name"],
            "path": COMMAND,
            "kind": "code",
        }
        assert (written["best_practice"], written["goal"]) == ("code", b.tree()["goal"]["decided"])


@pytest.mark.supports("Best practice")
def test_the_guides_rounds_work_by_the_readme_best_practice_and_its_groups(b: Bench):
    """Given the command done, and the guide next in the work
    When the guide's generator ends and the orchestrator runs rn's script of each evaluator's Cut
    Then the generator's Cut works by readme, and one evaluator judges each group of readme's
    conditions"""
    command_done(b)
    assert read_json(b, made(b))["best_practice"] == "readme"
    assert judge_all(b, {}) == ["C1", "C2", "C3", "C4"]


@pytest.mark.supports("Round")
def test_each_rounds_results_lie_beside_their_cuts(b: Bench):
    """Given round 1 of the command made and judged
    When the run's folder is read
    Then rounds/1/ holds the generator's and each evaluator's Cut, each with its result beside it"""
    made(b)
    judge_all(b, {})
    names = sorted(os.listdir(os.path.join(b.run, "rounds", "1")))
    assert names == [
        "evaluator-C1.cut.json",
        "evaluator-C1.json",
        "evaluator-C2.cut.json",
        "evaluator-C2.json",
        "evaluator-C3.cut.json",
        "evaluator-C3.json",
        "generator.cut.json",
        "generator.json",
    ]
