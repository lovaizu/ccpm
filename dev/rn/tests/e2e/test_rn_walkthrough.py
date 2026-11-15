"""The E2E cases of rn: the README's walkthrough, type hints for invoicer, a library of five modules
that other teams call, asked for in the person's own words, each run by dev/scripts/e2e.py on the
real Claude Code on Opus, as rn's Test strategy says under Scenario testing, and rn installed by the
README's commands, as it says under Installation testing. Each run's records give the key results:
KR1.1 from each deliverable that the run handed over, judged on Opus with only what its people have,
the deliverable's name and the change on the work's branch, and KR1.2 from the time of the person's
first turn to the turn that shows the pull request ready, the person's own turns included. Runs are
added until one more moves no mean by a step: a percent of KR1.1's share, a minute of KR1.2's time.
They run on the developer's login, so a case without one is skipped, as opus.NEEDS_LOGIN says."""

from __future__ import annotations

import glob
import json
import os
import subprocess
from typing import Any

import pytest

from dev.tests import opus, scenario

pytestmark = [
    pytest.mark.xfail(strict=True, reason="rn's parts have empty bodies"),
    opus.NEEDS_LOGIN,
]

TEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "walkthrough.json")
READY = "The pull request is ready for your merge"
JUDGE = (
    "You are one of the people a deliverable is for, as its name says, and you have only what they"
    " have: its name and what it changed in the repository, given below. Judge whether you could"
    ' use it for what its name says you\'re after. Reply with JSON {"usable": <true or false>}.'
)


def handed_over(records: str) -> list[tuple[str, str]]:
    """Each deliverable that the run handed over, as its name and the change on the work's branch:
    each one done in the design tree that the branch's change holds."""
    found = []
    for path in glob.glob(os.path.join(records, "branches", "*.diff")):
        with open(path, encoding="utf-8") as f:
            diff = f.read()
        tree = design_tree_in(diff)
        for each in tree.get("deliverables", []) if tree else []:
            if each.get("status") == "done":
                found.append((each["name"], diff))
    return found


def design_tree_in(diff: str) -> dict[str, Any] | None:
    """The design tree that a branch's change adds, as its added lines give it."""
    lines, within = [], False
    for line in diff.splitlines():
        if line.startswith("+++ "):
            within = line.endswith("/design-tree.json")
        elif within and line.startswith("+"):
            lines.append(line[1:])
    return json.loads("\n".join(lines)) if lines else None


def usable(name: str, diff: str) -> bool:
    """Whether the deliverable's people could use it, judged on Opus from its name and change."""
    return bool(opus.judged(f"{JUDGE}\n\n{name}\n\n{diff}")["usable"])


@pytest.mark.supports("KR1.1")
def test_the_deliverables_handed_over_are_ones_their_people_can_use() -> None:
    """Given: invoicer, a library of five modules with no type hints, and rn and Lane loaded.
    When: the person, played by e2e.py's stand-in, asks rn for type hints across invoicer in their
    own words, answers, signs off, and stops once the pull request is ready.
    Then: the share of the deliverables handed over that their people couldn't use is measured, and
    every run hands over at least one."""

    def share() -> float:
        given = handed_over(scenario.e2e(TEST))
        assert given, "the run handed over no deliverable"
        return 100 * sum(1 for name, diff in given if not usable(name, diff)) / len(given)

    print(f"KR1.1: {scenario.until_steady(share, 1):.1f}% of the deliverables handed over unusable")


@pytest.mark.supports("KR1.2")
def test_the_pull_request_is_ready_soon_after_the_request() -> None:
    """Given: invoicer, a library of five modules with no type hints, and rn and Lane loaded.
    When: the person, played by e2e.py's stand-in, asks rn for type hints across invoicer and
    answers what it asks.
    Then: the time from their first turn to the turn that shows the pull request ready is measured,
    their own turns included, and such a turn comes."""

    def minutes() -> float:
        turns = scenario.jsonl(os.path.join(scenario.e2e(TEST), "turns.jsonl"))
        ready = [t for t in turns if READY in t.get("screen", "")]
        assert ready, "no turn showed the pull request ready"
        return (scenario.seconds(ready[0]["ended"]) - scenario.seconds(turns[0]["started"])) / 60

    print(f"KR1.2: {scenario.until_steady(minutes, 1):.1f} minutes")


@pytest.mark.supports("KR1.2")
def test_rn_installs_by_the_readmes_commands(tmp_path: Any) -> None:
    """Given: a fresh home, with no plugin installed.
    When: the person runs the README's two commands of Installation in a shell.
    Then: `claude plugin details rn@ccpm` shows rn with its skills up, dn, ty, and gm, and Lane
    installed beside it."""
    env = scenario.fresh_home(str(tmp_path))
    for command in ("claude plugin marketplace add lovaizu/ccpm", "claude plugin install rn@ccpm"):
        subprocess.run(command, shell=True, env=env, check=True, capture_output=True)
    shown = scenario.shell("claude plugin details rn@ccpm", env)
    assert all(skill in shown for skill in ("up", "dn", "ty", "gm"))
    listed = scenario.shell("claude plugin list", env)
    assert "lane" in listed
