# overnight

overnight is a Claude Code plugin that keeps work from stopping by usage limits, unanswered prompts,
or closed sessions.

In development: overnight has no release yet, so nothing here runs, and this README draws what it
builds toward.

overnight is for you when you're an AI, such as Claude Code, given work that outlasts the person's
stay. With it, you have that work run on in pieces through the usage limit, unanswered prompts, and
your session's end.

## Non-goals

- overnight doesn't get past the usage limit sooner, such as by another account: it waits for each
  reset.
- overnight doesn't let a piece ask anyone anything while it runs: settle each question in its
  prompt.
- overnight doesn't run while the computer is off or asleep: the person leaves it on and awake.

## Requirements

- Claude Code: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- A Git repository that holds the work: at its root, `git rev-parse --show-toplevel` shows its
  folder.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install overnight@ccpm
```

In the person's next session, the skill `overnight:status` shows `No pieces yet`.

## Walkthrough

At the end, you have three issues fixed on their own branches, though the limit came and your
session closed.

This run draws what overnight builds toward, as no release of overnight runs it yet. At 23:00, in
a Python app's repository, the person types:

```text
Fix issues #12, #15, and #18 while I sleep. Each has a failing test. I'll review the branches in the morning.
```

You read the issues and settle each question in each piece's prompt, as no one answers while the
pieces run. For #12, you invoke the skill `overnight:ask` with:

```text
Fix issue #12: parse_date raises on "2026-02-29 00:00". Make tests/test_dates.py::test_leap_day pass, and change no other test. Run pytest to check, then commit on this branch.
Tools: Read, Edit, Bash(pytest:*), Bash(git add:*), Bash(git commit:*)
```

overnight shows:

```text
Piece 1 runs in the background, apart from this session.
Folder: ../myapp-overnight-1, on the branch overnight/1
Tools: Read, Edit, Bash(pytest:*), Bash(git add:*), Bash(git commit:*)
/overnight:status shows how it goes.
```

You hand over #15 and #18 the same way and tell the person:

```text
Three pieces run in the background, each on its own branch. They go on after you close this session, and wait out the usage limit if it comes.
```

The person closes the session. At 07:00, in a new session, the person asks how the night went. You
invoke the skill `overnight:status`, and overnight shows:

```text
Piece  State  Branch       Waited                       Last words
1      done   overnight/1  -                            Fixed parse_date for leap days. 214 tests pass.
2      done   overnight/2  usage limit, 01:12 to 04:00  Kept the CSV header in its column order. 214 tests pass.
3      done   overnight/3  usage limit, 01:12 to 04:00  Added the --dry-run flag. 216 tests pass.

0 of 3 pieces stopped by the usage limit, a wait for an answer, or the session closing.
```

You and the person review the three branches, each with its tests passing.

## How it works

overnight keeps each piece from stopping by the usage limit, a wait for an answer, or your session
closing.

![How overnight keeps each piece from stopping by the usage limit, a wait for an answer, or the session closing](images/how-it-works.svg)

### Does the work go on once the usage limit stops it at 01:00?

A piece that the limit stops goes on in its conversation after each reset, however often the limit
comes back. So the piece works through the hours after the limit, with no one there to restart it.

### Does the work sit all night at a prompt that no one answers?

Each piece gets the tools you name and a Git worktree of its own up front, so no prompt waits.
Without asking anyone, overnight refuses each call to a tool you didn't name, so name each tool the
piece needs.

### Does the work end when your session closes?

Each piece runs as a process apart from your session, so closing the session leaves it running. In
any later session, the skill `overnight:status` shows where each piece stands.

### Can a piece do more than you let it?

No. A piece runs with only the tools you named, and its changes stay on its branch until merged.

## Documentation

- [Issues](https://github.com/lovaizu/ccpm/issues): where you or the person ask for help or report a
  fault.

## License

[MIT](LICENSE)
