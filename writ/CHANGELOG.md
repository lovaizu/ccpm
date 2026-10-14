# Changelog

## [Unreleased]

### Added

- A plugin's step can call `writ:up`, from a subagent too, and gets back the document with its report, or the points only it can decide, each with writ's recommended answer — anything a plugin makes goes through writ, with no one there to answer.
- A checklist writ makes for a kind it has none for, or an addition to one of writ's, is kept at `.writ/checklists/<kind>.md` and used from then on — a kind you write again is held to what it needs, and your team shares it by committing it.

- A checklist for code and its tests (`code`): tests held to what the README and the design ask and seen failing, each told in Given / When / Then, each failure naming the one behavior that broke, the flow tested apart from each part's work with the least input and setup, every branch run, static checks and one style by tool, and stops that say what went wrong and what to do — code and tests are made and judged by one measure, as documents and prompts are.

### Changed

- Every checklist asks one thing per item, each item asks what the reader or user gets rather than what is in the work, and each sits in the section its kind of question belongs to — a no names the one thing that falls short, and anyone judging gets the same answer.
- `/writ:up` settles every item of the checklists before anything is written: it looks up what the repository shows, puts what it can infer to you to confirm, and asks you only the rest, one question at a time; turn then writes the document, has it read as its reader and checks it, and you get the report of each item with the lines that meet it — you answer once, before the writing, and can leave writ at work after.
- writ needs turn, which installing writ installs, and Python 3.9 and jq, which turn needs — the writing, reading and checking are turn's, done one way for every plugin.
- The README checklist asks for an opening of one or two sentences saying what the product is and what it gives whom, an example that shows only what the reader does and gets back, why to choose it in its own section after the example, a reason for a requirement only where the reader could not see it, and nothing beyond deciding and getting to the first result, which goes to pages reached from Documentation — a README reads as the ones people are used to, and no longer buries what it gives under how the product works.
- A checklist's version goes up once for each change that reaches those who judge by it, such as a release or a merge to a shared branch, not on every edit — a version names text people judged by, and drafts in between take no number.
- The design checklist asks that a design leave out how the product behaves in one case where a principle it gives settles it — a design holds principles and decisions, and does not grow a rule beside them for each case a trial meets.
- The design checklist asks that each check show one quality, the flow of the parts be checked apart from what each part makes, and each check be tried in the smallest situation that shows it — a failing check says which quality broke, and no check pays for real work it does not need.

- The checklists are in `checklists/`, and the checklist for checklists is `checklist.md` — the files are called by the name the README calls them.

### Removed

- The Vale and textlint settings, and Claude Code starting writ on its own when it is about to write a document — writ runs when you or a plugin call it, and what a document must be is in its checklists.

- `/writ:pith` — turn now has every work read in its receiver's place and checked against its checklist, so a second way to check in writ is not needed.

## [0.2.0] - 2026-10-13

### Changed

- The checklists writ checks a document by (`doc`, `readme`, `design`, `prompt`, `essentials`) are rewritten as yes-or-no items, each under a heading with its ID, and pith reads questions from such items — each question asks what the reader gets from the document, so two checks give the same answer.

## [0.1.0] - 2026-10-06

### Added

- `/writ:up` writes or fixes a document for its reader and returns it with Good and More for every question — you can hand the document on without rereading it, and judge it from the report alone.
- `/writ:pith` checks a prompt, code, tests or a document by having a first user who does not know the discussion use it, and writes essentials files from a purpose — you check your work by what happened in use, not by what you meant.
