# Building the plugins

Each plugin's product vision and architecture live here. Installing a plugin
copies only its own folder, so nothing here reaches its users' machines.

Each plugin is built as [the rules of plugin development](../.claude/rules/dev.md) say, by
[the plugin guide](plugin-development-guide.md) where its roles work together to make a work.

- [Rn](./rn/)

## The checks on every push

CI runs these checks on every push:

- the linter, the formatter, and the type checker of the plugins' code and the checks' own
- the checks of the code's design: copied code, import cycles, code that nothing uses, and a
  function more complex than one reading can follow
- the form of each best practice
- the style of every figure
- Mermaid's parse of every diagram in the Markdown files
- Claude Code's check of every manifest
- that each plugin works from its own folder, uses another plugin only through `dependencies`, and
  carries its LICENSE, by `dev/scripts/standalone.py`
- the form of each product vision, README, and architecture against its template, by
  `plugins/rn/domain/scripts/template`
- the tag of each decision of each architecture's views, by `dev/scripts/trace.py`
- each plugin's unit tests, and that they run every line and branch of the plugins' code

Each night, CI runs the checks again on the oldest Python and the newest, of `main` and of each
branch an open pull request comes from.

Run the checks from the top of the repository:

```console
uv sync --locked
(cd dev/scripts && npm ci --ignore-scripts)
uv run sh dev/scripts/check.sh
```

`uv sync --locked` sets up the tools of `pyproject.toml`'s `dev` group in `.venv`, with
[uv](https://docs.astral.sh/uv/). Run the checks there. `npm ci` sets up
Mermaid's parser in `dev/scripts/node_modules`. Without it, the check of the diagrams fails and
says how to set it up, as a skipped check would pass a diagram that nobody parsed.

Each tool the checks install must match the hashes of the files in its lock, so a version
replaced on PyPI or npm after the lock doesn't install. The Python tools come from `uv.lock`.
`uv lock` makes that file from `pyproject.toml`, with each tool at the newest version that runs on
each Python. Claude Code and Mermaid's parser come from `dev/scripts/package-lock.json`.

## Before each commit and each push

Before each commit, lefthook checks the English of the Markdown files staged by
[lovaizu/repofiles](https://github.com/lovaizu/repofiles), at the version that `lefthook.yml`
names. Markdown holds what people read and the prompts. The workflow Lint checks every Markdown
file the same way. Before Claude Code runs a `gh issue`
or `gh pr` command, a hook of `.claude/settings.json` checks its title and body. `setup.sh` of
lovaizu/repofiles puts these files, and `lefthook-repo.yml` and `.vale.ini` hold what ccpm
changes.

`dev/scripts/pre-push.sh` runs `sh dev/scripts/check.sh` on each commit pushed, and stops the
push on a failure.

Turn the hooks on once in a clone with `lefthook install`. They need uv on the PATH, and what
[lovaizu/repofiles](https://github.com/lovaizu/repofiles#readme) says it needs.
