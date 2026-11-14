"""The result script, which a role runs as `python3 <plugin>/hooks/lane/result.py <role> <result>`
to give its result: it refuses a result that the role may not give, and one that no Run of the
conversation, whose ID Claude Code gives each Bash command as `CLAUDE_CODE_SESSION_ID`, holds. The
guard adds the Result to the run record at the PostToolUse of a run that gave 0, as only that
payload names the subagent that ran it."""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping

from domain import run_record
from domain.fault import Fault
from domain.laid_set import load
from domain.results import may_give
from domain.routes import stand

USAGE = "usage: result.py <role> <result>"

# The folder of the plugin that holds this script, `<plugin>/hooks/lane/result.py`.
_PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main(argv: list[str], environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `result.py <role> <result>`: 0 and the result given,
    where the laid set of the plugin that holds this script lets the role give it, and a Run of the
    conversation that goes on holds the role, as the skill of the Run or the role of a Start that
    runs, each Run as `routes.stand`, the guard's code, works it out from the run record; 1 with the
    results that the role may give where it may give no such result, or with why where no such Run
    holds the role; 2 with the usage where the arguments aren't a role and a result. It writes
    nothing to the run record."""
    if len(argv) != 2:
        return 2, "", USAGE + "\n"
    role, result = argv
    try:
        laid_set = load(_PLUGIN_ROOT)
        if laid_set is None:
            raise Fault(f"{_PLUGIN_ROOT} holds no hooks/lanes.json", "the plugin's maker")
        may = may_give(laid_set, role)
        if result not in may:
            told = " or ".join(f"`{each}`" for each in may)
            why = f"may give only {told}" if may else "has no result that it may give"
            return 1, "", f"result.py: {role} {why}, so it can't give `{result}`.\n"
        session = environ.get("CLAUDE_CODE_SESSION_ID", "")
        lines = run_record.load(run_record.temp(environ), laid_set.plugin, session)
        runs = stand(lines, laid_set, session)
    except Fault as fault:
        return 1, "", f"result.py: {fault}\n"
    if not any(_holds(run, role) for run in runs):
        why = f"no run of {laid_set.plugin} in this conversation holds {role} now"
        return 1, "", f"result.py: {why}, so it takes no result of {role}.\n"
    return 0, f"{result}\n", ""


def _holds(run: run_record.Run, role: str) -> bool:
    """Whether the Run goes on and holds the role, as its skill or the role of a Start that runs."""
    started = any(start.role == role and start.running for start in run.starts)
    return not run.ended and (run.skill == role or started)


if __name__ == "__main__":
    import os

    code, out, err = main(sys.argv[1:], os.environ)
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
