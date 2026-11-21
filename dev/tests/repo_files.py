"""How the plugins' cases make and read the files of a bench: git run in a repository, files written
under a folder, the environment of each command a bench runs, and the text that a README's
walkthrough shows."""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping


def git(repo: str, *args: str) -> str:
    """Runs git in the repository, and gives what it printed."""
    done = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True)
    return done.stdout


# The settings by which coverage counts a process that a case starts.
COVERAGE_SETTINGS = ("COVERAGE_PROCESS_START", "COVERAGE_FILE")


def environment(tmp: str) -> dict[str, str]:
    """The environment of each command that a bench in the folder runs: the PATH, a home and a
    system's temporary folder of its own, the latter made, and, where check.sh measures coverage,
    its settings, so that a process that a case starts counts toward it as well."""
    env = {
        "PATH": os.environ.get("PATH", os.defpath),
        "HOME": os.path.join(tmp, "home"),
        "TMPDIR": os.path.join(tmp, "system-temp"),
    }
    env.update({name: os.environ[name] for name in COVERAGE_SETTINGS if name in os.environ})
    os.makedirs(env["TMPDIR"])
    return env


def write_files(folder: str, files: Mapping[str, str]) -> None:
    """Writes each file under the folder, by its path there."""
    for name, text in files.items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def readme_block(readme: str, after: str) -> str:
    """The first `text` block of the README at the path after the line that ends with `after`."""
    with open(readme, encoding="utf-8") as f:
        text = f.read()
    start = text.index(after) + len(after)
    found = re.search(r"```text\n(.*?)```", text[start:], re.DOTALL)
    assert found, f"the README holds no text block after {after!r}"
    return found[1].rstrip("\n")
