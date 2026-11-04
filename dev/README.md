# Building the plugins

Each plugin's UX, architecture, tests and trials live here. Installing a plugin copies only its own
folder, so nothing here reaches its users' machines.

Every plugin is built by [the plugin best practice](./plugin-best-practice.md). The order the work
on a plugin goes in is in [.claude/rules/dev.md](../.claude/rules/dev.md).

- [Turn](./turn/)
- [Rn](./rn/)
- [Lane](./lane/): also `testing.py` and `trials/trying.py`, what every plugin's tests and trials
  stand on
- [pin](./pin/)

## The checks on every push

CI runs these checks on every push: the linter, the formatter, the type checker, each plugin's unit
tests with the lines and branches they run counted, and Claude Code's check of every manifest. Run
them from the top of the repository:

```console
uv sync --locked
uv run sh dev/scripts/check.sh
```

`uv sync --locked` sets up the tools of `pyproject.toml`'s `dev` group in `.venv`, with
[uv](https://docs.astral.sh/uv/). Run the checks there: a `coverage` installed outside a virtual
environment does not count the scripts the tests start as separate processes.

Each tool the checks install is held to the hashes of the files it was locked with, so a version
replaced on PyPI or npm after it was locked does not install. The Python tools come from `uv.lock`,
which `uv lock` makes from `pyproject.toml`, each at the newest version that runs on each Python.
Claude Code comes from `dev/scripts/package-lock.json`.

## The property tests and the mutation testing

On the newest Python, CI also installs the `test-quality` group, by
`uv sync --locked --group test-quality`. With it, `sh dev/scripts/check.sh` also checks for copied code. CI
then runs two more checks, as [Unit: code](./plugin-best-practice.md#unit-code) says:

- `sh dev/scripts/properties.sh` runs the property tests, on many inputs each in CI and on few elsewhere.
- `sh dev/scripts/mutate.sh` runs the mutation testing of each plugin that has a
  `dev/<plugin>/cosmic-ray.toml`.

Each of `sh dev/scripts/check.sh <plugin>`, `sh dev/scripts/properties.sh <plugin>` and `sh dev/scripts/mutate.sh <plugin>`
checks that plugin alone. `sh dev/scripts/mutate.sh --since <commit> <plugin>` runs only the mutants on the
lines changed since that commit.

## Before each push

`dev/scripts/githooks/pre-push` runs `sh dev/scripts/check.sh` on the commits pushed, and stops the push on a
failure. It checks each plugin that `sh dev/scripts/changed.sh` names: those the push changes, those that
link a file it changes, or every plugin where it changes what they all stand on. The property tests
and the mutation testing run in CI only.

Turn the hook on once in a clone with `git config core.hooksPath dev/scripts/githooks`. It needs uv on the
PATH.
