# Changelog

## [Unreleased]

### Added

- A plugin's step can call `writ:up`, from a subagent too, and gets back in a file the document with its report, or the points only it can decide, each with writ's recommended answer — anything a plugin makes goes through writ, with no one there to answer.
- A checklist writ makes for a kind it has none for is kept at `.writ/checklists/<kind>.md` and used from then on — a kind you write again is held to what it needs, and your team shares it by committing it.
- A checklist for code and its tests (`code`): tests held to what the README and the design ask and seen failing, each told in Given / When / Then, each failure naming the one behavior that broke, every branch run, static checks and one style by tool, and stops that say what went wrong and what to do — code and tests are made and judged by one measure, as documents and prompts are.
- What the document must say, item by item of its checklists, is written to `.writ/content/<folder>/<name>.content.md` before turn writes — each item met traces back to what was asked of it, and a later call settles points from it.
- The report puts first what writ decided for you, each with its ground, every question or item turn left with why, and each line writ changed after turn — you judge from the report what is yours to decide, and open the document only where you doubt it.
- A page on what lies past the first document, a document you already have and a kind writ has no checklist for — the README keeps to deciding and starting.

### Changed

- `/writ:up` looks up what the repository and the sources show, asks you only what the document's purpose needs and only you can decide, one question at a time with a recommended answer, then has turn write the document, read it as its reader and check it, judges what turn returns by the purpose and finishes it itself, running turn again only when what it was given must change — you answer once, before the writing, leave writ at work, and get the document with its report.
- Every checklist asks one thing per item, each item asks what the reader or user gets rather than what is in the work, and each sits in the section its kind of question belongs to — a no names the one thing that falls short, and anyone judging gets the same answer.
- Every checklist opens with who reads such work and what they can then do, and holds only the conditions of that; an item that only adds a part is gone: the README's "what it is" sits inside what the reader gains, a figure of who does what is asked only where several act in turn, and a design names no invariant or cost for each approach — a document made to the checklist carries nothing its reader does not use.
- writ needs turn, which installing writ installs, and Python 3.9 and jq, which turn needs — the writing, reading and checking are turn's, done one way for every plugin.
- The README checklist asks for an opening that says what the reader gains and whom it is for, an example that shows only what the reader does and gets back, why to choose it in its own section after the example, a reason for a requirement only where the reader could not see it, and nothing beyond deciding and getting to the first result, which goes to pages reached from Documentation — a README reads as the ones people are used to, and no longer buries what it gives under how the product works.
- A checklist's version goes up once for each release, not on every edit — a version names text people judged by, and drafts in between take no number.
- The design checklist asks for the principles, the approach to each promise and the whole in one figure, that a design leave out a case a principle settles, that each check show one quality in the smallest situation that shows it, and that the flow be checked apart from what each part makes — a design holds the way of thinking and who takes part, and a failing check says which quality broke.
- The prompt checklist asks that each step be an instruction to act rather than a rule, said in positive terms, with the reason for each instruction, and that the prompt set the whole scope of what the AI reads — the AI does what the steps say on every run, and works from the inputs it was given.
- The checklists are in `checklists/`, and the checklist for checklists is `checklist.md` — the files are called by the name the README calls them.

### Removed

- The Vale and textlint settings, and Claude Code starting writ on its own when it is about to write a document — writ runs when you or a plugin call it, and what a document must be is in its checklists.
- `/writ:pith` — turn now has every work read in its receiver's place and checked against its checklist, so a second way to check in writ is not needed.
- writ's own hooks and its form of decisions per item — turn holds the document to the checklists, and writ holds nothing between calls.

## [0.2.0] - 2026-10-13

### Changed

- The checklists writ checks a document by (`doc`, `readme`, `design`, `prompt`, `essentials`) are rewritten as yes-or-no items, each under a heading with its ID, and pith reads questions from such items — each question asks what the reader gets from the document, so two checks give the same answer.

## [0.1.0] - 2026-10-06

### Added

- `/writ:up` writes or fixes a document for its reader and returns it with Good and More for every question — you can hand the document on without rereading it, and judge it from the report alone.
- `/writ:pith` checks a prompt, code, tests or a document by having a first user who does not know the discussion use it, and writes essentials files from a purpose — you check your work by what happened in use, not by what you meant.
