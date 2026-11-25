"""How rn's cases make and read the files of a repository: git run in it, and files written under
a folder."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping


def git(repo: str, *args: str) -> str:
    """Runs git in the repository, and gives what it printed."""
    done = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True)
    return done.stdout


def write_files(folder: str, files: Mapping[str, str]) -> None:
    """Writes each file under the folder, by its path there."""
    for name, text in files.items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
