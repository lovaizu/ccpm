# Changelog

## [Unreleased]

### Added

- A checklist for code and its tests (`code`): tests held to what the README and the design ask and seen failing, each told in Given / When / Then, every branch run, static checks and one style by tool, and stops that say what went wrong and what to do — code and tests are made and judged by one measure, as documents and prompts are.

### Changed

- The README checklist asks for an opening of one or two sentences saying what the product is and what it gives whom, an example that shows only what the reader does and gets back, why to choose it in its own section after the example, a reason for a requirement only where the reader could not see it, and nothing beyond deciding and getting to the first result, which goes to pages reached from Documentation — a README reads as the ones people are used to, and no longer buries what it gives under how the product works.
- A checklist's version goes up once for each change that reaches those who judge by it, such as a release or a merge to a shared branch, not on every edit — a version names text people judged by, and drafts in between take no number.
- The design checklist asks that a design leave out how the product behaves in one case where a principle it gives settles it — a design holds principles and decisions, and does not grow a rule beside them for each case a trial meets.

### Removed

- `/writ:pith` — turn now has every work read in its receiver's place and checked against its checklist, so a second way to check in writ is not needed.

## [0.2.0] - 2026-10-13

### Changed

- The checklists writ checks a document by (`doc`, `readme`, `design`, `prompt`, `essentials`) are rewritten as yes-or-no items, each under a heading with its ID, and pith reads questions from such items — each question asks what the reader gets from the document, so two checks give the same answer.

## [0.1.0] - 2026-10-06

### Added

- `/writ:up` writes or fixes a document for its reader and returns it with Good and More for every question — you can hand the document on without rereading it, and judge it from the report alone.
- `/writ:pith` checks a prompt, code, tests or a document by having a first user who does not know the discussion use it, and writes essentials files from a purpose — you check your work by what happened in use, not by what you meant.
