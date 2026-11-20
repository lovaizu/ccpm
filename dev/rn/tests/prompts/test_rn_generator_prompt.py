"""The unit cases of the generator's prompt, domain/generator.md, on Opus: a Cut whose points are
each settled, where it makes the deliverable, one whose point only the user can settle, where it
gives the point and makes nothing, and one with the last evaluator's findings, where it mends the
condition short; each run three times, each decided by code from the files the run leaves. Run by
the developer on the model, as rn's Test strategy says; check.sh never runs them."""

from __future__ import annotations

import os
import subprocess

import opus
import pytest
import rn_files
from repo_files import write_files
from rn_files import COMMAND
from rn_prompts import RUNS, Room, as_role, generator_cut, result_of, run_of

pytestmark = [opus.NEEDS_LOGIN]

NAME = "20261120-a-command-with-which-the"
TAX = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
LINES = "Hosting;40.00;1\nSupport hours;120.00;1\n"
# The command its people run, as the README's walkthrough shows it, which the case runs too.
RUN = ["python3", "-m", "invoicer", "lines.csv", "--rate", "0.19"]
# The check of the command, as N1.2 of the light best practice reads it: the decision about
# `The check`, which names the command of the README's walkthrough and the rate's form.
CHECK = rn_files.decision(
    "The check",
    f"The accountant saves the invoice's lines as lines.csv, runs `{' '.join(RUN)}` at the"
    " worktree's top, and reads the invoice it prints. The rate is a fraction, 0.19 for 19 %.",
    "reasoning",
)


def command_node(decisions: list) -> dict:
    """The command's node, of the kind light, with the decision about its check and the decisions
    given, each of its N1."""
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
    return rn_files.decided(node, {"N1": [CHECK, *decisions]})


def started_on(room: Room, node: dict, findings: object = None) -> str:
    """The run's worktree with its design tree holding the node, and the generator's Cut of the
    node's Round content-1; gives the Cut's path."""
    run_of(room, NAME, node)
    return generator_cut(room, NAME, node, findings)


def prints(room: Room, lines: str) -> subprocess.CompletedProcess[str]:
    """Runs the command in the run's worktree on a file of the lines, as its people do."""
    worktree = room.worktree(NAME)
    write_files(worktree, {"lines.csv": lines})
    return subprocess.run(
        RUN,
        cwd=worktree,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.supports("test_a_generators_made_makes_the_evaluator_due_in_the_same_round")
@pytest.mark.parametrize("run", RUNS)
def test_a_cut_with_each_point_settled_is_made_and_tried(room: Room, run: int):
    """Given the command's Cut, its tax rate given with each invoice by user
    When the generator runs on it
    Then its result is made, naming the command among its files, each line of its good stands in
    the command, and the command prints an invoice from the walkthrough's lines"""
    cut_path = started_on(room, command_node([TAX]))
    as_role(room, "generator", cut_path)
    result = result_of(room, cut_path, "generator")
    assert result["result"] == "made"
    assert COMMAND in result["files"]
    with open(os.path.join(room.worktree(NAME), COMMAND), encoding="utf-8") as f:
        text = f.read()
    assert all(line in text for each in result["good"] for line in each["lines"])
    assert prints(room, LINES).returncode == 0


@pytest.mark.supports("test_a_generators_point_reaches_the_user_and_their_answer_resumes_it")
@pytest.mark.parametrize("run", RUNS)
def test_a_cut_whose_point_only_the_user_can_settle_gives_the_point(room: Room, run: int):
    """Given the command's Cut, whose decisions leave to the user which currency the accounting
    team prints in
    When the generator runs on it
    Then its result is point, its words naming the currency, and it writes no command"""
    currency = rn_files.decision(
        "the currency",
        "The accounting team prints in the currency that the user names, which they haven't yet.",
        "reasoning",
    )
    cut_path = started_on(room, command_node([TAX, currency]))
    as_role(room, "generator", cut_path)
    result = result_of(room, cut_path, "generator")
    assert result["result"] == "point"
    assert "currenc" in result["point"].lower()
    assert not os.path.exists(os.path.join(room.worktree(NAME), COMMAND))


@pytest.mark.supports("test_an_evaluators_findings_go_to_the_next_rounds_generator_as_given")
@pytest.mark.parametrize("run", RUNS)
def test_a_cut_with_a_finding_short_mends_its_condition(room: Room, run: int):
    """Given the command's Cut with the last evaluator's finding that N1 is short, as the
    accountant's lines saved with commas print no invoice, and the command of the last Round
    When the generator runs on it
    Then its result is made, and the command prints an invoice from lines with commas"""
    findings = {
        "good": [],
        "more": [
            {
                "condition": "N1",
                "good_when": "The accountant prints an invoice from lines.csv saved with commas.",
            }
        ],
    }
    cut_path = started_on(room, command_node([TAX]), findings=findings)
    write_files(room.worktree(NAME), {COMMAND: "import sys\nsys.exit(1)\n"})
    as_role(room, "generator", cut_path)
    assert result_of(room, cut_path, "generator")["result"] == "made"
    assert prints(room, LINES.replace(";", ",")).returncode == 0
