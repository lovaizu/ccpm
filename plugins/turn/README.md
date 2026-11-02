# Turn

Turn is a Claude Code plugin that makes a deliverable you ask for, such as a document or code, by
the best practice of its kind.

With Turn, you get a deliverable that serves the one it is for, and you spend your own effort only
on the points that only you can decide.

The best practice of a kind of deliverable is spread over many guides and examples. Turn refines it
to the least that is needed, and keeps the result for each kind:

![Best practice refined into a standard and a practice](idea.svg)

The Standard's Goal says who uses such a deliverable and for what, its Template gives the shape, and
its Checklist asks the questions that a good deliverable answers yes to. The Practice's design tree
splits what to decide from the goal down, the same for every kind, and its way for each question
decides what makes that question yes. The Standard alone judges the deliverable, because its reader
gets only the deliverable: one made by the Practice can still fall short.

**Non-goals**

- Turn does not check whether the deliverable gets you what you want it for, such as whether the
  RoomBook press release gets RoomBook into trade magazines. You check that once you have it.
- Turn is not for a quick draft. Refining the best practice of a new kind, and having a second AI
  read the deliverable, take longer than asking Claude Code alone. A kind Turn has made before skips
  the refining.

## Requirements

- Claude Code.

  Turn runs inside it.

- Python 3.9 or later, run as `python3`.

  Turn's scripts check its deliverables with it.

- Claude Code allowed to search and read the web, with its WebSearch and WebFetch tools.

  Turn reads the best practice of a new kind on the internet.

## Installation

Turn comes from ccpm, a marketplace of Claude Code plugins on GitHub. Add the marketplace, then
install Turn:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install turn@ccpm
```

`claude plugin list` then shows Turn:

```console
$ claude plugin list
Installed plugins:

  ❯ turn@ccpm
    Version: 0.1.0
    Scope: user
    Status: ✔ enabled
```

## Walkthrough

It is November 2026, and your company, Northwind, launches RoomBook, a meeting-room booking app.
You need a press release for it. RoomBook's README, in the repository you have open in Claude
Code, says what the app does, who Northwind is and how to reach its PR department. In the lines
below, `You:` is what you type, and `turn:` is what Turn shows you.

1. Ask for the deliverable, and name Turn's agent, `turn:up`:

   ```text
   You:  Have turn:up write a press release for RoomBook, our new meeting-room booking app.
   ```

2. Turn confirms the kind of deliverable:

   ```text
   turn: Is this a press release, written for reporters and editors?
   You:  Yes
   ```

3. Turn reads guides and examples of good press releases on the internet. It then shows you the
   Standard it refined from them:

   ```text
   turn: Standard for a press release
         Goal: a reporter decides from the release whether to write about it.
         Template: headline, lead, body, boilerplate, contact.
         Checklist:
         - Can a reporter tell from the headline what is new?
         - Can a reporter tell from the lead who launches what, and when?
         - Can a reporter check each claim in the body?
         - Can a reporter tell from the boilerplate who the company is?
         - Can a reporter tell from the contact whom to ask, and how?
         Approve?
   You:  Approved
   ```

4. Turn asks what this release is for, and then the one point of it that only you can decide:

   ```text
   turn: What is the release for?
   You:  To get RoomBook into trade magazines.
   turn: When is the release date? I recommend the 1st of next month: trade magazines plan
         their issues weeks ahead, and this gives their editors time to place it.
   You:  The 1st of next month.
   ```

5. Turn shows the key points it will build the release on:

   ```text
   turn: Key points: a headline on RoomBook's launch; three benefits from RoomBook's README;
         Northwind's PR department as the contact; the release in press/roombook-launch.md.
         Approve?
   You:  Approved
   ```

6. Turn writes the release in `press/roombook-launch.md`. A second AI reads it as a reporter would
   and answers each question of the checklist. Turn makes again each decision behind an answer
   that is not yet yes, and asks you only where that is not enough. When every answer is yes, Turn
   tells you the release is done. The release reads:

   ```text
   turn: Northwind's RoomBook offers only the meeting rooms that fit your meeting

         Northwind launches RoomBook, a meeting-room booking app, on 1 December 2026.
         RoomBook matches each room's seats and equipment to the meeting you describe.

         With RoomBook, an office worker:
         - books a room with the seats and equipment the meeting needs;
         - sees at once which of those rooms are free for the time they need;
         - books it without asking anyone.

         About Northwind: Northwind makes software that helps offices run.

         Contact: Northwind PR department, pr@northwind.example
   ```

Turn keeps the Standard you approved, and the Practice it refined, in `.turn/kinds/` in the folder
you run Claude Code in, so your next press release skips step 3. Turn ships both for READMEs, UX
documents, architecture documents, code and prompts, so those kinds skip step 3 from the first time.

## How it works

![How Turn works](how-it-works.svg)

Turn has separate AIs plan, make and judge the deliverable, as Anthropic's "Harness design for
long-running application development" (2026) does with a planner, a generator and an evaluator. The
designer decides from this deliverable's purpose down: it splits what must hold until a fact or you
settle each point, and decides each by the Practice. It asks your points one at a time, each with
the answer it recommends.

The evaluator, the second AI, did not make the deliverable. For each question, the evaluator says
only what the reader gets once it is good, not a list of faults. Turn then makes again the decision
behind it, so the deliverable is never patched. Once what the deliverable says is good, Turn betters
how it says it, and the evaluator checks that too.

## Documentation

- [Calling Turn](docs/calling.md) tells how a step of another plugin, such as Rn, has Turn make its
  deliverable.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[Turn's development folder](../../dev/turn/README.md) leads to its UX, its architecture and how it
is checked.

## License

[MIT License](../../LICENSE)
