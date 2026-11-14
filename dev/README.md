# Building the plugins

Each plugin's product vision and architecture live here. Installing a plugin
copies only its own folder, so nothing here reaches its users' machines.

Every plugin takes from [the plugin guide](plugin-development-guide.md) what its requirements call
for, and starts from [the plugin template](plugin-template/).
[.claude/rules/dev.md](../.claude/rules/dev.md) gives the order the work on a plugin goes in.

- [Rn](./rn/)
- [Lane](./lane/)

## The checks on every push

CI runs these checks on every push:

- the linter, the formatter, and the type checker of the checks' own code, and its tests
- the checks of the code's design: copied code, and a function more complex than one reading can
  follow
- the form of each best practice, its Markdown, and the copy of its example
- the style of every figure
- Mermaid's parse of every diagram in the Markdown files
- Claude Code's check of every manifest
- the tests of the trial driver and of the double of Claude Code, and that they run every line and
  branch of each

Two more runs check the tests, not the change, as
[the architecture best practice](../plugins/rn/domain/best-practices/architecture/best-practice.md)
times them, and no work waits on them:

- On every push, `dev/scripts/quality.sh` runs mutation testing over the lines of each plugin's
  code that the push changed, and the plugin's property-based tests. A plugin's code comes under
  them once `dev/<plugin>/cosmic-ray.toml` names it.
- Each night, CI runs every check over the whole, of `main` and of each branch an open pull request
  comes from, where the branch holds these checks: every mutant of each plugin's code, and the
  property-based tests at their most inputs, among them.

`sh dev/scripts/ci-fix.sh <branch>...` watches both on the branches that the work goes on in,
and has Claude Code mend their failures by the brief of [ci-fix.md](scripts/ci-fix.md). For each
branch, it mends every failure at once on the branch's head, on a branch `ci-fix/<branch>-<head>`.
Merge that branch into yours once you've checked it: the next fix of your branch waits until then.
Start it once and leave it running. It reads a nightly run's failure the next time it runs.

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

## The product vision trials

`dev/scripts/trial.py` runs a product vision trial of a plugin from a trial file on the real Claude
Code, and keeps the run's records, from which the plugin's product vision test counts its key
results. The opening of the script says how to run it and what it reads and keeps.

## Before each commit and each push

Before each commit, lefthook checks the English of the Markdown files staged by
[lovaizu/repofiles](https://github.com/lovaizu/repofiles), at the version that `lefthook.yml`
names. Markdown holds what people read and the prompts. The workflow Lint checks every Markdown
file the same way. Before Claude Code runs a `gh issue`
or `gh pr` command, a hook of `.claude/settings.json` checks its title and body. `setup.sh` of
lovaizu/repofiles puts these files, and `lefthook-repo.yml` and `.vale.ini` hold what ccpm
changes.

`dev/scripts/pre-push.sh` runs `sh dev/scripts/check.sh` on each commit pushed, and stops the
push on a failure. It leaves `dev/scripts/quality.sh` to CI.

Turn the hooks on once in a clone with `lefthook install`. They need uv on the PATH, and what
[lovaizu/repofiles](https://github.com/lovaizu/repofiles#readme) says it needs.
