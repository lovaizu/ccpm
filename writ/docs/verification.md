# writ verification

Run these after any change to `writ`: the scene checks that its first user still reads its own
saved output, and the machine checks also check that it still reads nothing of how the work was
made and that other agents are still left unchecked.

## Where a run starts

- A fresh git repository in a temporary directory outside the ccpm repository, holding only the
  scene's files.
- `writ` from the branch under test, loaded with
  `claude -p --plugin-dir <path to writ> --permission-mode auto`, so the first user runs the scene's
  script without asking for approval. writ's hook still decides before the permission mode, so the
  run still shows whether it stops a read.
- Claude Code 2.1.291 or later.

## How a run goes

- Each scene's trial in `dev/writ/trials/` starts the `writ:first-user` agent directly, without
  running `/writ:pith` first, and hands it what pith's conductor would: the location of the work,
  its receiver and purpose, the location of the essentials file, and the language of its report.
- The trial leaves for the maintainer the first user's report and the first user's own conversation
  record. When Claude Code saves a long output, that record holds a tool result reading "Full output
  saved to: <path>", the path the first user then reads. A stop by writ's hook shows in that record
  with its reason, which begins "writ: the first user does not read how the work was made".
- The maintainer sets what happened beside the scene's "Passes when", then deletes the temporary
  directory by its exact path.

## Scenes

### A1: A writ first user reads the whole of what its own tool calls returned, even when Claude Code saved it to a file for being too long, and goes on using the work without a detour

- The scene's repository holds `print_log.py`, which prints a log of 40,000 entries, one per line,
  where three entries, all after entry 30,000, read `entry <n>: FAILED: <reason>` with a different
  reason each, and every other entry reads `entry <n>: ok`. The script picks the three entries and
  builds their reasons from a fixed random seed as it runs, so neither shows in its source and the
  answer can be learned only from the output; the maintainer learns it by running the script. The
  repository also holds `essentials.md`, with the one question "Run `python3 print_log.py` as
  written, with nothing added to the command, as its receiver runs it: which entries failed, and
  what does the log say about each?", so that Claude Code saves the output. The first user is
  handed `print_log.py` as the work; as its receiver and purpose, someone who runs it to find which
  entries failed; `essentials.md` as the essentials file; and English as the report language. It is
  told nothing about which tools to use to read the output, or about a saved file.

    Passes when Claude Code saves the first user's run of the script to a file, the first user reads
    that saved file by Read, Grep or Bash on its path, writ's hook does not stop the read, and the
    report names the three failed entries, quoting the saved output, without the first user running
    the script again to see its output another way. If the output was not saved, or the first
    user never tried to read the saved file, the run showed nothing about A1; run it again.

## Machine checks

After every change to writ, run the tests from the repository root, with Python 3.9 and
`coverage` installed by `pip install "coverage>=7.10"`, as CI does:
`coverage run --source=writ -m unittest discover -s dev/writ/tests`, then `coverage combine` and
`coverage report`; `.coveragerc` fails the report below 100%. The run leaves `.coverage` in the
repository root, which no `.gitignore` hides; delete it by that path once the report is read. The
tests check the following.

- A1: The first user's own saved output is let through, by Read, by Grep and by Bash.
- M1: Another agent's saved output, another first user's included, is stopped, even when its path
  is written with `~` or `..`.
- M1: The first user's own saved output is let through when its path is written with `~` or `..`.
- M1: A conversation record is stopped.
- M1: A path beside the first user's own saved output, a folder included, is stopped.
- M1: A path that is in the first user's own conversation record only because it typed the path
  in a call or a command printed it, not because Claude Code recorded it as saved output, is
  stopped.
- M1: A call is stopped when the hook cannot find or read the first user's own conversation record,
  which is what shows a saved file is its own.
- M2: Agents other than `writ:first-user` are not checked.
- Every line of writ is run by the tests, as `coverage report` shows.
