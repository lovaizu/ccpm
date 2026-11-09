# Building the plugins

Each plugin's product vision and architecture live here. Installing a plugin
copies only its own folder, so nothing here reaches its users' machines.

Every plugin follows [the plugin best practice](../plugins/rn/domain/best-practices/plugin/best-practice.md).
[.claude/rules/dev.md](../.claude/rules/dev.md) gives the order the work on a plugin goes in.

- [Rn](./rn/)
- [Lane](./lane/)

## The checks on every push

CI runs these checks on every push:

- the linter, the formatter, and the type checker of the checks' own code, and its tests
- the form of each best practice, its Markdown, and the copy of its example
- the style of every figure
- Mermaid's parse of every diagram in the Markdown files
- Claude Code's check of every manifest

Run the checks from the top of the repository:

```console
uv sync --locked
(cd dev/scripts && npm ci --ignore-scripts)
uv run sh dev/scripts/check.sh
```

`uv sync --locked` sets up the tools of `pyproject.toml`'s `dev` group in `.venv`, with
[uv](https://docs.astral.sh/uv/). Run the checks there. `npm ci` sets up
Mermaid's parser in `dev/scripts/node_modules`. Without it, the checks skip the diagrams and say so,
and CI parses them.

Each tool the checks install must match the hashes of the files in its lock, so a version
replaced on PyPI or npm after the lock doesn't install. The Python tools come from `uv.lock`.
`uv lock` makes that file from `pyproject.toml`, with each tool at the newest version that runs on
each Python. Claude Code and Mermaid's parser come from `dev/scripts/package-lock.json`.

## Before each commit and each push

Before each commit, lefthook checks the prose of the files staged and of the commit message by
[lovaizu/checks](https://github.com/lovaizu/checks), at the version that `lefthook.yml` names.
`lefthook.yml` leaves out only the files that no one here writes, such as lockfiles, and the code
of the checks made before the code best practice. CI checks every file the same way.

`dev/scripts/pre-push.sh` runs `sh dev/scripts/check.sh` on each commit pushed, and stops the
push on a failure.

Turn the hooks on once in a clone with `lefthook install`. They need uv on the PATH, and what
[lovaizu/checks](https://github.com/lovaizu/checks#readme) says it needs.
