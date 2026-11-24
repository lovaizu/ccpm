"""The integration cases of each principle item of rn's architecture: each where the scripts keep
it, as the orchestrator and each role run them, and each with the fixture `broken`, which takes the
part that holds the item out of the bench's copy of rn where TRACE_BROKEN is 1."""

from __future__ import annotations

import json
import os

import pytest
import rn_files
from repo_files import git
from rn_bench import (
    CHANGELOG,
    Bench,
    apart_tree,
    command_signed,
    cut_move,
    cut_of,
    denial,
    evaluated,
    evaluator_cut,
    generated,
    held,
    judged_command,
    next_round,
    pointed,
    pruned,
    put_up,
    refactor_made,
    refactored,
    requested,
    resulted,
    reviewed,
    sent_back,
    short_twice,
    signed,
    signed_apart,
    signed_plan,
    to_plan_signoff,
    tree_written,
    trial_made,
    wrote,
)
from rn_files import COMMAND, GUIDE

# P1: toward the people's aim.


@pytest.mark.supports("P1.1", "Design tree")
def test_a_tree_change_out_of_form_is_refused_at_its_commit(b: Bench, broken: None):
    """Given a run whose goal the orchestrator put, and a change of its design tree that gives the
    command a kind of no best practice
    When the orchestrator commits it by tree.py commit
    Then it gives 1 naming /deliverables/1/kind, and the work's branch holds no new commit"""
    requested(b)
    design_tree = rn_files.walkthrough_tree(b.name(), plan_done=False)
    design_tree["deliverables"][1]["kind"] = "no-such-kind"
    b.write_tree(design_tree)
    b.ran("tree", "touched", b.run)
    branch = f"rn-{b.name()}"
    before = git(b.repo, "rev-parse", branch).strip()
    refused = b.script("tree", "commit", b.run, "The plan.")
    assert refused.code == 1
    assert "/deliverables/1/kind" in refused.err
    assert git(b.repo, "rev-parse", branch).strip() == before


@pytest.mark.supports("P1.2", "Round")
def test_a_deliverable_whose_point_waits_on_the_user_gets_no_cut(b: Bench, broken: None):
    """Given a run whose command's generator ended with a point, kept by the pruner as an open
    decision of N1
    When the orchestrator writes the generator's Cut
    Then tree.py cut gives 1 saying the command waits on the user"""
    pointed(b, signed_plan(b), "Should a line's quantity default to 1?")
    point = rn_files.decision("a line's quantity", None)
    reviewed(b, held(b, COMMAND, [], {"N1": [point]}), "The generator's point.")
    refused = b.script(*cut_move(b, "generator", COMMAND))
    assert refused.code == 1
    assert "user" in refused.err


@pytest.mark.supports("P1.3", "Design tree")
def test_a_signoff_of_the_plan_makes_its_deliverables_generator_due(b: Bench, broken: None):
    """Given a run whose plan is put up for the user's sign-off
    When the user types /rn:ty and the orchestrator records it by tree.py signoff
    Then the plan is done, and tree.py cut writes the command's generator's Cut"""
    to_plan_signoff(b)
    b.ran("tree", "signoff", b.run)
    assert b.tree()["deliverables"][0]["status"] == "done"
    cut_path = reviewed(b, ground="Signed off.", moves=[cut_move(b, "generator", COMMAND)])[0]
    assert os.path.isfile(os.path.join(b.repo, cut_path.strip()))


@pytest.mark.supports("P1.3", "Round")
def test_a_send_back_past_the_contents_limit_is_remade_in_rounds_of_its_own(b: Bench, broken: None):
    """Given a run whose command, of the kind light, the evaluator found short on N1 in Round
    content-1 and judged good in content-2, LIMIT Rounds, put up for the user's sign-off
    When the user types /rn:gm with what to change, and the orchestrator writes it as a decision
    by user of N1, holds N1 not good, and writes the generator's Cut
    Then the Cut lies in Round content-3, as the send-back gets Rounds of its own"""
    judged_command(b, {"N1": "The accountant prints an invoice with a comma in a line."})
    generated(b, next_round(b, COMMAND, ["N2", "N3"]))
    evaluated(b, next_round(b, COMMAND, ["N2", "N3"], "evaluator"))
    put_up(b, COMMAND, rn_files.conditions("light"))
    words = "print the total on its own last line"
    cut_path = sent_back(b, COMMAND, rn_files.conditions("light"), words)
    third = rn_files.round_of(b.folder, COMMAND, "content", 3)
    assert os.path.join(b.repo, cut_path) == os.path.join(third, "generator-cut.json")


# P2: judged by the people's aim.


@pytest.mark.supports("P2.1", "evaluator")
def test_the_people_start_from_the_branch_without_rns_folder(b: Bench, broken: None):
    """Given a run whose command's evaluator has its Cut, the command written but not committed
    When the evaluator runs repository.py trial for its Round
    Then the folder it prints is its Cut's trial, holding the command and invoicer's files, and
    no .rn"""
    cut_path = evaluator_cut(b)
    trial = trial_made(b, cut_path)
    given = cut_of(b, cut_path)
    assert trial == given["trial"] or os.path.samefile(trial, given["trial"])
    assert os.path.isfile(os.path.join(trial, COMMAND))
    assert os.path.isfile(os.path.join(trial, "invoicer", "lines.py"))
    assert not os.path.exists(os.path.join(trial, ".rn"))


@pytest.mark.supports("P2.2", "evaluator", "Round")
def test_an_evaluators_answers_leaving_a_condition_unanswered_are_refused(b: Bench, broken: None):
    """Given a run whose command's evaluator tried the command and wrote answers of N1 and N2 alone
    When it runs check.py evaluator before it ends
    Then check.py gives 1 naming N3"""
    cut_path = evaluator_cut(b)
    trial_made(b, cut_path)
    with open(os.path.join(b.worktree, COMMAND), encoding="utf-8") as f:
        first = f.read().splitlines()[0]
    resulted(b, cut_path, "evaluator", rn_files.judged([("N1", [first]), ("N2", [first])]))
    refused = b.script("check", "evaluator", cut_path)
    assert refused.code == 1
    assert "N3" in refused.out


@pytest.mark.supports("P2.3", "Design tree")
def test_the_pull_request_stays_a_draft_after_the_last_signoff(b: Bench, broken: None):
    """Given a run whose plan and command are done, and whose guide was judged good, refactored,
    and put up
    When the user signs the guide off, and the orchestrator records it, commits the change, and
    has the work checked whole
    Then gh was asked to open the pull request once, as a draft, and never to mark it ready"""
    refactored(b)
    signed(b)
    b.ran("repository", "diff", b.run)
    asked = b.asked_gh()
    created = [each for each in asked if each[1:3] == ["pr", "create"]]
    assert len(created) == 1 and "--draft" in created[0]
    assert [each for each in asked if each[1:3] == ["pr", "ready"]] == []


# P3: made the field's established way.


@pytest.mark.supports("P3.1", "evaluator", "Round")
def test_the_evaluator_waits_on_its_generators_result(b: Bench, broken: None):
    """Given a run whose command's generator has its Cut in Round content-1 and wrote no result yet
    When the orchestrator writes the evaluator's Cut of the command
    Then tree.py cut gives 1 saying the command waits on its generator, writing no evaluator's
    Cut, as judging starts once the making has ended"""
    signed_plan(b)
    refused = b.script(*cut_move(b, "evaluator", COMMAND))
    assert refused.code == 1
    assert "waits on its generator, not on its evaluator" in refused.err
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert not os.path.exists(os.path.join(first, "evaluator-cut.json"))


@pytest.mark.supports("P3.2", "generator", "Round")
def test_no_evaluator_is_due_after_a_refactor_round(b: Bench, broken: None):
    """Given a run whose guide, of the kind readme, the evaluator judged good on each condition in
    Round content-1, and whose new generator made Round refactor-2
    When the orchestrator holds each condition good, and writes the evaluator's Cut of the guide
    Then tree.py cut gives 1 saying the guide waits on the user's sign-off"""
    refactor_made(b)
    reviewed(b, held(b, GUIDE, rn_files.conditions("readme")), "Refactored.")
    refused = b.script(*cut_move(b, "evaluator", GUIDE))
    assert refused.code == 1
    assert "sign-off" in refused.err


@pytest.mark.supports("P3.3", "Round")
def test_a_deliverable_short_after_two_content_rounds_gets_no_third(b: Bench, broken: None):
    """Given a run whose command's N1 the evaluator found short in Rounds content-1 and content-2
    When the pruner holds N2 and N3 good, and the orchestrator writes the generator's Cut
    Then tree.py cut gives 1 saying the command waits on the pruner, to keep each finding left as
    an open decision"""
    short_twice(b)
    reviewed(b, held(b, COMMAND, ["N2", "N3"]), "The Round's findings.")
    refused = b.script(*cut_move(b, "generator", COMMAND))
    assert refused.code == 1
    assert "waits on the pruner, to keep each finding left as an open decision" in refused.err


# P4: each role on its own work.


@pytest.mark.supports("P4.1", "evaluator", "Cut", "Best practice")
def test_the_evaluators_cut_holds_only_what_the_people_have(b: Bench, broken: None):
    """Given a run whose command's generator made Round content-1
    When the orchestrator writes the evaluator's Cut
    Then the Cut holds the goal, the command's name and path, what light's best practice judges
    by, the run's worktree, Round content-1, and the people's folder, and none of the command's
    decisions"""
    given = cut_of(b, evaluator_cut(b))
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert sorted(given) == ["deliverable", "goal", "judges_by", "round", "trial", "worktree"]
    assert given["goal"] == rn_files.GOAL
    assert given["deliverable"] == {"name": rn_files.COMMAND_NAME, "path": COMMAND}
    assert given["judges_by"] == rn_files.judged_by("light")
    assert os.path.normpath(os.path.join(b.repo, given["worktree"])) == b.worktree
    assert os.path.normpath(os.path.join(b.repo, given["round"])) == first
    assert os.path.isabs(given["trial"])


@pytest.mark.supports("P4.2", "generator", "Round")
def test_a_generators_result_unwritten_is_refused(b: Bench, broken: None):
    """Given a run whose command's generator wrote the command but no result in its Round
    When it runs check.py generator before it ends
    Then check.py gives 1, naming the path of generator.json in the Round's folder"""
    cut_path = signed_plan(b)
    wrote(b, {COMMAND: "print('invoice')\n"})
    refused = b.script("check", "generator", cut_path)
    assert refused.code == 1
    assert os.path.join(cut_of(b, cut_path)["round"], "generator.json") in refused.out


@pytest.mark.supports("P4.3", "generator", "scripts")
def test_the_generators_checks_judge_its_files_alone_beside_another_staged(b: Bench, broken: None):
    """Given invoicer's repository with a pre-commit hook that refuses each commit of the guide,
    and a run whose worktree holds the guide staged, as another deliverable's, and whose command's
    generator wrote the command
    When it runs repository.py checks on the command
    Then it gives 0, and the worktree's index holds the guide alone, as it was"""
    hook = os.path.join(b.repo, ".git", "hooks", "pre-commit")
    with open(hook, "w", encoding="utf-8") as f:
        f.write(
            "#!/bin/sh\n"
            f"git diff --cached --name-only | grep -qx '{GUIDE}' || exit 0\n"
            f"echo '{GUIDE}: no title'\n"
            "exit 1\n"
        )
    os.chmod(hook, 0o755)
    signed_plan(b)
    wrote(b, {GUIDE: "guide\n"})
    git(b.worktree, "add", "--", GUIDE)
    wrote(b, {COMMAND: "print('invoice')\n"})
    found = b.script("repository", "checks", b.run, COMMAND)
    assert found.code == 0, found.out + found.err
    assert git(b.worktree, "diff", "--cached", "--name-only").split() == [GUIDE]


# P5: the shortest path.


@pytest.mark.supports("P5.2", "Design tree", "Cut")
def test_two_deliverables_resting_on_none_are_due_together(b: Bench, broken: None):
    """Given a run whose plan holds two deliverables that rest on none, the command and a
    changelog, put up for the user's sign-off
    When the user signs the plan off, and the orchestrator writes the generator's Cut of each
    Then tree.py cut writes both, each in Round content-1 of its own deliverable"""
    cuts = signed_apart(b, apart_tree(b), [COMMAND, CHANGELOG])
    assert [os.path.join(b.repo, each) for each in cuts] == [
        os.path.join(rn_files.round_of(b.folder, each, "content", 1), "generator-cut.json")
        for each in (COMMAND, CHANGELOG)
    ]


@pytest.mark.supports("P5.3", "Design tree")
def test_a_blocker_kept_for_the_user_leaves_the_other_deliverables_work_going_on(
    b: Bench, broken: None
):
    """Given a run whose plan holds the command and a changelog, each resting on none, the command
    keeping a refusal that only the user can mend as an open decision of its N1, put up for the
    user's sign-off
    When the user signs the plan off, and the orchestrator writes the changelog's Cut, then the
    command's
    Then tree.py cut writes the changelog's, and gives 1 for the command's, saying it waits on the
    user's answer"""
    blocker = rn_files.decision("a tool the repository's check needs", None)
    (cut_path,) = signed_apart(b, apart_tree(b, [blocker]), [CHANGELOG])
    assert os.path.isfile(os.path.join(b.repo, cut_path))
    refused = b.script(*cut_move(b, "generator", COMMAND))
    assert refused.code == 1
    assert "the user's answer" in refused.err


# P6: nothing lost on a stop.


@pytest.mark.supports("P6.1", "scripts", "Design tree")
def test_a_new_conversation_picks_up_the_run_from_its_files(b: Bench, broken: None):
    """Given a run whose plan is put up, paused by /rn:dn
    When the user types /rn:up in a new conversation, and the orchestrator runs
    repository.py find
    Then it prints the run's folder from the repository's top"""
    to_plan_signoff(b)
    b.ran("repository", "pause", b.run)
    assert b.ran("repository", "find").split() == [b.run]


# P7: only what the people can't reach their aim without.


@pytest.mark.supports("P7.1", "hook", "orchestrator", "Design tree")
@pytest.mark.parametrize("tool", ["Write", "Edit"])
def test_the_orchestrators_write_to_the_design_tree_is_denied_pointing_to_a_new_pruner(
    b: Bench, broken: None, tool: str
):
    """Given a run whose goal the pruner wrote and the orchestrator committed
    When the orchestrator, the main conversation, which names no agent, calls Write or Edit on the
    run's design tree, and Claude Code runs the hook
    Then the hook denies the call, its reason naming the tree and telling the writer to hand the
    fact to a new pruner, so that no fact enters the tree unweighed"""
    requested(b)
    reason = denial(b.script("hook", given=tree_written(b, None, tool)))
    assert reason is not None, "the orchestrator's write is denied"
    assert b.tree_path in reason
    assert "hand the fact you'd write to a new pruner" in reason


@pytest.mark.supports("P7.2", "pruner", "Design tree")
def test_a_done_deliverable_keeps_its_decisions_and_is_read_again_with_one_resting_on_it(
    b: Bench, broken: None
):
    """Given a run whose command, holding the user's answer about the tax rate in its N1, was
    judged good, put up, and signed off
    When a new pruner adds a changelog that rests on the command, and the orchestrator runs
    tree.py touched
    Then the command is done keeping its conditions, its N1 holding the user's answer, and
    tree.py touched lists the command among the nodes to weigh again"""
    command_signed(b)
    design_tree = b.tree()
    command = design_tree["deliverables"][1]
    tax = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
    assert command == rn_files.done_node(
        rn_files.COMMAND_NAME, COMMAND, "light", decisions={"N1": [tax]}
    )
    changelog = rn_files.open_node("The changes", CHANGELOG, "light", [COMMAND])
    design_tree["deliverables"].append(changelog)
    pruned(b, design_tree)
    assert "/deliverables/1" in b.ran("tree", "touched", b.run).split()


@pytest.mark.supports("P7.3", "hook", "scripts", "Design tree")
def test_a_makers_write_to_the_design_tree_is_denied_while_the_scripts_write_it(
    b: Bench, broken: None
):
    """Given a run whose plan is put up for the user's sign-off
    When rn's generator calls Write on the run's design tree, and Claude Code runs the hook; and
    then the user types /rn:ty, and the orchestrator records it by tree.py signoff
    Then the hook denies the generator's write, telling it to hand the fact on, and tree.py signoff
    writes the tree by Python, through no tool that the hook sees, the plan done"""
    to_plan_signoff(b)
    reason = denial(b.script("hook", given=tree_written(b, "rn:generator")))
    assert reason is not None, "the generator's write is denied"
    assert "hand the fact you'd write to a new pruner" in reason
    b.ran("tree", "signoff", b.run)
    assert b.tree()["deliverables"][0]["status"] == "done"


@pytest.mark.supports("P7.3", "S1", "generator", "Cut", "Round")
def test_the_generators_cut_holds_the_pruners_remedy_and_no_evaluators_finding(
    b: Bench, broken: None
):
    """Given a run whose command's evaluator judged Round content-1, N1 with more
    When the pruner writes the remedy that it keeps of the finding as a decision of N1, holds N2
    and N3 good and N1 not, and the orchestrator writes the generator's Cut
    Then the Cut lies in Round content-2, its deliverable holding the remedy in N1, its last_good
    the generator's good of content-1, and nothing of the evaluator's findings, so that the
    generator mends by the remedy that the pruner weighed alone"""
    finding = "The accountant prints an invoice with a comma in a line."
    judged_command(b, {"N1": finding})
    remedy = rn_files.decision("a comma in a line", "A line's comma is read as a decimal.", "maker")
    design_tree = held(b, COMMAND, ["N2", "N3"], {"N1": [remedy]})
    cut_path = reviewed(
        b, design_tree, "The Round's findings.", [cut_move(b, "generator", COMMAND)]
    )[0].strip()
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    second = rn_files.round_of(b.folder, COMMAND, "content", 2)
    assert os.path.join(b.repo, cut_path) == os.path.join(second, "generator-cut.json")
    given = cut_of(b, cut_path)
    assert remedy in given["deliverable"]["necessary_conditions"][0]["decisions"]
    made = rn_files.read_json(os.path.join(first, "generator.json"))
    assert given["last_good"] == made["good"]
    assert "findings" not in given
    assert finding not in json.dumps(given)
