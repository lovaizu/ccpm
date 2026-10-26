"""The `gh` rn's acceptance test puts first on the PATH Claude Code runs with: runs the real gh for
every command, with the repository `--repo lovaizu/ccpm` names changed to lovaizu/playground, so the
issue rn's learnings stage sends reaches the playground rather than a repository people use; any
other command that still names lovaizu/ccpm it refuses, exiting 1, run by no gh. It
keeps each command, as given and as run, with its exit code and what it printed, as a line of
`gh.jsonl` in the run's folder, above its own, from which the trial finds each issue the run
opened; what gh prints on its standard error passes through, kept by no line.

The trial copies it into `<run>/bin/`, beside a `gh` that runs it with the real gh's path first:

    python3 gh.py <the real gh> <gh's arguments>...

Exits with the real gh's exit code."""

import json
import os
import subprocess
import sys

LOG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gh.jsonl")
PEOPLE = "lovaizu/ccpm"
PLAYGROUND = "lovaizu/playground"


def changed(args: list) -> list:
    """The arguments with lovaizu/ccpm changed to lovaizu/playground where `--repo`, or its short
    form `-R`, names it, as `--repo lovaizu/ccpm` or `--repo=lovaizu/ccpm`; each other argument as
    it is."""
    out = []
    for k, arg in enumerate(args):
        if arg == f"--repo={PEOPLE}":
            arg = f"--repo={PLAYGROUND}"
        elif arg == PEOPLE and k and args[k - 1] in ("--repo", "-R"):
            arg = PLAYGROUND
        out.append(arg)
    return out


def main() -> int:
    """Runs the real gh on the arguments changed, keeping the command in gh.jsonl; gives gh's exit
    code."""
    real, given = sys.argv[1], sys.argv[2:]
    ran = changed(given)
    if any(PEOPLE in arg for arg in ran):
        print(f"gh: the trial keeps {PEOPLE} out of reach; nothing was run", file=sys.stderr)
        done = subprocess.CompletedProcess(ran, 1, "")
    else:
        done = subprocess.run([real, *ran], stdout=subprocess.PIPE, text=True, check=False)
    with open(LOG, "a", encoding="utf-8") as f:
        kept = {"given": given, "ran": ran, "code": done.returncode, "printed": done.stdout}
        f.write(json.dumps(kept, ensure_ascii=False) + "\n")
    sys.stdout.write(done.stdout)
    return done.returncode


if __name__ == "__main__":
    sys.exit(main())
