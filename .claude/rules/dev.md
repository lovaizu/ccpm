---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
  - ".rn/**"
---

# Plugin development in ccpm

**Build each plugin by [the plugin guide](../../dev/plugin-development-guide.md), and run the work
by rn, which runs it as [rn's architecture](../../dev/rn/architecture.md) draws.**

- Rationale: rn exists to carry a request to deliverables that their people can use, so the work on
  ccpm's own plugins goes through rn, and a lack that the work meets is a lack of rn's.

**After each change to the tree, read its whole order again, and put each deliverable after each
one it takes from, waits for, or whose check it rests on.**

- Rationale: a deliverable added or changed in one place leaves another before what it rests on,
  and the work then starts it on a guess.

**A subagent makes the test cases, the skeleton, and the code, and the main conversation reads all
it made.** The main conversation first writes the policy into the design tree's decisions, and
briefs the subagent with the best practice of the deliverable's kind and the documents agreed. It
then reads each line the subagent made against the architecture and the best practice, and takes
only the vital few by the plugin's purpose. It writes each gap into the architecture and the design
tree before the tests and the code.

- Rationale: the main conversation keeps the whole only where it sets each policy and reads each
  result itself, as a subagent's report is a claim, not a result.

**Before any fix to a part, write the part's purpose and the simplest way that could meet it at
all, beside how the part meets it now, and make the part that way, removing each mechanism that
only works around another.** Have one subagent, given only the purpose and the code, name a simpler
way where one exists.

- Rationale: a fault fixed where it shows passes its tests and its conditions, so fixes pile up
  around the first design until a plain task, such as writing a change into the design tree, runs
  through a shell, a temporary folder, and a workaround of the host's refusal.

**Until the user says yes, install nothing, and send nothing to a translator, a web API, or any
service other than Claude Code and the repository's git and GitHub. Running `claude`, such as a
prompt's tests on Opus, needs no ask, and neither does fetching a public page to read it. Say so
in every brief to a subagent and in every `claude -p` you start.**

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address. Claude Code and GitHub already hold the work, as the user runs the work through them.
