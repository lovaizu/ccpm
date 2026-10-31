"""Mutation testing of each plugin given, or of each plugin dev/plugins.sh lists that has
dev/<plugin>/cosmic-ray.toml where none is given, run as `sh dev/mutate.sh` from the top of the
repository with the tools of pyproject.toml's dev and test-quality groups; fails on any mutant no
test catches. Given `--since <commit>` first, it tests only the mutants on lines changed since that
commit, files not yet added to git among them, by Cosmic Ray's own git filter, as before a push.

Each mutant is to be caught by the unit tests, which dev/check.sh runs, as the mutation testing
checks that they are enough; the property tests are left out of it. cr-rate is not used to fail the
run: it takes a limit of 0 as no limit.

Cosmic Ray changes the files it tests, so each worker runs on a copy of its own; one worker for each
processor, as each mutant is tested on its own, each on a port free when the run starts, so two runs
at once do not test each other's copies. The copies of each plugin's run are in
<plugin>/<yyyymmdd>-mutate-<random>/ in the system's temporary folder (dev/architecture.md, Where a
plugin writes its files), removed when the run ends, and the system's temporary folder the workers'
tests are given is in it, so what a test killed on its timeout leaves goes with it."""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lane"))
import testing

# Cosmic Ray is installed on the newest Python alone, so the type check on 3.9 finds it missing.
from cosmic_ray.cli import main as cosmic_ray  # pyrefly: ignore[missing-import]
from cosmic_ray.config import load_config, serialize_config  # pyrefly: ignore[missing-import]

USAGE = "usage: sh dev/mutate.sh [--since <commit>] [<plugin>...]"
# What cr-report ends with where no mutant survives.
NONE_SURVIVE = re.compile(r"^surviving mutants: 0 ", re.MULTILINE)


def free_ports(count: int) -> list[int]:
    """Ports free now, as many as asked: each socket is held until all are bound, so no two ports
    are the same."""
    found = [socket.socket() for _ in range(count)]
    try:
        for s in found:
            s.bind(("localhost", 0))
        return [s.getsockname()[1] for s in found]
    finally:
        for s in found:
            s.close()


def outside_venv(folder: str, names: list[str]) -> list[str]:
    """What copytree leaves out of a copy of the repository: the virtual environment uv makes in
    .venv, as the workers run the tools from where it is, and the files Python writes in it while
    the first workers start would be copied half made."""
    return [".venv"] if folder == "." else []


def started(copy: str, ports: list[int]) -> list[subprocess.Popen[bytes]]:
    """A worker on each port, on a copy of the repository of its own in the run's folder, given the
    system's temporary folder in it; each answering once this gives them back."""
    env = {**os.environ, "TMPDIR": os.path.join(copy, "tmp")}
    os.mkdir(env["TMPDIR"])
    workers = []
    for port in ports:
        place = os.path.join(copy, f"worker-{port}")
        shutil.copytree(".", place, symlinks=True, ignore=outside_venv)
        workers.append(
            subprocess.Popen(
                ["cosmic-ray", "http-worker", "--port", str(port)],
                cwd=place,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        )
    for port in ports:
        for _ in range(300):
            try:
                socket.create_connection(("localhost", port)).close()
                break
            except OSError:
                time.sleep(0.1)
    return workers


def linked(folders: list[str]) -> list[str]:
    """Each module in the folders that is a link: what a plugin takes from another through a link is
    mutated in the plugin it is from, with that plugin's tests (dev/architecture.md, Code kept
    once)."""
    return sorted(
        os.path.join(top, name)
        for folder in folders
        for top, _, names in os.walk(folder)
        for name in names
        if name.endswith(".py") and os.path.islink(os.path.join(top, name))
    )


def written(plugin: str, ports: list[int], since: str, path: str) -> None:
    """The run's config, written at the path: the plugin's cosmic-ray.toml, its links left out, the
    workers on the ports its distributor, and the commit the changed lines are counted from given
    to the git filter, where one is."""
    config = load_config(config_of(plugin))
    config["excluded-modules"] = linked(config["module-path"])
    urls = [f"http://localhost:{port}" for port in ports]
    config["distributor"] = {"name": "http", "http": {"worker-urls": urls}}
    if since:
        config["filters"] = {"git-filter": {"branch": since}}
    with open(path, "w", encoding="utf-8") as f:
        f.write(serialize_config(config))


def filtered_by_git(copy: str, config: str, db: str) -> None:
    """The mutants on no line changed since the commit the config gives marked as not to be tested.
    The git filter reads the lines changed from `git diff`, which leaves out a file not yet added to
    git, such as a check just written; each is marked as to be added in a copy of the index, the
    index git uses itself left as it is, so all its lines count as changed."""
    index = os.path.join(copy, "index")
    shutil.copy(git("rev-parse", "--git-path", "index"), index)
    env = {**os.environ, "GIT_INDEX_FILE": index}
    new = git("ls-files", "--others", "--exclude-standard").splitlines()
    if new:
        subprocess.run(["git", "add", "--intent-to-add", "--", *new], env=env, check=True)
    subprocess.run(["cr-filter-git", "--config", config, db], env=env, check=True)


def git(*args: str) -> str:
    """What git prints, run with the arguments."""
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def mutated(plugin: str, since: str) -> bool:
    """Whether every mutant of the plugin's code, or of the lines changed since the commit where
    one is given, is caught; the report of those that survive printed."""
    copy = testing.temporary(plugin, "mutate")
    workers: list[subprocess.Popen[bytes]] = []
    try:
        ports = free_ports(os.cpu_count() or 1)
        workers = started(copy, ports)
        config, db = os.path.join(copy, "config.toml"), os.path.join(copy, "mutants.sqlite")
        written(plugin, ports, since, config)
        subprocess.run(["cosmic-ray", "init", config, db], check=True)
        # A line marked `# pragma: no mutate` has no mutant a test can tell apart, for the reason
        # the plugin's cosmic-ray.toml gives (dev/architecture.md, Unit tests: code).
        subprocess.run(["cr-filter-pragma", db], check=True)
        if since:
            filtered_by_git(copy, config, db)
        # Cosmic Ray 8.7.0's http distributor asks asyncio for a loop that Python 3.14 no longer
        # makes on its own (sixty-north/cosmic-ray#608, fixed after 8.7.0), so one is set first.
        asyncio.set_event_loop(asyncio.new_event_loop())
        if cosmic_ray(["exec", config, db]):
            sys.exit(f"mutate.py: Cosmic Ray stopped testing {plugin}'s mutants, as said above")
        report = subprocess.run(
            ["cr-report", "--surviving-only", "--show-diff", db],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        print(report, end="")
        return NONE_SURVIVE.search(report) is not None
    finally:
        # The workers are stopped before their copies are removed, and the next plugin's run takes
        # ports of its own.
        for worker in workers:
            worker.kill()
            worker.wait()
        shutil.rmtree(copy, ignore_errors=True)


def main(args: list[str]) -> None:
    """Tests the mutants of each plugin the arguments give, in order; exits with a stop at the
    first plugin whose mutants survive, or that has no cosmic-ray.toml."""
    since = ""
    if args[:1] == ["--since"]:
        if len(args) < 2:
            sys.exit(USAGE)
        since, args = args[1], args[2:]
    listed = subprocess.run(["sh", "dev/plugins.sh"], check=True, capture_output=True, text=True)
    plugins = args or [p for p in listed.stdout.split() if os.path.isfile(config_of(p))]
    for plugin in plugins:
        if not os.path.isfile(config_of(plugin)):
            sys.exit(f"mutate.py: {config_of(plugin)} is not there; give a plugin that has it")
        try:
            caught = mutated(plugin, since)
        except subprocess.CalledProcessError as stopped:
            sys.exit(f"mutate.py: {stopped}")
        if not caught:
            sys.exit(f"mutate.py: mutants of {plugin} survive, shown above")


def config_of(plugin: str) -> str:
    """The plugin's cosmic-ray.toml."""
    return f"dev/{plugin}/cosmic-ray.toml"


if __name__ == "__main__":
    main(sys.argv[1:])
