"""Mutation testing of each plugin given, or of each plugin dev/scripts/plugins.sh lists that has
dev/<plugin>/cosmic-ray.toml where it gets none, run as `sh dev/scripts/mutate.sh` from the top of
the repository with the tools of pyproject.toml's dev and test-quality groups. It fails on any
mutant no test catches, and on any no test run checked. It stops before the mutants where the tests
fail with none. Given `--since <commit>` first, it tests only the mutants on lines changed since
that commit, files not yet added to git among them, by Cosmic Ray's own git filter, as before a
push.

The unit tests, which dev/scripts/check.sh runs, are to catch each mutant, as the mutation testing
checks that they're enough. The property-based tests take no part in it. The run doesn't use
cr-rate to fail: it takes a limit of 0 as no limit.

Cosmic Ray changes the files it tests, so each worker runs on a copy of its own. One worker runs
for each processor, as the run tests each mutant on its own, each on a port free when the run
starts, so two runs at once don't test each other's copies. The copies of each plugin's run lie in
<plugin>/<yyyymmdd>-mutate-<random>/ in the system's temporary folder, as Q12 of
plugins/rn/domain/best-practices/plugin/best-practice.md says. The run removes them when it ends,
and the system's temporary folder that the workers' tests get lies in it, so what a test killed on
its timeout leaves goes with it."""

from __future__ import annotations

import asyncio
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lane")
)
import testing

# Only the newest Python has Cosmic Ray, so the type check on 3.9 finds it missing.
from cosmic_ray.cli import main as cosmic_ray  # pyrefly: ignore[missing-import]
from cosmic_ray.config import load_config, serialize_config  # pyrefly: ignore[missing-import]
from cosmic_ray.work_db import WorkDB, use_db  # pyrefly: ignore[missing-import]
from cosmic_ray.work_item import WorkerOutcome  # pyrefly: ignore[missing-import]

USAGE = "usage: sh dev/scripts/mutate.sh [--since <commit>] [<plugin>...]"
# What cr-report ends with where no mutant survives.
NONE_SURVIVE = re.compile(r"^surviving mutants: 0 ", re.MULTILINE)


def free_ports(count: int) -> list[int]:
    """Ports free now, as many as asked: each socket stays open until all have bound, so no two
    ports are the same."""
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
    .venv, as the workers run the tools from where it lies, and the copy would take half made the
    files Python writes in it while the first workers start."""
    return [".venv"] if folder == "." else []


def env_of(copy: str) -> dict[str, str]:
    """The environment the workers' tests get: the system's temporary folder in the run's
    folder, and no bytecode written, as Cosmic Ray runs a test command."""
    return {**os.environ, "TMPDIR": os.path.join(copy, "tmp"), "PYTHONDONTWRITEBYTECODE": "1"}


def started(copy: str, ports: list[int]) -> list[subprocess.Popen[bytes]]:
    """A worker on each port, on a copy of the repository of its own in the run's folder, given the
    system's temporary folder in it. Each answers once this gives them back."""
    env = env_of(copy)
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
    """Each module in the folders that's a link: the run mutates what a plugin takes from another
    through a link in the plugin it comes from, with that plugin's tests, as Q14 of
    plugins/rn/domain/best-practices/plugin/best-practice.md says."""
    return sorted(
        os.path.join(top, name)
        for folder in folders
        for top, _, names in os.walk(folder)
        for name in names
        if name.endswith(".py") and os.path.islink(os.path.join(top, name))
    )


def written(plugin: str, ports: list[int], since: str, path: str) -> None:
    """The run's config, written at the path: the plugin's cosmic-ray.toml, its links left out
    beside the modules it leaves out itself, the workers on the ports its distributor, and the
    commit the changed lines count from given to the git filter, where there is one."""
    config = load_config(config_of(plugin))
    own = list(config.get("excluded-modules", []))
    config["excluded-modules"] = own + linked(config["module-path"])
    urls = [f"http://localhost:{port}" for port in ports]
    config["distributor"] = {"name": "http", "http": {"worker-urls": urls}}
    if since:
        config["filters"] = {"git-filter": {"branch": since}}
    with open(path, "w", encoding="utf-8") as f:
        f.write(serialize_config(config))


def filtered_by_git(copy: str, config: str, db: str) -> None:
    """The mutants on no line changed since the commit the config gives, marked so the run skips
    them. The git filter reads the lines changed from `git diff`, which leaves out a file not yet
    added to git, such as a check just written. A copy of the index marks each such file as one to
    add, and the index git uses itself stays unchanged, so all its lines count as changed."""
    index = os.path.join(copy, "index")
    shutil.copy(git("rev-parse", "--git-path", "index"), index)
    env = {**os.environ, "GIT_INDEX_FILE": index}
    new = git("ls-files", "--others", "--exclude-standard").splitlines()
    if new:
        subprocess.run(["git", "add", "--intent-to-add", "--", *new], env=env, check=True)
    subprocess.run(["cr-filter-git", "--config", config, db], env=env, check=True)


def unmutated(plugin: str, place: str, env: dict[str, str]) -> None:
    """Exits saying so where the plugin's test command fails on its code with no mutant, run in the
    worker's copy at the place, its output printed: every mutant would then count as caught,
    though no test caught it."""
    # Split as Cosmic Ray splits it to run it.
    test = shlex.split(load_config(config_of(plugin))["test-command"])
    done = subprocess.run(test, cwd=place, env=env, capture_output=True, text=True, check=False)
    if done.returncode:
        print(done.stdout + done.stderr, end="")
        sys.exit(f"mutate.py: {plugin}'s tests fail with no mutant, as shown above")


def untested(db: str) -> list[str]:
    """Each mutant in the database that no test run checked, as the worker failed either before
    its tests ran or after, such as where a mutant removed the code of its worker's copy, by its
    module, its line and the last line the worker printed. cr-report counts such a mutant as
    caught, though no test caught it, as Q10 of
    plugins/rn/domain/best-practices/plugin/best-practice.md says."""
    failed = (WorkerOutcome.EXCEPTION, WorkerOutcome.ABNORMAL)
    with use_db(db, WorkDB.Mode.open) as work:
        items = {item.job_id: item for item in work.work_items}
        return [
            f"{m.module_path}:{m.start_pos[0]}: {last_line(result.output)}"
            for job, result in work.results
            if result.worker_outcome in failed
            for m in items[job].mutations
        ]


def last_line(output: str | None) -> str:
    """The last line of what a worker printed, or "" where it printed none."""
    return ((output or "").strip().splitlines() or [""])[-1]


def git(*args: str) -> str:
    """What git prints, run with the arguments."""
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()


def mutated(plugin: str, since: str) -> bool:
    """Whether the tests catch every mutant of the plugin's code, or of the lines changed since the
    commit where it gets one. It prints the report of those that survive."""
    copy = testing.temporary(plugin, "mutate")
    workers: list[subprocess.Popen[bytes]] = []
    try:
        ports = free_ports(os.cpu_count() or 1)
        workers = started(copy, ports)
        unmutated(plugin, os.path.join(copy, f"worker-{ports[0]}"), env_of(copy))
        config, db = os.path.join(copy, "config.toml"), os.path.join(copy, "mutants.sqlite")
        written(plugin, ports, since, config)
        subprocess.run(["cosmic-ray", "init", config, db], check=True)
        # A line marked `# pragma: no mutate` has no mutant a test can tell apart, for the reason
        # the plugin's cosmic-ray.toml gives, as Q12 of
        # plugins/rn/domain/best-practices/architecture/best-practice.md says.
        subprocess.run(["cr-filter-pragma", db], check=True)
        if since:
            filtered_by_git(copy, config, db)
        # Cosmic Ray 8.7.0's http distributor asks asyncio for a loop that Python 3.14 no longer
        # makes on its own, which sixty-north/cosmic-ray#608 fixed after 8.7.0, so this sets one
        # first.
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
        missed = untested(db)
        if missed:
            print("\n".join(missed))
            sys.exit(f"mutate.py: {len(missed)} of {plugin}'s mutants were not tested, shown above")
        return NONE_SURVIVE.search(report) is not None
    finally:
        # The workers stop before the run removes their copies, and the next plugin's run takes
        # ports of its own.
        for worker in workers:
            worker.kill()
            worker.wait()
        shutil.rmtree(copy, ignore_errors=True)


def main(args: list[str]) -> None:
    """Tests the mutants of each plugin the arguments give, in order. Exits with a stop at the
    first plugin whose mutants survive, or that has no cosmic-ray.toml."""
    since = ""
    if args[:1] == ["--since"]:
        if len(args) < 2:
            sys.exit(USAGE)
        since, args = args[1], args[2:]
    listed = subprocess.run(
        ["sh", "dev/scripts/plugins.sh"], check=True, capture_output=True, text=True
    )
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
