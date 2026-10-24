"""What every plugin's tests stand on: a temporary folder each test runs in, with its files written
and read; for a test that reads git, a repository made once a run and copied into each test's
folder, git reading no setting of the machine it runs on, since a repository made by git commands
for every test spends most of the tests' time; and, for a plugin whose lanes lane laid, lane's code
as the plugin takes it through a link, and each lane its hooks/hooks.json lays."""

from __future__ import annotations

import atexit
import importlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Callable
from unittest import mock

# Each repository made this run, by the name it was made under, kept until the run ends.
MADE: dict[str, str] = {}
KEPT = os.path.realpath(tempfile.mkdtemp())
atexit.register(shutil.rmtree, KEPT, True)


class FolderTest(unittest.TestCase):
    """Each test runs in a temporary folder of its own, `base`, removed after it."""

    def setUp(self) -> None:
        self.base = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.base)
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(self.base)

    def write(self, path: str, text: str) -> None:
        """Writes the text at the path, making its folder where it is not there."""
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def write_json(self, path: str, data: Any) -> None:
        """Writes the data at the path as JSON on one line."""
        self.write(path, json.dumps(data))

    def read(self, path: str) -> str:
        """The text at the path."""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def read_json(self, path: str) -> Any:
        """The JSON at the path."""
        with open(path, encoding="utf-8") as f:
            return json.load(f)


class GitTest(FolderTest):
    """A test whose git reads no setting of the machine and finds no repository above `base`."""

    def setUp(self) -> None:
        super().setUp()
        env = {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "HOME": self.base,
            "GIT_CEILING_DIRECTORIES": self.base,
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com",
        }
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)

    def git(self, *args: str) -> None:
        """Runs git with the arguments where the test stands; fails the test where git fails."""
        subprocess.run(["git", *args], check=True, capture_output=True)

    def commit(self) -> None:
        """Commits every change on the checked-out branch."""
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "c")

    def copied(self, name: str, make: Callable[[], None]) -> str:
        """The repository `make` builds where it stands, made the first time a test asks for it by
        this name and copied into `base/<name>` for each test, which then stands in it."""
        if name not in MADE:
            made = tempfile.mkdtemp(dir=KEPT)
            os.chdir(made)
            make()
            MADE[name] = made
        place = os.path.join(self.base, name)
        shutil.copytree(MADE[name], place, symlinks=True)
        os.chdir(place)
        return place


def load_hypothesis_profile() -> None:
    """Loads Hypothesis's settings, once a property test has imported it: new inputs on every run,
    CI included, a failure printing how to reproduce it, nothing kept after the run, and no
    deadline, as an example's time varies from machine to machine; few inputs while a change is
    made and many in CI, the dev and ci profiles of Hypothesis's settings guide, or the profile
    HYPOTHESIS_PROFILE names, such as dev for mutation testing, which runs the tests once for each
    mutant."""
    import hypothesis  # pyrefly: ignore[missing-import]
    import hypothesis.configuration  # pyrefly: ignore[missing-import]

    hypothesis.configuration.set_hypothesis_home_dir(tempfile.mkdtemp(dir=KEPT))
    kept = {"derandomize": False, "database": None, "print_blob": True, "deadline": None}
    hypothesis.settings.register_profile("dev", max_examples=10, **kept)
    hypothesis.settings.register_profile("ci", max_examples=1000, **kept)
    default = "ci" if os.environ.get("CI") else "dev"
    hypothesis.settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", default))


def lane_code(plugin: str, *names: str) -> list[Any]:
    """lane's modules of the names, imported from the link in the plugin's hooks: lane's code and
    the plugin's scripts share module names, such as call, so lane's are imported apart and the
    plugin's put back after."""
    code = os.path.join(plugin, "hooks", "lane")
    shared = {os.path.splitext(n)[0] for n in os.listdir(code)} & {
        os.path.splitext(n)[0] for n in os.listdir(os.path.join(plugin, "scripts"))
    }
    own = {n: sys.modules.pop(n) for n in shared if n in sys.modules}
    sys.path.insert(0, code)
    try:
        return [importlib.import_module(n) for n in names]
    finally:
        sys.path.pop(0)
        for n in shared:
            sys.modules.pop(n, None)
        sys.modules.update(own)


def laid(plugin: str) -> list[tuple[str, int, str, list[str]]]:
    """Each lane the plugin's hooks/hooks.json lays, as (agent, step, lane, takes), read from the
    words after the command's last `; exec `, as lane writes them."""
    with open(os.path.join(plugin, "hooks", "hooks.json"), encoding="utf-8") as f:
        hooks = json.load(f)["hooks"]
    found = []
    for entries in hooks.values():
        for entry in entries:
            words = shlex.split(entry["hooks"][0]["command"].rpartition("; exec ")[2])
            agent, *held = words[2:]
            for one in held:
                number, lane, takes = one.split(":", 2)
                found.append((agent, int(number), lane, takes.split(",")))
    return found
