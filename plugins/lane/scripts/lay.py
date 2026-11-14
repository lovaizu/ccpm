"""Lane's script that up runs: `lay.py types` gives each lane type for up to propose from,
`lay.py steps <plugin>` gives each Role and Step of the plugin without the text that Lane laid,
`lay.py print <plugin> <proposal.json>` checks the Proposal that up wrote and shows it, and
`lay.py write <plugin> <ID>` lays the Proposal of the ID, which its caller approved, into the
plugin. It imports the lane types from `hooks/lane/`, the code it copies into each plugin."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping

# Lane's folder, which holds this script in scripts/ and its code in hooks/lane/.
_LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_LANE, "hooks", "lane"))

from domain import laid_set, run_record
from domain.fault import Fault
from domain.routes import stand
from laying import lay
from proposal import check, keep, kept, parse, waits
from shown import text
from steps import fingerprint, laid_of, roles

USAGE = (
    "usage: lay.py types | steps <plugin> | print <plugin> <proposal.json> | write <plugin> <ID>"
)
# The line by which `lay.py write` ends once it laid a Proposal, as Claude Code loads a plugin's
# hooks only as a session starts or once the person types /reload-plugins.
_RELOAD = "Type /reload-plugins, and the checks hold from your next prompt.\n"


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
    blocks = []
    for role in roles(plugin_root, laid_of(plugin_root)):
        kind = "skill" if role.skill else "subagent"
        lines = [f"{role.name}, a {kind}, in {role.entry}:"]
        for step in role.steps:
            lines.append(step.words)
            lines += [f"  (kept as your own words: {each})" for each in step.kept]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


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
    try:
        if len(argv) == 3 and argv[0] == "print":
            return _print(os.path.join(cwd, argv[1]), os.path.join(cwd, argv[2]), environ)
        if len(argv) == 2 and argv[0] == "steps":
            return 0, steps_text(os.path.join(cwd, argv[1])), ""
        if len(argv) == 3 and argv[0] == "write":
            return _write(os.path.join(cwd, argv[1]), argv[2], environ)
    except Fault as fault:
        return 1, "", f"lay.py: {fault}\n"
    return 2, "", USAGE + "\n"


def _print(plugin_root: str, path: str, environ: Mapping[str, str]) -> tuple[int, str, str]:
    try:
        with open(path, encoding="utf-8") as f:
            given = json.load(f)
    except (OSError, ValueError) as e:
        raise Fault(f"{path} can't be read as JSON ({e})", "up") from None
    proposal = parse(given, path)
    found = roles(plugin_root, laid_of(plugin_root))
    refusal = check(proposal, found, plugin_root)
    if refusal is not None:
        faults = "".join(f"- {fault}\n" for fault in refusal.faults)
        return 1, "", f"lay.py: the Proposal can't stand:\n{faults}"
    conversation = environ.get("CLAUDE_CODE_SESSION_ID", "")
    shown = keep(proposal, found, run_record.temp(environ), conversation)
    return 0, text(shown, found), ""


def _write(plugin_root: str, id: str, environ: Mapping[str, str]) -> tuple[int, str, str]:
    temp = run_record.temp(environ)
    given = kept(temp, _name(plugin_root), id)
    if given is None:
        return 1, "", f"lay.py: no Proposal has the ID {id}, so run `lay.py print` again.\n"
    found = roles(plugin_root, laid_of(plugin_root))
    if fingerprint(found) != given.steps:
        why = f"the steps changed since `lay.py print` showed {id}"
        return 1, "", f"lay.py: {why}, so run `lay.py print` on them again.\n"
    if not waits(given, _run_of_up(temp, given.conversation)):
        why = f"the Run of up that showed {id} ended without its approval"
        return 1, "", f"lay.py: {why}, so propose again.\n"
    laid = lay(given, found, plugin_root, os.path.join(_LANE, "hooks", "lane"), _validate)
    if not laid.validated:
        return 1, "\n".join(laid.lines) + "\n", ""
    return 0, "\n".join(laid.lines) + "\n" + _RELOAD, ""


def _name(plugin_root: str) -> str:
    """The plugin's name, as its plugin.json gives it."""
    path = os.path.join(plugin_root, ".claude-plugin", "plugin.json")
    try:
        with open(path, encoding="utf-8") as f:
            return str(json.load(f)["name"])
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Fault(f"{path} gives no name ({e!r})", "the plugin's maker") from None


def _run_of_up(temp: str, conversation: str) -> run_record.Run | None:
    """The last Run of Lane's up in the conversation, None where it has none."""
    own = laid_set.load(_LANE)
    if not conversation or own is None:
        return None
    runs = stand(run_record.load(temp, own.plugin, conversation), own, conversation)
    return next((run for run in reversed(runs) if run.skill == "up"), None)


def _validate(plugin_root: str) -> tuple[bool, str]:
    """Whether `claude plugin validate` passes on the plugin, and what it said."""
    try:
        done = subprocess.run(
            ["claude", "plugin", "validate", plugin_root],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return False, "lay.py: `claude` isn't on the PATH, so `claude plugin validate` can't run"
    return done.returncode == 0, (done.stdout + done.stderr).strip()


if __name__ == "__main__":
    code, out, err = main(sys.argv[1:], os.environ, os.getcwd())
    sys.stdout.write(out)
    sys.stderr.write(err)
    sys.exit(code)
