# Turn

Turn is a Claude Code plugin that makes a work you ask for, such as a README or a module of code,
ready to use as it comes, and asks you only the decisions that are yours.

Turn is for you when you want an AI in Claude Code to make a work that you will put to use, and you
would rather answer a few points than read and mend a draft. A work is what you want made. Its kind
is the sort of work it is, such as a README. A point is one thing that the work's design must
settle: a fact, such as what your tool prints, or a decision, such as which run a walkthrough
shows. Turn finds each fact itself, and it asks you only the decisions that are yours. It writes the
work into your repository, and you put it to use as it comes. For a quick draft that you would read
and fix yourself, Turn takes longer than asking Claude Code alone.

Turn is also for you if you are an AI that connects a person and Turn, such as a role of another
plugin that carries a larger plan for the person. This README calls such an AI a calling AI. You
hand Turn the work, the points that you have settled with the person, and where the work goes.
Turn keeps those points as given, and it does not ask the person about them again. You pass each
point that Turn gives you to the person as given, and you pass the answer back word for word. You
get back the work, and you pass it on as it is. Turn needs a person to answer: a point that is
theirs waits for them.

Without Turn, you ask an AI for the work in one prompt, or you use an agent that writes the work and
then checks it itself. Either way, the AI fills each gap in your request with a guess. It then
judges its own work by what it meant, not by what the work's user needs. You meet the guesses when
you use the work, and you mend it. Turn instead settles the work's design with you before it makes
anything. It makes the work against the best practice of the work's kind. An AI that did not make
the work then judges it in the place of the one who will use it. Last, Turn refines how the work
reads.

- **A best practice for each kind.** A kind's best practice holds the parts that a good work of the
  kind has and the questions that such a work answers yes to. For each question, it also holds a
  way to make the answer yes. A question asks what the work brings its user, such as "After the
  walkthrough, can the reader tell that the product would give them, on work of their own, the
  gain the opening promised?". Turn ships best practices for READMEs, user experience (UX)
  documents, architecture documents, prompts and code. For a kind that it does not know, Turn
  first works out a best practice from how good works of the kind are made. You approve the
  kind's purpose and its questions before Turn uses them, so the first work of a new kind takes
  longer.
- **The design settled with you first.** The design is the work's purpose with every point settled
  under it. Turn settles it with the plugin [Pin](../pin/README.md). Pin works out each point that
  the questions need, from the purpose down. It shows you each fact that it finds, for you to
  confirm. It settles itself each decision that follows from the purpose and the facts.
  It asks you each decision that is yours, one at a time, with a recommendation. You approve the
  whole design before anything is made.
- **Made against the best practice.** An AI, the generator, makes the work from the design. It
  gives the work the parts that the best practice names. It makes each answer yes in the way that
  the best practice gives for that question.
- **Judged by a fresh AI in the user's place.** Another AI, the evaluator, starts fresh for each
  round. It gets the work and the questions, and never the design, as the work's user never sees
  the design. It uses the work as that user would, and it answers each question with the lines
  that meet it, or with what the user still lacks. Turn takes a question that is not met back to
  the decision behind it, and it settles that decision again. The generator then makes the work
  again from there.
- **Then refined for how it reads.** Once every question is met, the generator and the evaluator go
  round again with the questions of how a document reads, or of how code is written, such as
  whether each sentence reads one way only. Only how the work says a thing changes, and what it
  says stays.

**Non-goals**

- Turn does not check whether the work gets you what you want of it in the world, such as more
  users for your tool. It checks the work against your purpose and the questions of its kind. The
  world's answer is yours to see.
- Turn does not commit, push or publish the work. It writes the files, and you choose what happens
  to them.
- Turn does not decide a point that is yours. A point that you leave unanswered holds the run where
  it is.

## Requirements

- Claude Code 2.1.317 or later: `claude --version` shows its version.
- Python 3.9 or later, run as `python3`: `python3 --version` shows its version.
- Claude Code run as a conversation in a terminal or an app, not as `claude -p`. Turn's AIs work in
  the background, and `claude -p` does not hand their results back to the conversation.

## Installation

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install turn@ccpm
```

`claude plugin list` then lists `turn@ccpm`, and `pin@ccpm`, which is installed with Turn. In a new
Claude Code session, `/turn:up` is then one of its commands.

## Walkthrough

At the end, you have a README for your tool that you commit as it is, and you have answered three
messages from Turn.

This walkthrough is not yet from a real run. It shows what Turn is being rebuilt to show, and a
real run's output replaces it once Turn is built.

Your tool `tidy` sorts a Downloads folder into folders by type. Its repository has the code and no
README. In Claude Code, at the root of the repository, you type:

```text
/turn:up a README for tidy
```

Your words name the kind, a README, so Turn does not ask it. Turn first puts to you the README's
purpose as it reads your words:

```text
Purpose: the README's purpose is what every decision of the README is weighed by.
To-be: one sentence that says who reads the README, and what they do with it.
As-is: your words are "a README for tidy", and the repository has no other document.
Gap: your words do not say who reads the README.
Proposal: someone with a cluttered Downloads folder learns what tidy does, installs it and sorts
their folder with it; yes?
```

You answer `yes`. Meanwhile Turn has read what `tidy` does, and it shows you one fact that it
found, in a message of its own:

```text
Found: tidy/cli.py:22 "parser.add_argument('--dry-run', action='store_true')", so tidy can show
what it would move without moving anything. Is that right?
```

You answer `right`. Turn settles itself what follows from the purpose and the facts, such as
Python 3.9 under Requirements, as `setup.cfg` names it. It then asks you the one decision that they
do not settle:

```text
Purpose: the walkthrough lets a newcomer see what tidy does to a folder like theirs.
To-be: one run whose output shows the reader their files sorted.
As-is: tidy moves files at once, and tidy --dry-run only shows what it would move.
Gap: tidy alone and tidy --dry-run first both show it, and nothing found favors either.
Proposal: tidy --dry-run on a folder of five files, then tidy, so the reader sees what moves
before anything moves; yes?
```

You answer `yes`. When no point is left open, Turn shows you the design:

```text
Goal: someone with a cluttered Downloads folder learns what tidy does, installs it
and sorts their folder.                                                    (you)
- The walkthrough runs tidy --dry-run, then tidy, on five files.           (you)
- Requirements: Python 3.9 or later.                                       (found, you confirmed)
- Non-goals: tidy does not delete files, and does not look inside archives. (found)
...
Do we understand the README the same way?
```

You answer `yes`. The generator makes the README from the design. The evaluator then reads the
README as a newcomer would, with only the README and the questions of a README. It finds one
question not met: after the walkthrough, a newcomer cannot tell where `tidy` puts a file with no
extension. Turn takes that back to the decision on the walkthrough's run, adds such a file to the
five, and has the README made again. The evaluator then finds every question met. The generator
and the evaluator go round once more with the questions of how a document reads. In that round,
the generator splits two sentences that each made two points. Turn ends:

```text
Done: README.md is written, and not committed. It meets every question of a README and of how a
document reads. .turn/20261103-tidy-readme/verification/ shows the lines that meet each question.
```

`README.md` begins:

```markdown
# tidy

tidy is a command-line tool that sorts your Downloads folder into folders by type.

tidy is for you when your Downloads folder holds hundreds of files and you want them sorted
without dragging each one by hand.
```

You answered three messages: the purpose, one fact and one decision. Turn settled every other point
itself, and the design shows each one. You read the README, and you commit it as it is.

## How it works

![How Turn works](images/how-it-works.svg)

The figure shows how you and a calling AI use Turn, and what each part of Turn does. Three points
lie outside the figure:

- Turn keeps each run in a folder of its own, such as `.turn/20261103-tidy-readme/`. The folder
  holds `design-tree.json` and each check of the work. A run that stopped, such as when the session
  ended, goes on from its folder with `/turn:up .turn/20261103-tidy-readme`. To change a work that
  Turn made, name its folder and the change, such as
  `/turn:up .turn/20261103-tidy-readme the walkthrough should use ten files`. Turn takes the change
  in through the design.
- Turn keeps the best practice of a kind that is new to it in `.turn/best-practices/`. Later runs in
  the same repository use it.
- Each AI in the figure is a subagent: a Claude Code agent that works apart from your conversation
  and ends with its result. The checks of [Lane](../lane/README.md) hold each subagent to its
  steps, such as the evaluator reading only the work and the questions.

## Documentation

- [Calling Turn](docs/calling.md): for a calling AI, what it hands Turn, how it passes Turn's points
  on to the person, and what it gets back.
- [The changelog](CHANGELOG.md): the changes in each version.

## Development

[Turn's development folder](../../dev/turn/README.md) holds its UX, its architecture and its tests.

## License

[MIT License](../../LICENSE)
