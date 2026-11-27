"""The unit cases of each script's `__main__.py`, as python3 runs the script's folder: it reaches
its `command` module from scripts/ and ends with what the module's `main` gives, here the usage of
arguments of another form."""

from __future__ import annotations

import os
import subprocess
import sys

import pytest
import rn_files
from repository.command import USAGE as REPOSITORY
from role.command import USAGE as ROLE
from steering.command import USAGE as STEERING

SCRIPTS = os.path.join(rn_files.RN, "domain", "scripts")


@pytest.mark.parametrize(
    ("script", "usage"),
    [("repository", REPOSITORY), ("role", ROLE), ("steering", STEERING)],
)
def test_each_script_run_with_no_arguments_exits_2_with_its_usage(script: str, usage: str):
    """Given one of rn's scripts, repository, role, or steering
    When python3 runs its folder from the repository's top, as the checks run each test, with no
    arguments and nothing on stdin
    Then it exits 2, having written nothing on stdout and its command module's usage on stderr"""
    ran = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)],
        cwd=rn_files.TOP,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )
    assert (ran.returncode, ran.stdout, ran.stderr) == (2, "", usage)
