# turn

What turn must achieve, how each quality is checked, and how turn is built are in
[turn design](./design.md).

- Tests: `python3 -m unittest discover -s dev/turn/tests` from the top of the repository.
- Trial: `python3 dev/turn/trials/run.py <new folder> <task> <out name> [<answer> ...]` runs turn on
  a fresh clone of this repository, with the turn of this working tree, on a task such as
  [dev-readme.json](./trials/dev-readme.json), and answers each question turn asks with the next
  answer given. Commit first, since the clone holds only what is
  committed. Judge the run from the records of its conversation and agents, which Claude Code keeps
  under `~/.claude/projects/`.
