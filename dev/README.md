# Building the plugins

Each plugin's architecture, tests and trials live here. Installing a plugin copies only its own folder, so nothing here reaches its users' machines.

Every plugin is built on [how a plugin works](./architecture.md).

- [turn](./turn/)
- [rn](./rn/)
- [lane](./lane/): also `testing.py` and `trials/trying.py`, what every plugin's tests and trials share

The checks CI runs on every push, the linter, the formatter, the check of the Markdown for plain English, the type checker, each plugin's unit tests with the lines and branches they run counted, and Claude Code's check of every manifest, are run by `uv run sh dev/check.sh` from the top of the repository, [uv](https://docs.astral.sh/uv/) setting up the tools of `pyproject.toml`'s `dev` group in `.venv` with `uv sync --locked`. A `coverage` installed outside a virtual environment does not count the scripts the tests start as separate processes.

Every tool the checks install is held to the hashes of the files it was locked with, so a version replaced on PyPI or npm after it was locked does not install: the Python tools come from `uv.lock`, made from `pyproject.toml` by `uv lock`, each at the newest version that runs on each Python, Claude Code from `dev/package-lock.json`, and Vale, which is not on PyPI, from its GitHub release by `sh dev/vale.sh`, which holds the sha256 Vale published for each archive.

On the newest Python, CI also installs the `test-quality` group, by `uv sync --locked --group test-quality`, which runs the check for copied code in `sh dev/check.sh`, and runs `sh dev/properties.sh`, the property tests, many inputs each in CI and few elsewhere, and `sh dev/mutate.sh`, the mutation testing of each plugin with a `dev/<plugin>/cosmic-ray.toml`, as [Unit tests: code](./architecture.md#unit-tests-code) says. `sh dev/check.sh <plugin>`, `sh dev/properties.sh <plugin>` and `sh dev/mutate.sh <plugin>` check that plugin alone, and `sh dev/mutate.sh --since <commit> <plugin>` only the mutants on the lines changed since that commit.

Before each push, `dev/githooks/pre-push` runs `sh dev/check.sh` on the commits pushed, for each plugin `sh dev/changed.sh` names, those the push changes or that link a file it changes, or every plugin where it changes what they all stand on, or `sh dev/prose.sh` alone where it names none and the push changes Markdown, and stops the push on a failure; the property tests and the mutation testing run in CI. It is turned on once in a clone by `git config core.hooksPath dev/githooks`, and needs uv on PATH.

`sh dev/prose.sh` checks the Markdown with [Vale](https://vale.sh), by the [Google developer documentation style](https://github.com/vale-cli/Google) and ccpm's own words, so that someone who has not followed the work can read each document plainly. Add a term the documents may use, such as a plugin's name, to `dev/vale/styles/config/vocabularies/ccpm/accept.txt`. Add a word a reader stops at to `dev/vale/styles/ccpm/Substitutions.yml`, with the plain words to use instead. `.vale.ini` gives the reason for each rule it turns off. It also lists the files written before the check came in: for those files alone, Vale skips the rules on passive voice, semicolons, acronyms and ccpm's words, until someone rewrites a file and takes it off the list.

The order the work on a plugin goes in is in [.claude/rules/dev.md](../.claude/rules/dev.md).
