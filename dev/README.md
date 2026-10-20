# Building the plugins

Each plugin's design, tests and trials live here. Installing a plugin copies only its own folder, so nothing here reaches its users' machines.

- [turn](./turn/)
- [rn](./rn/)
- [common](./common/): the tests of `common/`, the code the plugins share, and `testing.py`, what their tests share

Every check CI runs on a push, the linter, the formatter, the type checker, and each plugin's tests with the lines and branches they run counted, and Claude Code's check of every manifest, is run by `sh dev/check.sh` from the top of the repository, in a virtual environment made with `pip install --require-hashes -r dev/requirements.txt`. A `coverage` installed outside one does not count the scripts the tests start as separate processes.

Every tool the checks install is held to the hashes of the files it was locked with, so a version replaced on PyPI or npm after it was locked does not install: each `dev/requirements*.txt` is made from its `.in` by the `pip-compile` command at its top, `requirements.txt` on Python 3.9 and `requirements-test-quality.txt` on the newest, and Claude Code comes from `dev/package-lock.json`.

On the newest Python, CI also installs `dev/requirements-test-quality.txt`, which runs the property tests in `sh dev/check.sh`, and runs `sh dev/mutate.sh`, the mutation testing of each plugin with a `dev/<plugin>/cosmic-ray.toml`. `sh dev/mutate.sh <plugin>` tests that plugin alone, and CI tests them all.

Before each push, `dev/githooks/pre-push` runs `sh dev/check.sh` and the mutation testing of each plugin the push changes, on the commits pushed, and stops the push on a failure. It is turned on once in a clone by `git config core.hooksPath dev/githooks`, and needs the virtual environment's bin first on PATH.

The rules for building, testing, trying and releasing a plugin are in [.claude/rules/plugin.md](../.claude/rules/plugin.md).
