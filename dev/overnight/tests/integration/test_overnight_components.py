"""The integration cases of the decisions that a component of overnight's architecture makes alone,
where no sequence's path shows them: each command a skill that runs one script and shows what it
prints, and a runner's stop known by a lock that the OS releases however the runner ends."""

from __future__ import annotations

import os
import re
import subprocess
import sys

import pytest
from overnight_bench import PLUGIN, QUEUE_PY, UNNAMED, Detached, end_group, stacked_review, until

pytestmark = pytest.mark.xfail(strict=True, reason="overnight's parts are not built yet")


def skill_command(skill: str, arguments: str) -> list[str]:
    """The command that the skill's `Gives:` names, `${CLAUDE_PLUGIN_ROOT}` given as overnight's
    folder and the skill's arguments in place of its slot."""
    with open(os.path.join(PLUGIN, "skills", skill, "SKILL.md"), encoding="utf-8") as f:
        named = re.search(r"`(python3 \$\{CLAUDE_PLUGIN_ROOT\}/scripts/queue.py [^`]*)`", f.read())
    assert named, f"the skill {skill} names no command of queue.py"
    words = named.group(1).replace("${CLAUDE_PLUGIN_ROOT}", PLUGIN).split(" ")
    return [sys.executable, words[1], words[2], *arguments.split()]


@pytest.mark.supports("commands", "S2")
def test_each_skill_runs_its_script_and_shows_what_it_prints(d: Detached):
    """Given overnight's folder, and a queue file whose task's prompt isn't there
    When `/overnight:check` runs its command with no queue file, and `/overnight:stack` runs its
    command with the queue file
    Then the check gives 0 with overnight's version and what to name, and the stack gives 1 naming
    the prompt's file, each as the script prints it"""
    os.makedirs(d.path("work"))
    task = {"name": "review", "prompt": "review.md", "dir": d.path("work")}
    queue_file = d.queue({"tasks": [task]}, d.path("tonight.json"))

    checked = subprocess.run(
        skill_command("check", ""), cwd=d.home, capture_output=True, text=True, check=False
    )
    stacked = subprocess.run(
        skill_command("stack", queue_file), cwd=d.home, capture_output=True, text=True, check=False
    )

    assert (checked.returncode, checked.stdout.rstrip("\n")) == (0, UNNAMED)
    assert stacked.returncode == 1
    assert d.path("review.md") in stacked.stdout + stacked.stderr


@pytest.mark.supports("record", "runner", "Run")
def test_a_runner_killed_mid_task_leaves_the_task_given_up_at_the_next_check(d: Detached):
    """Given a runner of a queue of one review, killed with no time to mark anything while the
    review's session runs
    When the user checks the queue
    Then the review is given up with why, and the check shows that why"""
    from runner import handoff

    given = stacked_review(d, 60)
    runner = subprocess.Popen(
        [sys.executable, QUEUE_PY, "run"],
        stdin=subprocess.PIPE,
        env=d.env(),
        text=True,
        start_new_session=True,
    )
    assert runner.stdin is not None
    runner.stdin.write(handoff.encode(given))
    runner.stdin.close()

    def running() -> bool:
        return d.runs(d.path("tonight"))[0]["run"]["state"] == "running"

    assert until(running, 30)
    end_group(runner.pid)
    runner.wait(timeout=30)
    checked = subprocess.run(
        [sys.executable, QUEUE_PY, "check", given.queue_file],
        capture_output=True,
        text=True,
        check=False,
    )

    run = d.runs(d.path("tonight"))[0]["run"]
    assert run["state"] == "given up" and run["why"]
    assert checked.returncode == 0 and run["why"] in checked.stdout
