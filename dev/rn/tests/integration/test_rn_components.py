"""The integration cases of each component's decisions and of each handoff with its data, as rn's
architecture draws them under Components and Data model: the orchestrator's steps of each event,
the generator's and the evaluator's steps and checks, each Cut that the scripts write, the best
practice each role takes, and the starts due that rn gives Lane. Each runs rn and Lane through the
double of Claude Code and the double of gh, with a double of each prompt's work."""

from __future__ import annotations

import json
import os
import shutil

import pytest
import rn_files
from claude_code import Agent, Conversation
from gh import gh_double
from repo_files import git
from rn_bench import (
    NOT_BUILT,
    Bench,
    command_signed,
    confirmed,
    cut_of,
    ended,
    evaluator_started,
    marked,
    planned_tree,
    ran,
    read_step,
    requested,
    shared_steps,
    signed_plan,
    to_plan_signoff,
    trial_made,
)
from rn_files import COMMAND, GOAL, GUIDE, WORDS

pytestmark = pytest.mark.xfail(strict=True, reason=NOT_BUILT)


def at_make(b: Bench, c: Conversation, generator: Agent) -> None:
    """The generator reads its inputs and keeps its step `decide`, each item done."""
    read_step(b, c, generator, cut_of(c, generator))
    for each in rn_files.items_at(kind_of_cut(c, generator), "decide"):
        generator.bash(f"lane-item decide {each}")
    marked(c, "decide", generator)


def kind_of_cut(c: Conversation, agent: Agent) -> str:
    """The kind of the best practice that the agent's Cut names."""
    return os.path.basename(os.path.normpath(cut_of(c, agent)["best_practice"]))


def made_with(
    b: Bench, c: Conversation, generator: Agent, text: str, result: dict
) -> tuple[bool, str]:
    """The generator keeps each step, writing the text as its deliverable and the result in its
    Round, and ends with made; gives whether Lane stopped the end, and what it said."""
    given = cut_of(c, generator)
    at_make(b, c, generator)
    path = given["deliverable"]["path"]
    generator.write(os.path.join(b.worktree, path), text)
    for each in rn_files.items_at(kind_of_cut(c, generator), "make"):
        generator.bash(f"lane-item make {each}")
    marked(c, "make", generator)
    generator.write(os.path.join(c.cwd, given["round"], "generator.json"), json.dumps(result))
    marked(c, "try", generator)
    ran(c, b.script("repository", "checks", b.run, path), generator)
    generator.bash("lane-result made")
    marked(c, "check", generator)
    stopped, _ = generator.end("made")
    return stopped.blocked, stopped.said


# The orchestrator: each command an entry, and the steps of each event.


@pytest.mark.supports("orchestrator")
@pytest.mark.parametrize(
    ("prompt", "first"),
    [
        ("/rn:ty", "record"),
        ("/rn:dn", "stop"),
        ("/rn:gm the guide first", "review"),
        ("yes", "review"),
    ],
)
def test_each_event_in_a_run_loads_the_orchestrator_and_holds_its_turn_to_its_steps(
    b: Bench, prompt: str, first: str
):
    """Given a run whose plan is put up for the user's sign-off
    When the user types the event's prompt, and the orchestrator ends its turn at once
    Then a command's skill points to domain/orchestrator.md, and Lane stops the end, naming the
    event's first step"""
    c = to_plan_signoff(b)
    typed = c.type(prompt)
    if prompt.startswith("/"):
        assert "domain/orchestrator.md" in typed.output
    answer = c.stop("Done.")
    assert answer.blocked
    assert f"`{first}`" in answer.said


@pytest.mark.supports("orchestrator", "scripts")
def test_a_new_requests_turn_is_held_to_repository_py_new_first(b: Bench):
    """Given invoicer's repository with no run of rn
    When the user types /rn:up with the walkthrough's words, and the orchestrator runs git
    worktree add in place of repository.py new
    Then Lane stops the call at the step `start`"""
    c = b.converse()
    typed = c.type(f"/rn:up {WORDS}")
    assert "domain/orchestrator.md" in typed.output
    answer = c.bash(f"git worktree add .claude/worktrees/rn-{b.name()}")
    assert answer.blocked
    assert "`start`" in answer.said


@pytest.mark.supports("orchestrator", "scripts")
def test_the_orchestrators_move_pushes_only_by_repository_py(b: Bench):
    """Given a run whose goal the user confirmed, its review, touched, and commit done
    When the orchestrator runs git push at the step `move`
    Then Lane stops the call, as move runs only repository.py put-up and tree.py cut"""
    c = requested(b)
    c.type("yes")
    marked(c, "review")
    marked(c, "touched")
    ran(c, b.script("tree", "commit", b.run, "The goal."))
    marked(c, "commit")
    answer = c.bash(f"git -C {b.worktree} push origin HEAD")
    assert answer.blocked
    assert "`move`" in answer.said


# The generator: its steps, its Cut, and the checks of its end.


@pytest.mark.supports("generator", "Cut", "Best practice")
def test_the_generators_cut_holds_its_deliverables_node_inputs_and_best_practice(b: Bench):
    """Given a run whose plan the user signed off
    When the orchestrator writes the command's Cut and starts its generator
    Then the Cut holds the goal, the command's node as the tree holds it, the run's worktree, the
    path of invoicer's
    lines in the worktree as its one input, rn's light best practice, Round content-1, and no
    findings or good of an earlier Round"""
    c, generator = signed_plan(b)
    given = cut_of(c, generator)
    node = next(each for each in b.tree()["deliverables"] if each["path"] == COMMAND)
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert given["goal"] == GOAL
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


@pytest.mark.supports("generator", "Cut")
def test_a_generators_read_marked_before_its_cut_is_read_whole_is_stopped(b: Bench):
    """Given a run whose command's generator started
    When it reports `read` done before reading its Cut
    Then Lane stops the mark, naming the Cut's path"""
    _c, generator = signed_plan(b)
    answer = generator.bash("lane-step read")
    assert answer.blocked
    assert generator.start_use["tool_input"]["prompt"] in answer.said


@pytest.mark.supports("generator")
def test_the_generators_make_writes_only_its_deliverables_paths(b: Bench):
    """Given a run whose command's generator decided
    When it writes invoicer's README at the step `make`
    Then Lane stops the write, naming the command's path as what the step writes"""
    c, generator = signed_plan(b)
    at_make(b, c, generator)
    answer = generator.write(os.path.join(b.worktree, "README.md"), "# invoicer\n")
    assert answer.blocked
    assert COMMAND in answer.said


@pytest.mark.supports("generator", "Round")
def test_a_generators_good_of_a_condition_its_deliverable_lacks_is_stopped(b: Bench):
    """Given a run whose command's generator kept each step
    When it ends with made, its result naming good a condition N9 that light doesn't hold
    Then Lane stops the end with check.py's fault naming N9"""
    c, generator = signed_plan(b)
    text = "print('invoice')\n"
    blocked, said = made_with(
        b, c, generator, text, rn_files.made([("N9", ["print('invoice')"])], [COMMAND])
    )
    assert blocked
    assert "N9" in said


@pytest.mark.supports("generator", "Round")
def test_a_generators_good_quoting_a_line_no_file_holds_is_stopped(b: Bench):
    """Given a run whose command's generator kept each step
    When it ends with made, its good of N1 quoting a line that the command doesn't hold
    Then Lane stops the end with check.py's fault naming the line"""
    c, generator = signed_plan(b)
    blocked, said = made_with(
        b,
        c,
        generator,
        "print('invoice')\n",
        rn_files.made([("N1", ["print('receipt')"])], [COMMAND]),
    )
    assert blocked
    assert "print('receipt')" in said


@pytest.mark.supports("generator", "Best practice")
def test_a_generators_end_with_its_deliverable_off_its_template_is_held(b: Bench):
    """Given a run whose guide's generator, of the kind readme, kept each step
    When it ends with made, the guide holding none of the readme template's sections
    Then Lane stops the end with the template check's places, each `docs/guide.md:<line>: ...`"""
    c, generator = command_signed(b)
    text = "# Print an invoice\n\nSave the lines as lines.csv, and type the command.\n"
    blocked, said = made_with(
        b, c, generator, text, rn_files.made([("N1", ["# Print an invoice"])], [GUIDE])
    )
    assert blocked
    assert f"{GUIDE}:" in said


@pytest.mark.supports("generator", "scripts")
def test_the_generators_checks_give_the_repositorys_commit_check_findings(b: Bench):
    """Given invoicer's repository with a pre-commit hook that refuses each commit, saying
    `invoicer/__main__.py: no tests`, and a run whose command's generator wrote the command
    When it runs repository.py checks on the command
    Then it gives 1 with the hook's line, and the repository's own index is as it was"""
    hook = os.path.join(b.repo, ".git", "hooks", "pre-commit")
    with open(hook, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\necho 'invoicer/__main__.py: no tests'\nexit 1\n")
    os.chmod(hook, 0o755)
    c, generator = signed_plan(b)
    at_make(b, c, generator)
    generator.write(os.path.join(b.worktree, COMMAND), "print('invoice')\n")
    found = c.bash(b.script("repository", "checks", b.run, COMMAND), generator)
    assert found.exit_code == 1
    assert "invoicer/__main__.py: no tests" in found.output
    assert git(b.repo, "diff", "--cached", "--name-only").strip() == ""


# The evaluator: its Cut, and what its steps never read or write.


@pytest.mark.supports("evaluator", "Cut", "Best practice")
def test_the_evaluators_cut_holds_only_what_the_people_have(b: Bench):
    """Given a run whose command's generator made Round content-1
    When the orchestrator writes the evaluator's Cut and starts it
    Then the Cut holds the goal, the command's name and path, what light's best practice judges
    by, the run's worktree, Round content-1, and the people's folder, and none of the command's
    decisions"""
    c, evaluator = evaluator_started(b)
    given = cut_of(c, evaluator)
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    assert sorted(given) == ["deliverable", "goal", "judges_by", "round", "trial", "worktree"]
    assert given["goal"] == GOAL
    assert given["deliverable"] == {"name": rn_files.COMMAND_NAME, "path": COMMAND}
    assert given["judges_by"] == rn_files.judged_by("light")
    assert os.path.normpath(os.path.join(b.repo, given["worktree"])) == b.worktree
    assert os.path.normpath(os.path.join(b.repo, given["round"])) == first
    assert os.path.isabs(given["trial"])


@pytest.mark.supports("evaluator", "Round")
def test_the_evaluator_reading_the_generators_result_is_stopped(b: Bench):
    """Given a run whose command's evaluator started
    When it reads the generator's result in its Round
    Then Lane stops the read"""
    _c, evaluator = evaluator_started(b)
    first = rn_files.round_of(b.folder, COMMAND, "content", 1)
    answer = evaluator.read(os.path.join(first, "generator.json"))
    assert answer.blocked
    assert "generator.json" in answer.said


@pytest.mark.supports("evaluator")
def test_the_evaluators_try_writes_only_in_the_peoples_folder(b: Bench):
    """Given a run whose command's evaluator made the people's folder
    When it writes a file in the run's worktree at the step `try`
    Then Lane stops the write, naming the people's folder as what the step writes"""
    c, evaluator, _, trial = trial_made(b)
    marked(c, "start", evaluator)
    answer = evaluator.write(os.path.join(b.worktree, "lines.csv"), "Hosting;40.00;1\n")
    assert answer.blocked
    assert os.path.basename(os.path.normpath(trial)) in answer.said


# The scripts: the best practice each role takes, and rn's order given to Lane.


@pytest.mark.supports("scripts", "Best practice")
def test_a_runs_own_best_practice_is_taken_before_rns(b: Bench):
    """Given a run whose worktree holds its own best practice of the kind light, at
    .rn/best-practices/light/, and whose plan the user signed off
    When the orchestrator writes the command's Cut
    Then the Cut's best practice is the run's own folder"""
    c = to_plan_signoff(b)
    own = os.path.join(b.worktree, ".rn", "best-practices", "light")
    shutil.copytree(os.path.join(b.rn, "domain", "best-practices", "light"), own)
    c.type("/rn:ty")
    ran(c, b.script("tree", "signoff", b.run))
    marked(c, "record")
    cut_path = shared_steps(
        b, c, ground="Signed off.", moves=[b.script("tree", "cut", b.run, "generator", COMMAND)]
    )[0].strip()
    ended(c, "Making it.")
    given = rn_files.read_json(os.path.join(b.repo, cut_path))
    assert os.path.normpath(os.path.join(b.repo, given["best_practice"])) == own


@pytest.mark.supports("scripts", "Design tree")
def test_a_deliverable_waits_while_one_it_rests_on_is_being_made(b: Bench):
    """Given a run whose command's evaluator runs, the guide resting on the command
    When the orchestrator starts a generator for the guide
    Then a start of a second rn:generator is stopped as not due"""
    c, _ = evaluator_started(b)
    answer, agent = c.start("rn:generator", "Make the guide.", "Run rn:generator")
    assert agent is None
    assert "No start of rn's subagents is due now." in answer.said


@pytest.mark.supports("scripts", "Design tree")
def test_a_put_up_without_a_login_of_gh_is_refused_before_any_push(b: Bench):
    """Given a run whose plan has each condition good, and gh with no login
    When the orchestrator puts the plan up by repository.py put-up
    Then it gives 1 with what gh auth status said, gh was asked nothing after it, and the remote
    holds no branch of the run"""
    c = requested(b)
    confirmed(b, c)
    c.type(rn_files.TAX_ANSWER)
    shared_steps(b, c, planned_tree(b, answered=True), "The user's answer.")
    gh_double.logged_out(b.gh)
    refused = c.bash(b.script("repository", "put-up", b.run, rn_files.plan_path(b.name())))
    assert refused.exit_code == 1
    assert "You are not logged into any GitHub hosts." in refused.output
    assert [each[:3] for each in b.asked_gh()] == [["gh", "auth", "status"]]
    assert f"rn-{b.name()}" not in git(b.origin, "branch", "--list").split()
