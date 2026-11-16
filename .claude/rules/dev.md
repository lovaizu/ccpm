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

**The main conversation makes the test cases, the skeleton, and the code too, and has subagents
review the code and the test code.** One subagent reviews each part, and one each combination of
parts that the architecture defines. Each reads the plugin's product vision, README, and
architecture whole first, then names each place where the code or the test code misses a case, says
other than the three documents, or holds what none of them traces to. The main conversation takes
only the vital few by the plugin's purpose. It writes each into the architecture and the design
tree before the tests and the code.

- Rationale: a rebuild over existing code needs one maker who holds the whole, as makers apart
  copied what they saw and missed how the parts meet. A review of one unit finds the gaps that a
  reader of the whole misses, and most of what it names is trivia that the purpose leaves out.

**Until the user says yes, install nothing, and send nothing to a translator, a web API, or any
service other than Claude Code and the repository's git and GitHub. Running `claude`, such as a
prompt's tests and the E2E tests on Opus, needs no ask, and neither does fetching a public page to
read it. Say so in every brief to a subagent and in every `claude -p` you start.**

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address. Claude Code and GitHub already hold the work, as the user runs the work through them.
