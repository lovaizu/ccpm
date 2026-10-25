"""What every plugin's tests stand on: a temporary folder each test runs in, with its files written
and read; for a test that reads git, a repository made once a run and copied into each test's
folder, git reading no setting of the machine it runs on, since a repository made by git commands
for every test spends most of the tests' time; and, for a plugin whose lanes lane laid, lane's code
as the plugin takes it through a link, and each lane its hooks/lanes.json lays. What a run of a
plugin's tests writes is in one folder of its own, `<plugin>/<yyyymmdd>-tests-<random>/` in the
system's temporary folder, as dev/architecture.md's Where a plugin writes its files has it, the
plugin's tests being in dev/<plugin>/tests/; and such a folder for what a trial uses only while
it runs."""

from __future__ import annotations

import atexit
import importlib
import inspect
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from typing import Any, Callable
from unittest import mock

# Each repository made this run, by the name it was made under, kept until the run ends.
MADE: dict[str, str] = {}
# The folder of this run of each plugin's tests, by the plugin's name.
RUNS: dict[str, str] = {}


def temporary(plugin: str, name: str) -> str:
    """A new folder of the plugin's, `<plugin>/<yyyymmdd>-<name>-<random>/` in the system's
    temporary folder, for what a test or a trial uses only while it runs, as dev/architecture.md's
    Where a plugin writes its files has it."""
    top = os.path.join(tempfile.gettempdir(), plugin)
    os.makedirs(top, exist_ok=True)
    return tempfile.mkdtemp(prefix=time.strftime(f"%Y%m%d-{name}-"), dir=top)


def run_folder(file: str) -> str:
    """The folder of this run of the tests of the plugin the file is a test of, made the first time
    it is asked for and removed when the run ends."""
    plugin = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(file))))
    if plugin not in RUNS:
        made = temporary(plugin, "tests")
        RUNS[plugin] = os.path.realpath(made)
        atexit.register(shutil.rmtree, made, True)
    return RUNS[plugin]


class FolderTest(unittest.TestCase):
    """Each test runs in a temporary folder of its own, `base`, in the run's folder, removed after
    it."""

    def setUp(self) -> None:
        self.run_folder = run_folder(inspect.getfile(type(self)))
        self.base = os.path.realpath(tempfile.mkdtemp(dir=self.run_folder))
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
            made = tempfile.mkdtemp(dir=self.run_folder)
            os.chdir(made)
            make()
            MADE[name] = made
        place = os.path.join(self.base, name)
        shutil.copytree(MADE[name], place, symlinks=True)
        os.chdir(place)
        return place


def load_hypothesis_profile() -> None:
    """Loads Hypothesis's settings, once a property test has imported it: new inputs on every run,
    CI included, a failure printing how to reproduce it, nothing kept after the run, its folder in
    the run's folder of the plugin whose module of property tests loads them, and no deadline, as an
    example's time varies from machine to machine; few inputs while a change is made and many in
    CI, the dev and ci profiles of Hypothesis's settings guide."""
    import hypothesis  # pyrefly: ignore[missing-import]
    import hypothesis.configuration  # pyrefly: ignore[missing-import]

    loading = next(f.filename for f in inspect.stack() if f.filename != __file__)
    hypothesis.configuration.set_hypothesis_home_dir(tempfile.mkdtemp(dir=run_folder(loading)))
    kept = {"derandomize": False, "database": None, "print_blob": True, "deadline": None}
    hypothesis.settings.register_profile("dev", max_examples=10, **kept)
    hypothesis.settings.register_profile("ci", max_examples=1000, **kept)
    hypothesis.settings.load_profile("ci" if os.environ.get("CI") else "dev")


def hypothesis() -> Any:
    """Hypothesis, its settings loaded as load_hypothesis_profile says, for a module of property
    tests to take given, assume and strategies from; stops the module, its tests skipped, where it
    is not installed, as it is installed on the newest Python alone, so the type check on 3.9
    finds it missing."""
    try:
        import hypothesis  # pyrefly: ignore[missing-import]
    except ImportError:
        raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None
    load_hypothesis_profile()
    return hypothesis


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
    """Each lane the plugin's hooks/lanes.json lays, as (agent, step, lane, takes), the agent as
    `<plugin>:<name>`, read by lane's code as the plugin takes it, as the guard reads them."""
    (hooks_file,) = lane_code(plugin, "hooks_file")
    with open(os.path.join(plugin, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        name = json.load(f)["name"]
    found = []
    for agent in hooks_file.laid(plugin)["subagents"]:
        for number, lane, takes, _ in hooks_file.lanes_of(agent):
            found.append((f"{name}:{agent['name']}", number, lane, takes))
    return found
