"""Lane's script that up runs: `lay.py types` gives each lane type for up to propose from,
`lay.py steps <plugin>` gives each Role and Step of the plugin without the text that Lane laid,
`lay.py print <plugin> <proposal.json>` checks the Proposal that up wrote and shows it, and
`lay.py write <plugin> <ID>` lays the Proposal of the ID, which its caller approved, into the
plugin. It imports the lane types from `hooks/lane/`, the code it copies into each plugin."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "hooks", "lane"))

USAGE = (
    "usage: lay.py types | steps <plugin> | print <plugin> <proposal.json> | write <plugin> <ID>"
)


def types_text() -> str:
    """What `lay.py types` prints: for each lane type, its name, what it takes, the steps it suits,
    and its sentence as it reads on an example."""
    raise NotImplementedError("lay.types_text")


def steps_text(plugin_root: str) -> str:
    """What `lay.py steps <plugin>` prints for the plugin in the folder: each Role, a skill or a
    subagent, with each of its Steps by its number and its words, without the sentences that the
    plugin's Laid names where a Step still holds them word for word, and beside a Step each laid
    sentence that the user changed, which Lane keeps as their own words, as `steps.roles` reads
    them. Raises Fault as `steps.roles` does."""
    raise NotImplementedError("lay.steps_text")


def main(argv: list[str], environ: Mapping[str, str], cwd: str) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `lay.py` with the arguments, from the folder `cwd`,
    where `<plugin>` is the plugin's folder from there: 0 with what `types`, `steps`, `print`, or
    `write` prints; 1 with what's wrong where the plugin's Steps can't be read, where the Proposal
    can't stand, where no Proposal has the ID, where the Steps changed since it was shown, where the
    Run of up that showed it no longer waits for its reply, as `proposal.waits` reads the Run of up
    that `routes.stand`, the guard's code, works out from the run record of that conversation in the
    system's temporary folder, or where `claude plugin validate` fails after laying, with what it
    said; 2 with the usage where the arguments are none of these. `print` keeps the Proposal with
    the conversation that `CLAUDE_CODE_SESSION_ID` names, which Claude Code gives each Bash
    command."""
    raise NotImplementedError("lay.main")


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], os.environ, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
