# Building the plugins

Each plugin's design, tests and trials live here. Installing a plugin copies only its own folder, so nothing here reaches its users' machines.

- [turn](./turn/)
- [rn](./rn/): its design and verification document are in [rn/docs/](../rn/docs/), where a
  session of rn itself would keep them.

Every check CI runs on a push, the linter, the formatter, the type checker, and each plugin's tests with the lines and branches they run counted, and Claude Code's check of every manifest, is run by `sh dev/check.sh` from the top of the repository, in a virtual environment made with `pip install -r dev/requirements.txt`. A `coverage` installed outside one does not count the scripts the tests start as separate processes.

The rules for building, testing, trying and releasing a plugin are in [.claude/rules/plugin.md](../.claude/rules/plugin.md).
