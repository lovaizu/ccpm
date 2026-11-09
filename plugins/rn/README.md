# `rn`

rn is a Claude Code plugin that builds what you ask for, such as a document, code, or a plugin, so
that the people who use it can do what they need with it.

rn is being rebuilt. This README describes the rebuilt rn, which isn't released yet. Until its release,
the installation below installs the earlier rn 0.9.0, which works differently, and the walkthrough
shows the run that the design of the rebuilt rn lays out, not a recorded run.

rn is for you when you want an AI to build work made of several pieces, such as a feature with its
README and its code, and you'd rather answer a few questions than read and fix drafts. With it, you
hand over work that its users can use without fixes, and rn asks you only what it can't decide
itself.

## Non-goals

- rn doesn't decide your purpose or what you want. When rn leaves a question to you, the work that
  depends on it waits for your answer.
- rn isn't for a quick draft that you'll fix yourself. It plans, builds, and tests each piece, so it
  takes longer than a single prompt to Claude Code.
- rn doesn't merge your work. It commits each piece to a branch and leaves one draft pull request
  for you to merge.

## Requirements

- macOS or Linux: `uname` shows it. No one has tried rn on Windows yet.
- Claude Code 2.1.319 or later: `claude --version` shows it.
- Python 3.9 or later, run as `python3`: `python3 --version` shows it.
- git, and the GitHub command-line tool `gh` signed in to the repository's host: `gh auth status`
  shows it. rn keeps your work in a draft pull request.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install rn@ccpm
```

`claude plugin list` then lists `rn@ccpm`, and `lane@ccpm`, which comes with it.

## Walkthrough

At the end, your tool `tidy` has a dry-run option, and its README shows how to use it. You've
answered two questions and typed `/rn:up` twice.

`tidy` sorts a Downloads folder into subfolders by file type. You want it to show what it would
move before it moves anything. In Claude Code, at the root of its repository, you type:

```text
/rn:up tidy should show what it would move, without moving it
```

rn shows:

```text
Goal: before sorting their Downloads folder with tidy, a user sees what it would move, so that
nothing moves that they didn't intend. Is that what you want?
```

You answer `yes`. rn shows:

```text
Plan, working back from the goal:
1. README.md: describe the dry run in the Walkthrough, so that the code is built to match what
   the reader is told.
2. tidy/cli.py: add the --dry-run option, with tests.

Question 1 of 1 for README.md: should the dry run list each file with its target folder, or only
a count for each folder? Either would work. I recommend listing each file, because users check
file names before they move anything.
```

You answer `each file`. rn updates README.md, and you close Claude Code before it continues. The
next day, in a new conversation, you type:

```text
/rn:up
```

rn shows:

```text
Resuming "tidy shows what it would move" at step 2, tidy/cli.py. README.md is done.
```

Later, rn shows:

```text
Done: README.md and tidy/cli.py are updated, with tests/test_dry_run.py. Each piece was tried as
its users would use it, and meets every item of its kind's checklist.

Decided without asking you:
- The README shows tidy --dry-run before tidy, because users check first.   (README best practice)
- --dry-run prints each move as "<file> -> <folder>", as the README shows.   (README.md)
```

## How it works

![The usual way and rn, with the five problems marked](images/problem.svg)

1. The AI builds the one piece you asked for, and misses the other pieces it needs, or builds them
   in the wrong order.

   rn lists every piece the goal needs and the order to build them in. It plans again after it
   builds each piece and after each answer.

2. The AI starts from scratch and writes what similar texts say, not what its users need.

   rn builds each piece by the best practice for its kind. A best practice states the goal that the
   piece's users reach, a template for the piece, and a checklist of what the users need from it.

3. An AI review produces many findings, and few of them are about whether the work serves its
   users.

   A second AI, the evaluator, tries each piece as its users would, and checks only that
   checklist. rn builds the piece again until it meets every item.

4. The AI asks you what it could find out itself, and guesses what only you know.

   rn asks you one question at a time, and only what the purpose and the best practices leave
   open. It decides the rest, and reports those decisions at the end.

5. The AI follows a step one time and skips it the next, and a new conversation starts the work
   over.

   Lane, a plugin installed with rn, enforces each step on every run. rn keeps the work in your
   repository, so `/rn:up` resumes where it stopped.

### How does rn decide what to ask you?

![rn decides what the purpose or a best practice answers, and asks you the rest](images/how-asks.svg)

When a question comes up while rn builds a piece, rn checks whether the purpose or a best practice
answers it. If one does, rn decides it. If not, rn asks you, one question at a time, and you answer
in your own words. rn then builds the piece again with your answer.

### How can an AI judge another AI's work?

![The evaluator gets the piece and its checklist, never the design](images/how-evaluator.svg)

The evaluator is a separate AI that gets only the piece and the checklist for its kind. It never
gets the design, so it judges by what the piece's users get, not by what its builder intended. rn
weighs each gap that the evaluator finds against your purpose. The generator, the AI that built the
piece, builds it again for each gap that its users would hit, until the piece meets every item.

### How does rn follow every step, every time?

![Lane stops a call that breaks its step, and shows the text of the step](images/how-steps.svg)

Lane watches each tool call that each part of rn makes. When a part breaks a step, such as by
running a command that the step doesn't name, Lane stops the call and shows the part the text of
that step. The part then returns to the step.

### What if the conversation ends partway?

![Each decision and result goes into .rn/, and /rn:up reads it in a new conversation](images/how-resume.svg)

As it works, rn writes each decision and each result to the folder `.rn/<date>-<goal>/` in your
repository. `/rn:up` with no arguments reads that folder and continues from the next step, so you
never answer a question twice.

### What if rn has no best practice for your kind of work?

![For a kind of work rn has no best practice for, rn creates one first](images/how-new-kind.svg)

rn first creates one, by its best practice for writing best practices. It keeps the new one in the
folder `best-practices/` of `.rn/<date>-<goal>/`, and then builds your piece by it.

## Documentation

- [Lane](../lane/README.md): how Lane enforces each step.
- [Changelog](CHANGELOG.md): the changes in each version.
- [Issues](https://github.com/lovaizu/ccpm/issues): where to ask for help or report a bug.

## License

[The `MIT` License](../../LICENSE)

rn's way of asking one question at a time with a recommendation comes from
[grilling](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/productivity/grilling/SKILL.md),
by Matt Pocock, under the `MIT` License in [LICENSE-grilling](LICENSE-grilling).
