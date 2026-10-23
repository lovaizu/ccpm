# Building the plugins

Each plugin's architecture, tests and trials live here. Installing a plugin copies only its own folder, so nothing here reaches its users' machines.

Every plugin is built on [how a plugin works](./architecture.md).

- [turn](./turn/)
- [rn](./rn/)
- [lane](./lane/): also the tests of `hook.py` and `shell.py`, the hook code the plugins share, and `testing.py`, what their tests share

Every check CI runs on a push, the linter, the formatter, the check for code copied between files, the type checker, and each plugin's tests with the lines and branches they run counted, and Claude Code's check of every manifest, is run by `sh dev/check.sh` from the top of the repository, in a virtual environment made with `pip install --require-hashes -r dev/requirements.txt`. A `coverage` installed outside one does not count the scripts the tests start as separate processes.

Every tool the checks install is held to the hashes of the files it was locked with, so a version replaced on PyPI or npm after it was locked does not install: each `dev/requirements*.txt` is made from its `.in` by the `pip-compile` command at its top, `requirements.txt` on Python 3.9 and `requirements-test-quality.txt` on the newest, and Claude Code comes from `dev/package-lock.json`.

On the newest Python, CI also installs `dev/requirements-test-quality.txt`, which runs the check for copied code and the property tests in `sh dev/check.sh`, many inputs each in CI and few elsewhere, and runs `sh dev/mutate.sh`, the mutation testing of each plugin with a `dev/<plugin>/cosmic-ray.toml`, each plugin in a job of its own. `sh dev/check.sh <plugin>` and `sh dev/mutate.sh <plugin>` check that plugin alone, and `sh dev/mutate.sh --since <commit> <plugin>` only the mutants on the lines changed since that commit.

Before each push, `dev/githooks/pre-push` runs both on the commits pushed, for each plugin the push changes, or every plugin where it changes what they all stand on, such as lane's `hook.py` and `shell.py`, the mutation testing on the lines changed alone, and stops the push on a failure. It is turned on once in a clone by `git config core.hooksPath dev/githooks`, and needs the virtual environment's bin first on PATH.

The rules for building, testing, trying and releasing a plugin are in [.claude/rules/plugin.md](../.claude/rules/plugin.md).
