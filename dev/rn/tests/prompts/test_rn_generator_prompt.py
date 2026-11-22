"""The unit cases of the generator's prompt, domain/generator.md, on Opus: a Cut whose points are
each settled, where it makes the deliverable, one whose point only the user can settle, where it
gives the point and makes nothing, one with the last evaluator's findings, where it mends the
condition short, and two whose trial meets a shortfall, where it goes back to decide for one the
people meet and not for one they'd never meet; each run three times, each decided by code from the
files and the records the run leaves. Run by the developer on the model, as rn's Test strategy
says; check.sh never runs them."""

from __future__ import annotations

import os
import subprocess

import opus
import pytest
import rn_files
from repo_files import git, write_files
from rn_files import COMMAND
from rn_prompts import RUNS, Room, as_role, commands_of, generator_cut, result_of, run_of

pytestmark = [opus.NEEDS_LOGIN]

NAME = "20261120-a-command-with-which-the"
TAX = rn_files.decision(rn_files.TAX_ABOUT, rn_files.TAX_ANSWER, "user")
LINES = "Hosting;40.00;1\nSupport hours;120.00;1\n"
# The command its people run, as the bench's own request gives it, which the case runs too.
RUN = ["python3", "-m", "invoicer", "lines.csv", "--rate", "0.19"]
# The check of the command, as N1.2 of the light best practice reads it: the decision about
# `The check`, which names the command of the bench's own request and the rate's form.
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


# The accounting team's own files, as the repository holds them: what its spreadsheet exports for
# March, the file of a tool it dropped, and its note of both, which the command's Cut takes as an
# input.
NOTE = "docs/accounting.md"
MARCH = "samples/march.csv"
LEGACY = "samples/legacy.csv"
NOTE_TEXT = (
    "# How the accounting team keeps invoice lines\n\n"
    f"The team keeps each invoice's lines in its spreadsheet, and exports them as a file such as\n"
    f"`{MARCH}`, the lines of March, to print the invoice.\n\n"
    f"`{LEGACY}` comes from the tool that the team dropped in 2019. No one prints from it now.\n"
)
LEGACY_TEXT = "description,price,quantity\nHosting,40.00,1\n"
# The decision about how the command reads a file, as the orchestrator settled it.
READS = rn_files.decision(
    "How the command reads the file",
    "Read each line of the file as invoicer.parse_lines reads it, description;price;quantity.",
    "reasoning",
)


def with_the_teams_files(room: Room, march: str) -> dict:
    """Commits the team's files on main, March's export as given, and gives the command's node,
    resting on invoicer's lines and the team's note, with the decisions about its check, the tax
    rate, and how it reads a file."""
    write_files(room.repo, {NOTE: NOTE_TEXT, MARCH: march, LEGACY: LEGACY_TEXT})
    git(room.repo, "add", "-A")
    git(room.repo, "commit", "-q", "-m", "The accounting team's files.")
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py", NOTE])
    return rn_files.decided(node, {"N1": [CHECK, TAX, READS]})


def prints_march(room: Room) -> subprocess.CompletedProcess[str]:
    """Runs the command in the run's worktree on March's export, as the team does."""
    return subprocess.run(
        ["python3", "-m", "invoicer", MARCH, "--rate", "0.19"],
        cwd=room.worktree(NAME),
        capture_output=True,
        text=True,
        check=False,
    )


def went_back(room: Room) -> bool:
    """Whether the generator went back to decide by Lane's lane-back, as its record holds it."""
    return any("lane-back decide" in each for each in commands_of(room))


@pytest.mark.supports(
    "test_a_generator_whose_trial_falls_short_goes_back_to_decide_and_makes_it_again"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_shortfall_the_people_meet_goes_back_to_decide(room: Room, run: int):
    """Given the command's Cut, deciding that it reads each line as invoicer does, while the
    team's March export, which its note names, holds a header row first
    When the generator runs on it
    Then it goes back to decide by lane-back, its result is made, and the command prints an
    invoice from March's export"""
    node = with_the_teams_files(
        room, "Description;Price;Quantity\nHosting;40.00;1\nSupport hours;120.00;1\n"
    )
    cut_path = started_on(room, node)
    as_role(room, "generator", cut_path)
    assert went_back(room)
    assert result_of(room, cut_path, "generator")["result"] == "made"
    assert prints_march(room).returncode == 0


@pytest.mark.supports(
    "test_a_generator_whose_trial_falls_short_goes_back_to_decide_and_makes_it_again"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_shortfall_the_people_would_never_meet_doesnt_go_back(room: Room, run: int):
    """Given the command's Cut, deciding that it reads each line as invoicer does, as the team's
    March export holds its lines, while the file of the tool the team dropped, which its note
    names, holds commas and a header row
    When the generator runs on it
    Then it doesn't go back by lane-back, its result is made, and the command prints an invoice
    from March's export"""
    node = with_the_teams_files(room, LINES)
    cut_path = started_on(room, node)
    as_role(room, "generator", cut_path)
    assert not any("lane-back" in each for each in commands_of(room))
    assert result_of(room, cut_path, "generator")["result"] == "made"
    assert prints_march(room).returncode == 0
