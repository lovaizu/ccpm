# writ

What writ must achieve, how each quality is checked, and how writ is built are in
[writ design](design.md).

- Tests: `python3 -m unittest discover -s dev/writ/tests` from the top of the repository.
- Trial: `python3 dev/writ/trials/run.py <new folder> <what the user knows> <first message> <files>
  ...` runs writ in a new repository made from the folders of files, such as
  [csvtidy](trials/csvtidy/), with the writ and turn of this working tree, and has another Claude
  answer each question as a user who knows only what [the user's file](trials/csvtidy-user.md)
  says. Judge the run from the records of its conversation and agents, which Claude Code keeps
  under `~/.claude/projects/`.
