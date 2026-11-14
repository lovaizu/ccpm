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

**Until rn runs, the main conversation runs rn's architecture by hand.** It's the orchestrator, and
keeps the design tree `.rn/20261107-rn/design-tree.json` as the tree-keeper would. It starts each
other role as a subagent, briefed by that role's part of
[the plugin template](../../dev/plugin-template/domain/), with the role's cut of the tree. Where
rn's guard would check a role's record, the subagent writes its record to a file in the system's
temporary folder, in the form of
[the record](../../dev/plugin-template/domain/record.schema.json), and the main conversation reads
it against the part's steps and the best practice's practices before it takes the result, then
removes the file.

- Rationale: no guard holds a subagent here yet, so the main conversation does what the guard and
  rn's check would.

**Until the user says yes, install nothing, and send nothing to a translator, a web API, or any
other service outside the repository's git and GitHub. Fetching a public page to read it needs no
ask. Say so in every brief to a subagent and in every `claude -p` you start.**

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address.
