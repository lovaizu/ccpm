# turn

turn is a Claude Code plugin that makes a piece of work you ask for, such as a document or code,
until it is what it should be.

With turn, anyone who wants a piece of work made gets it as it should be. They spend their own
effort only on the points that only they can decide. turn decides every other point itself.

For each kind of work, such as a press release, a README or a script, turn first reads how good
ones are made, and draws from them two things for you to approve. The format is the shape of the
work, such as a headline, a lead and a body. The checklist is a set of questions that a work answers
yes to when it serves its readers, such as "Can a reporter tell from the headline what is new?"
turn then asks you what the work is for, and each point only you can decide, one at a time, with
the answer it recommends. turn has a second AI check the work. That AI never sees the design of the
work, so it judges only what the reader gets.

![Claude Code alone and turn, side by side](idea.svg)

**Non-goals**

- turn does not choose what the work is for. It asks you, and builds every other decision on your
  answer.
- turn does not check whether the work does what you want it for, such as whether the RoomBook
  press release gets RoomBook into trade magazines. You check that once you have the work.
- turn does not commit, push, publish or send the work. It gives the work to you, and what happens
  to it next is yours.
- turn is not for a quick draft. Reading how good works of a new kind are made, and having a second
  AI read the work, take longer than asking Claude Code alone. A kind turn has made before skips
  that reading.

## Requirements

- Claude Code.

  turn runs inside it.

- Python 3.9 or later, run as `python3`.

  turn's scripts check its work with it.

- Claude Code allowed to search and read the web, with its WebSearch and WebFetch tools.

  turn reads on the internet how good works of a new kind are made.

## Installation

turn comes from ccpm, a marketplace of Claude Code plugins on GitHub. Add the marketplace, then
install turn:

```console
claude plugin marketplace add lovaizu/ccpm
claude plugin install turn@ccpm
```

`claude plugin list` then shows turn:

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
below, `You:` is what you type, and `turn:` is what turn shows you.

1. Ask for the work, and name turn's agent, `turn:up`:

   ```text
   You:  Have turn:up write a press release for RoomBook, our new meeting-room booking app.
   ```

2. turn confirms the kind of work:

   ```text
   turn: Is this a press release, written for reporters and editors?
   You:  Yes
   ```

3. turn reads guides and examples of good press releases on the internet. It then shows you the
   format and the checklist it drew from them:

   ```text
   turn: Format: headline, lead, body, boilerplate, contact.
         Checklist:
         - Can a reporter tell from the headline what is new?
         - Can a reporter tell from the lead who launches what, and when?
         - Can a reporter check each claim in the body?
         - Can a reporter tell from the boilerplate who the company is?
         - Can a reporter tell from the contact whom to ask, and how?
         Approve?
   You:  Approved
   ```

4. turn asks what this release is for, and then the one point of it that only you can decide:

   ```text
   turn: What is the release for?
   You:  To get RoomBook into trade magazines.
   turn: When is the release date? I recommend the 1st of next month: trade magazines plan
         their issues weeks ahead, and this gives their editors time to place it.
   You:  The 1st of next month.
   ```

5. turn shows the key points it will build the release on:

   ```text
   turn: Key points: a headline on RoomBook's launch; three benefits from RoomBook's README;
         Northwind's PR department as the contact; the release in press/roombook-launch.md.
         Approve?
   You:  Approved
   ```

6. turn writes the release in `press/roombook-launch.md`. The second AI reads it as a reporter
   would and answers each question of the checklist. Where an answer is not yet yes, turn remakes
   the decision behind it. Where an answer stays not yes after that, turn asks you whether to
   change that decision or what the release is for, or to take the release as it is on that
   question. Only when every answer is yes, or one you took as it is, does turn tell you the
   release is done, naming its file and each question you took as it is. The release reads:

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

turn keeps the format and the checklist you approved in `.turn/templates/` in your repository, and
what each run decided in a folder of its own in `.turn/`. Your next press release in this
repository starts from them, so turn skips step 3, the research and that approval. turn ships its
own format and checklist for READMEs, UX documents, architecture documents, code and prompts, so a
work of those kinds skips step 3 from the first time.

## How it works

![How turn works](how-it-works.svg)

An AI asked to review a work lists many faults on its surface. Fixing each fault as it stands only
adds patches. turn prevents this. The evaluator does not list what is missing. It looks only for
what makes the work good. The designer then remakes the decision behind each part that is not yet
good.

After everything the work says is good, turn polishes how the work says it. The evaluator checks
the polished work too.

## Documentation

- [Calling turn](docs/calling.md) tells how a step of another plugin, such as rn, has turn make its
  work.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[turn's development folder](../../dev/turn/README.md) leads to its UX, its architecture and how it
is checked.

## License

[MIT License](../../LICENSE)
