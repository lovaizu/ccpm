# Building the plugins

Each plugin's architecture, tests and trials live here. Installing a plugin copies only its own folder, so nothing here reaches its users' machines.

Every plugin is built on [how a plugin works](./architecture.md).

- [turn](./turn/)
- [rn](./rn/)
- [lane](./lane/): also `testing.py` and `trials/trying.py`, what every plugin's tests and trials share

The checks CI runs on every push, the linter, the formatter, the check for code copied between files, the type checker, each plugin's unit tests with the lines and branches they run counted, and Claude Code's check of every manifest, are run by `uv run sh dev/check.sh` from the top of the repository, [uv](https://docs.astral.sh/uv/) setting up the tools of `pyproject.toml`'s `dev` group in `.venv` with `uv sync --locked`. A `coverage` installed outside a virtual environment does not count the scripts the tests start as separate processes.

Every tool the checks install is held to the hashes of the files it was locked with, so a version replaced on PyPI or npm after it was locked does not install: the Python tools come from `uv.lock`, made from `pyproject.toml` by `uv lock`, each at the newest version that runs on each Python, and Claude Code from `dev/package-lock.json`.

On the newest Python, CI also installs the `test-quality` group, by `uv sync --locked --group test-quality`, which runs the check for copied code in `sh dev/check.sh`, and runs `sh dev/properties.sh`, the property tests, many inputs each in CI and few elsewhere, and `sh dev/mutate.sh`, the mutation testing of each plugin with a `dev/<plugin>/cosmic-ray.toml`, as [Unit tests: code](./architecture.md#unit-tests-code) says. `sh dev/check.sh <plugin>`, `sh dev/properties.sh <plugin>` and `sh dev/mutate.sh <plugin>` check that plugin alone, and `sh dev/mutate.sh --since <commit> <plugin>` only the mutants on the lines changed since that commit.

Before each push, `dev/githooks/pre-push` runs all three on the commits pushed, for each plugin `sh dev/changed.sh` names, those the push changes or that link a file it changes, or every plugin where it changes what they all stand on, the mutation testing on the lines changed alone, and stops the push on a failure. It is turned on once in a clone by `git config core.hooksPath dev/githooks`, and needs uv on PATH.

The order the work on a plugin goes in is in [.claude/rules/dev.md](../.claude/rules/dev.md).
