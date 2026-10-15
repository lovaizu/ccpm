"""What turn keeps of the user's repository: what git holds, and what changed during a run."""

import hashlib
import os
import subprocess

from state import RUN, Stop


def git(*args):
    done = subprocess.run(["git", *args], check=False, capture_output=True, text=True)
    if done.returncode:
        raise Stop(done.stderr.strip())
    return done.stdout


def changed():
    """Each file git does not hold as committed, with what it holds now, or None where it is gone."""
    found = {}
    for entry in git("status", "--porcelain", "-z", "--untracked-files=all", "--no-renames").split(
        "\0"
    ):
        path = entry[3:]
        if path:
            found[path] = None
            if os.path.isfile(path):
                with open(path, "rb") as f:
                    found[path] = hashlib.sha1(f.read()).hexdigest()
    return found


def elsewhere(run, deliverable):
    """The line naming each file changed since the run started outside where the work goes and the
    run's evidence, or none."""
    now = changed()
    ours = (deliverable, run["out"], RUN)
    # A second reading's folder lies in the first's, and both hold the run's evidence.
    kept = os.path.dirname(run["work"]) if run.get("second") else run["work"]
    names = sorted(
        p
        for p in set(run["before"]) | set(now)
        if run["before"].get(p, "") != now.get(p, "")
        and p not in ours
        and not p.startswith(kept + "/")
    )
    return [f"Also changed during the run, outside the work: {', '.join(names)}"] if names else []
