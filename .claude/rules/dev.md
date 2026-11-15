---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
  - ".rn/**"
---

# Plugin development in ccpm

**Build each plugin by [the plugin guide](../../dev/plugin-development-guide.md), and run the work
as rn runs it, by [rn's architecture](../../dev/rn/architecture.md).**

- Rationale: rn exists to carry a request to deliverables that their people can use, so the work on
  ccpm's own plugins goes the way rn's architecture draws, and a lack that the work meets is a lack
  of rn's.

**Until rn runs, the main conversation keeps the design tree `.rn/20261107-rn/design-tree.json`,
and takes its deliverables from the top.** Each session resumes from the tree.

- Rationale: the tree holds each decision and where the work stands, so a new session needs nothing
  else.

**After each change to the tree, read its whole order again, and put each deliverable after each
one it takes from, waits for, or whose check it rests on.**

- Rationale: a deliverable added or changed in one place leaves another before what it rests on,
  and the work then starts it on a guess.

**Until rn runs, the main conversation makes each document itself, with no evaluators: the best
practices and their templates, the plugin guide, and each plugin's product vision, README, and
architecture.** It makes each to its best practice and its template, and keeps only the vital few.

- Rationale: rounds of evaluators work only once rn runs them. Run by hand, each round added what
  the evaluators named, until the documents held trivia that no decision of the tree asked for.

**From the test cases on, a subagent makes each deliverable, and the main conversation checks it**
against its best practice and the tree before it takes the result. The main conversation briefs the
subagent by its role's part of [the plugin template](../../dev/plugin-template/domain/), with the
role's cut of the tree, and the subagent writes its record to a file in the system's temporary folder, in the form of
[the record](../../dev/plugin-template/domain/record.schema.json). The main conversation reads the
record against the part's steps and the best practice's practices, then removes the file.

- Rationale: no guard holds a subagent here yet, so the main conversation does what the guard and
  rn's check would.

**Until the user says yes, install nothing, and send nothing to a translator, a web API, or any
other service outside the repository's git and GitHub. Fetching a public page to read it needs no
ask. Say so in every brief to a subagent and in every `claude -p` you start.**

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address.
