"""The unit cases of the evaluator's prompt, domain/evaluator.md, on Opus: a deliverable its people
can use, which it judges good, and one they can't, which it answers more with what would make it
good; each run three times, each decided by code from the answers the run leaves. Run by the
developer on the model, as rn's Test strategy says; check.sh never runs them."""

from __future__ import annotations

import os
import tempfile
from urllib.parse import quote

import opus
import pytest
import rn_files
from repo_files import write_files
from rn_files import COMMAND
from rn_prompts import NOT_BUILT, RUNS, Room, as_role, evaluator_cut, result_of, run_of

pytestmark = [opus.NEEDS_LOGIN, pytest.mark.xfail(strict=True, reason=NOT_BUILT)]

NAME = "20261120-a-command-with-which-the"
WORKS = (
    "import sys\n"
    "from decimal import Decimal\n\n"
    "from invoicer.lines import parse_lines\n\n"
    "lines = parse_lines(open(sys.argv[1], encoding='utf-8').read())\n"
    "rate = Decimal(sys.argv[sys.argv.index('--rate') + 1])\n"
    "subtotal = sum(each.amount() for each in lines)\n"
    "for each in lines:\n"
    "    print(f'{each.description:<30}{each.amount():>10.2f} EUR')\n"
    "print(f'{\"Subtotal\":<30}{subtotal:>10.2f} EUR')\n"
    "print(f'{\"Tax\":<30}{subtotal * rate:>10.2f} EUR')\n"
    "print(f'{\"Total\":<30}{subtotal * (1 + rate):>10.2f} EUR')\n"
)
BROKEN = "import sys\n\nprint('Usage: invoicer <lines>')\nsys.exit(2)\n"


def judging(room: Room, command: str) -> tuple[str, list[str]]:
    """The run's worktree holding the command as given, and the evaluator's Cut of its Round
    content-1; gives the Cut's path and the IDs of light's conditions."""
    node = rn_files.open_node(rn_files.COMMAND_NAME, COMMAND, "light", ["invoicer/lines.py"])
    run_of(room, NAME, node)
    write_files(room.worktree(NAME), {COMMAND: command})
    trial = os.path.join(
        tempfile.gettempdir(), f"rn-trial-{NAME}-{quote(COMMAND, safe='')}-content-1"
    )
    return evaluator_cut(room, NAME, node, trial), rn_files.conditions("light")


@pytest.mark.supports(
    "test_an_evaluator_started_reads_only_its_cut_and_tries_in_the_peoples_folder"
)
@pytest.mark.parametrize("run", RUNS)
def test_a_command_its_people_can_use_is_judged_good(room: Room, run: int):
    """Given the evaluator's Cut of a command that prints the walkthrough's invoice
    When the evaluator runs on it
    Then its answers are judged, each of light's conditions answered once, N1 good, and each line
    it quotes stands in the command"""
    cut_path, ids = judging(room, WORKS)
    as_role(room, "evaluator", cut_path)
    result = result_of(room, cut_path, "evaluator")
    answered = [each["condition"] for each in result["good"] + result["more"]]
    assert result["result"] == "judged"
    assert sorted(answered) == sorted(ids)
    assert "N1" in [each["condition"] for each in result["good"]]
    assert all(line in WORKS for each in result["good"] for line in each["lines"])


@pytest.mark.supports("test_an_evaluators_end_leaving_a_condition_unanswered_is_stopped")
@pytest.mark.parametrize("run", RUNS)
def test_a_command_its_people_cannot_use_gets_more_with_what_would_make_it_good(
    room: Room, run: int
):
    """Given the evaluator's Cut of a command that prints only its usage, whatever lines it's given
    When the evaluator runs on it
    Then its answers hold N1 in more, with words of what would make it good, and not in good"""
    cut_path, _ = judging(room, BROKEN)
    as_role(room, "evaluator", cut_path)
    result = result_of(room, cut_path, "evaluator")
    more = {each["condition"]: each["good_when"] for each in result["more"]}
    assert more.get("N1", "").strip()
    assert "N1" not in [each["condition"] for each in result["good"]]
