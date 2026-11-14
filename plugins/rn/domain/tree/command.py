"""Decides tree.py's command line: which command each call names, what it takes, what it prints,
and the exit code by which a role reads its result: 0 where it did what it names, 1 with what's
wrong or what's missing, and 2 with why it couldn't run, or with the usage."""

from __future__ import annotations

from collections.abc import Mapping

USAGE = """\
usage: tree.py begin <words>
       tree.py runs
       tree.py cut <run> <role> [<deliverable> [<group>]]
       tree.py write <run> <design-tree.json> <ground>
       tree.py lack <run> <deliverable> <condition> <lack>
       tree.py place <run> <deliverable> <role> <step> [<group>]
       tree.py round <run> <deliverable>
       tree.py sign-off <run> <sign-off.json>
       tree.py approve
       tree.py send-back
       tree.py push <run>
       tree.py comments <run>
       tree.py pause <run>
       tree.py ready <run>
"""


def main(argv: list[str], environ: Mapping[str, str], cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `tree.py` with the arguments, from the folder `cwd`,
    where `<run>` is the run's folder from there, `.rn/<yyyymmdd>-<goal>`:

    - `begin <words>` makes the run's worktree on its branch from HEAD, and its folder there with
      `records/` and `rounds/`, commits it, and prints the worktree's path; 1 where the run
      exists.
    - `runs` prints `{"runs": [...]}`, each run left with its name, words, worktree, the name of
      each deliverable doing, each role's step, and what waits, as JSON.
    - `cut <run> <role> [<deliverable> [<group>]]` writes the role's Cut and prints its run values
      as one JSON line; 1 where the role, the deliverable, or the group isn't one there is.
    - `write <run> <design-tree.json> <ground>` takes the tree that the tree-keeper wrote, marks
      each deliverable whose turn has come doing, writes it as the run's design tree, commits it
      with the ground, and prints `{"changed", "touched", "doing"}` as JSON; 1 with each fault
      where the tree isn't in its form or its order, and the run's tree is left as it was.
    - `lack <run> <deliverable> <condition> <lack>` keeps the Lack kept for the next round; 1,
      naming the condition, where no decision that answers it changed since the round's Cut, as
      the next round would make it good by a fix beside the design.
    - `place <run> <deliverable> <role> <step> [<group>]` keeps the Place of the generator, or of
      the evaluator of the group, and commits its work.
    - `round <run> <deliverable>` prints the deliverable's last round as JSON: its number, what
      the generator made, each evaluator's Answers, and each Lack kept; 1 where the deliverable
      has no round.
    - `sign-off <run> <sign-off.json>` puts the Sign-off up, waiting; 1 where it isn't in its form.
    - `approve` and `send-back`, which only /rn:ty and /rn:gm run as they load, decide the first
      Sign-off that waits in the run of the worktree that holds `cwd`, and print what they
      decided; `approve` opens the issue of a lesson and prints its URL, `send-back` drops a
      lesson, and `send-back` of the pull request handed over marks it a draft again, while
      `approve` of it leaves the merge to the user; 1 where nothing waits.
    - `push <run>` pushes the run's branch and opens its draft pull request where it has none, and
      prints its URL; 1 with what's missing, such as gh's login, where it can't.
    - `comments <run>` prints each comment on the pull request since the Sign-off that the user
      last sent back was put up.
    - `pause <run>` commits each role's work so far and pushes it, and prints the run's words and
      where each role stood; 1 with `committed but not pushed` and what's missing where the push
      fails.
    - `ready <run>` marks the pull request ready, puts the pull request handed over up for the
      user's /rn:gm, and prints its URL; 1 where a deliverable isn't done and signed off, or a
      Sign-off waits.

    2 with the usage where the arguments are none of these."""
    raise NotImplementedError("command.main")
