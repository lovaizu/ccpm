# rn

rn is a Claude Code plugin that makes what you ask for so the people it's for can use it.

In development: this README describes the rebuilt rn, which isn't built yet, so don't install rn
for your work.

rn is for you when you have Claude Code make something in a GitHub repository for other people to
use. With it, you get each deliverable you mean, one its people can use, and answer only what's
yours.

## Non-goals

- rn doesn't put the deliverable in front of real people: its AI subagents read it as they would.
- rn doesn't finish alone where your goal leaves a question open: it asks you, and other work goes
  on.
- rn doesn't make a small change faster than Claude Code alone: for a one-line fix, ask Claude Code.
- rn doesn't merge: it leaves one pull request, ready once you sign off the last deliverable.

## Requirements

- macOS or Linux: `uname` shows it.
- Claude Code 2.1.319 or later: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- Git: `git --version` shows it.
- The GitHub command-line tool `gh`, logged in: `gh auth status` shows `Logged in to github.com`.
- A GitHub repository you can push to: at its root, `gh repo view --json viewerPermission` shows
  `WRITE`, `MAINTAIN`, or `ADMIN`.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install rn@ccpm
```

At your repository's root in Claude Code, `/rn:up` alone says that rn has no run to pick up.

## Walkthrough

At the end, you have a pull request, ready to merge, that adds a command and its guide for your
accounting team.

`invoicer`, a Python library that your team calls, renders invoices. Your accounting team writes no
Python, so they ask a developer for each invoice. You type:

```text
/rn:up a command with which the accounting team prints an invoice from its lines, without writing Python
```

rn shows:

```text
The goal, as I'd put it:
  The accounting team prints each invoice themselves from the lines they keep in a
  spreadsheet, without asking a developer.
Is that what you're after?
```

You type:

```text
yes
```

rn shows:

```text
A question that's yours:
  Should the tax rate be given with each invoice, or set once?
  I recommend setting it once, as the rate rarely changes.
```

You type:

```text
with each invoice
```

rn shows:

```text
The plan, for your sign-off:
  1. A command that prints an invoice from a file of its lines, with the tax rate given each time
  2. A guide from which the accounting team prints an invoice on its own
/rn:ty to approve, or /rn:gm with what to change.
```

You type:

```text
/rn:ty
```

rn makes both deliverables. That evening, before rn finishes, you type:

```text
/rn:dn
```

rn shows:

```text
Paused "invoices for the accounting team" while making "A command that prints an invoice
from a file of its lines".
Its work so far is pushed. Type /rn:up in any conversation to go on.
```

The next day, in a new conversation, you type:

```text
/rn:up
```

rn shows:

```text
Picking up "invoices for the accounting team", making "A command that prints an invoice
from a file of its lines", where it stopped.
```

Later, rn shows:

```text
"A command that prints an invoice from a file of its lines", for your sign-off:
  What its people can do with it: anyone at a terminal prints an invoice from a file of
  its lines with one command.
  Decisions I took without asking:
  - Read each line as invoicer already does, description;price;quantity, which a
    spreadsheet saves as CSV with semicolons.
  Changes: https://github.com/<owner>/invoicer/pull/12/files
/rn:ty to approve, or /rn:gm with what to change.
```

You type:

```text
/rn:ty
```

rn puts up the guide in the same form, and you type `/rn:ty` again.

rn shows:

```text
Done. The pull request is ready for your merge: https://github.com/<owner>/invoicer/pull/12
```

On the pull request's branch, a colleague from accounting follows the guide alone, saves the lines
from their spreadsheet as `lines.csv`, and types:

```console
$ python3 -m invoicer lines.csv --rate 0.19
Hosting                              40.00 EUR
Support hours                       120.00 EUR
Subtotal                            160.00 EUR
Tax                                  30.40 EUR
Total                               190.40 EUR
```

You then merge the pull request.

## How it works

rn works only on the few things that decide whether a deliverable's people can use it.

![How rn works, from your decisions to the pull request you sign off](images/how-it-works.svg)

### "I can't spell out every detail up front, so it builds the wrong thing."

rn asks only the decisions that change what the people get, one at a time, each with a
recommendation. You sign off the plan and each deliverable, so you get what you mean without a
specification.

### "Its output misses what this kind of work needs."

rn plans and makes each deliverable by the best practice of its kind, such as one for a README.
Where it has none for a kind, it makes one first, and lists what each settled without asking.

### "It looks done, but the people it's for can't use it."

AI evaluators read each deliverable with only what its people have, never what rn meant. rn makes
it again until they find each aim met, so you get one they can use.

### "Each fix breaks something else."

rn takes each shortfall back to the decision it comes from, and makes the deliverable again from
the decisions. A shortfall the people would never meet changes nothing, so the deliverable doesn't
grow with each round.

### "Does it skip a step when no one watches?"

No. Lane, installed with rn, stops any part of rn that leaves its steps, and shows it its step.

### "Does it change the repository's files, or merge on its own?"

No. rn works in its own worktree and branch, runs commands in a throwaway copy, and leaves the
merge to you.

## Documentation

- [Changelog](CHANGELOG.md): for you after an update, the changes in each version.
- [Lane](https://github.com/lovaizu/ccpm/blob/main/plugins/lane/README.md): for you if you want to
  know what Lane does, or use it in a plugin of your own.
- [Issues](https://github.com/lovaizu/ccpm/issues): where you ask for help or report a fault.

## License

[MIT](LICENSE)
