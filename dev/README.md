# Building the plugins

Each plugin's product vision board, architecture, tests and trials live here. Installing a plugin
copies only its own folder, so nothing here reaches its users' machines.

Every plugin is built by [the plugin best practice](./plugin-best-practice.md).
[.claude/rules/dev.md](../.claude/rules/dev.md) gives the order the work on a plugin goes in.

- [Turn](./turn/)
- [Rn](./rn/)
- [Lane](./lane/): also `testing.py` and `trials/trying.py`, what every plugin's tests and trials
  stand on
- [Pin](./pin/)

## The checks on every push

CI runs these checks on every push: the linter, the formatter, the type checker, each plugin's unit
and architecture tests with the lines and branches they run counted, Claude Code's check of every
manifest, and Mermaid's parse of every diagram in the Markdown files. pytest runs the tests on
every processor at once, as [Unit: code](./plugin-best-practice.md#unit-code) says. Run the checks
from the top of the repository:

```console
uv sync --locked
(cd dev/scripts && npm ci --ignore-scripts)
uv run sh dev/scripts/check.sh
```

`uv sync --locked` sets up the tools of `pyproject.toml`'s `dev` group in `.venv`, with
[uv](https://docs.astral.sh/uv/). Run the checks there. A `coverage` installed outside a virtual
environment does not count the scripts the tests start as separate processes. `npm ci` sets up
Mermaid's parser in `dev/scripts/node_modules`. Without it, the checks skip the diagrams and say so,
and CI parses them.

Each tool the checks install must match the hashes of the files it was locked with, so a version
replaced on PyPI or npm after it was locked does not install. The Python tools come from `uv.lock`.
`uv lock` makes that file from `pyproject.toml`, with each tool at the newest version that runs on
each Python.
Claude Code and Mermaid's parser come from `dev/scripts/package-lock.json`.

## The property-based tests and the mutation testing

On the newest Python, CI also installs the `test-quality` group, by
`uv sync --locked --group test-quality`. With it, `sh dev/scripts/check.sh` also checks for copied code. CI
then runs two more checks, as [Unit: code](./plugin-best-practice.md#unit-code) says:

- `sh dev/scripts/properties.sh` runs the property-based tests, on many inputs each in CI and on few
  elsewhere.
- `sh dev/scripts/mutate.sh` runs the mutation testing of each plugin that has a
  `dev/<plugin>/cosmic-ray.toml`.

Each of `sh dev/scripts/check.sh <plugin>`, `sh dev/scripts/properties.sh <plugin>` and `sh dev/scripts/mutate.sh <plugin>`
checks that plugin alone. `sh dev/scripts/mutate.sh --since <commit> <plugin>` runs only the mutants on the
lines changed since that commit.

## Before each push

`dev/scripts/githooks/pre-push` runs `sh dev/scripts/check.sh` on the commits pushed, and stops the
push on a failure. It checks each plugin that `sh dev/scripts/changed.sh` names: those the push
changes, those that link a file it changes, or every plugin where it changes what they all stand on.
It runs them as `sh dev/scripts/check.sh --reached`: of the tests, only those the change reaches,
chosen by pytest-testmon, without the lines counted. testmon keeps what each test ran in
`.testmondata` at the top of the clone. It comes with `pyproject.toml`'s `push` group, on Python
3.11 or later; on an older Python every test runs. Every test, the property-based tests and the
mutation testing run in CI.

Turn the hook on once in a clone with `git config core.hooksPath dev/scripts/githooks`. It needs uv on the
PATH.
