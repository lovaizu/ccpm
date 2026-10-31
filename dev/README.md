# Building the plugins

Each plugin's UX, architecture, tests and trials live here. Installing a plugin copies only its own
folder, so nothing here reaches its users' machines.

Every plugin is built on [how a plugin works](./architecture.md). The order the work on a plugin
goes in is in [.claude/rules/dev.md](../.claude/rules/dev.md).

- [turn](./turn/)
- [rn](./rn/)
- [lane](./lane/): also `testing.py` and `trials/trying.py`, what every plugin's tests and trials
  stand on

## The checks on every push

CI runs these checks on every push: the linter, the formatter, the type checker, each plugin's unit
tests with the lines and branches they run counted, and Claude Code's check of every manifest. Run
them from the top of the repository:

```console
uv sync --locked
uv run sh dev/check.sh
```

`uv sync --locked` sets up the tools of `pyproject.toml`'s `dev` group in `.venv`, with
[uv](https://docs.astral.sh/uv/). Run the checks there: a `coverage` installed outside a virtual
environment does not count the scripts the tests start as separate processes.

Each tool the checks install is held to the hashes of the files it was locked with, so a version
replaced on PyPI or npm after it was locked does not install. The Python tools come from `uv.lock`,
which `uv lock` makes from `pyproject.toml`, each at the newest version that runs on each Python.
Claude Code comes from `dev/package-lock.json`.

## The property tests and the mutation testing

On the newest Python, CI also installs the `test-quality` group, by
`uv sync --locked --group test-quality`. With it, `sh dev/check.sh` also checks for copied code. CI
then runs two more checks, as [Unit tests: code](./architecture.md#unit-tests-code) says:

- `sh dev/properties.sh` runs the property tests, on many inputs each in CI and on few elsewhere.
- `sh dev/mutate.sh` runs the mutation testing of each plugin that has a
  `dev/<plugin>/cosmic-ray.toml`.

Each of `sh dev/check.sh <plugin>`, `sh dev/properties.sh <plugin>` and `sh dev/mutate.sh <plugin>`
checks that plugin alone. `sh dev/mutate.sh --since <commit> <plugin>` runs only the mutants on the
lines changed since that commit.

## Before each push

`dev/githooks/pre-push` runs `sh dev/check.sh` on the commits pushed, and stops the push on a
failure. It checks each plugin that `sh dev/changed.sh` names: those the push changes, those that
link a file it changes, or every plugin where it changes what they all stand on. The property tests
and the mutation testing run in CI only.

Turn the hook on once in a clone with `git config core.hooksPath dev/githooks`. It needs uv on the
PATH.
