# turn

What turn must achieve, how each quality is checked, and how turn is built are in
[turn design](./design.md).

- Tests: `python3 -m unittest discover -s dev/turn/tests` from the top of the repository. To count
  the lines they run as CI does, run them under `coverage` installed in a virtual environment, since
  one installed for the user does not count the scripts the tests start as separate processes.
- Trial: `python3 dev/turn/trials/run.py <new folder> <task> <out name>` runs turn on a fresh clone
  of this repository, with the turn of this working tree, on a task such as
  [dev-readme.json](./trials/dev-readme.json). Commit first, since the clone holds only what is
  committed. Judge the run from the records of its conversation and agents, which Claude Code keeps
  under `~/.claude/projects/`.
