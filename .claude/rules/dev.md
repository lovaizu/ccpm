---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development (ccpm)

Read [how a plugin works](../../dev/architecture.md), the architecture every plugin is built on, and
follow it.

This file holds the order the work goes in. Each step names the best practice in
`plugins/turn/core/domain/best-practices/` to open while doing it. Its goal says what the deliverable's user
achieves, and its parts say what the deliverable holds. Its benefits ask the questions that the
deliverable must pass, and its practices hold a way to make each question pass. A document is also
finished by `refactor-doc.json`, and code by `refactor-code.json`; open that one with it.

When a step's work needs something that its best practice does not ask, mend that best practice as
Q8 of [meta.json](../../plugins/turn/core/domain/best-practices/meta.md) says, whichever plugin is
being built, and make the work again against it.

- Rationale: every plugin here is made with the same best practices, so a gap left in one is met
  again by every plugin made with it.

Work made before a rule or a best practice changed is read against the new one before it is
committed.

- Rationale: work made earlier was checked against what the rules said then; committed unread, it
  brings back what the change was made to stop.

Install nothing, and send nothing to a service outside the repository's git and GitHub, such as a
translator or a web API, until the user says yes; fetching a public page to read it needs no ask.
Every brief to a subagent, and every `claude -p` started, says so.

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address.

Source: facts confirmed in the official docs (plugins reference / plugin marketplaces, prompting
best practices / skill authoring best practices) and the official plugins.

## Steps

### 1. Write the UX

**Write `dev/<plugin>/ux.md` with `ux.json` open, and have the user agree to it before anything else
is made.**

- Rationale: the README takes two things from the UX: what the user gains, and the scenario that
  its walkthrough runs. The architecture says how the plugin gives the UX. If they are made before
  the UX, they are built on a goal that the user has not agreed to.

### 2. Write the README

**Write `plugins/<plugin>/README.md` from the UX with `readme.json` open, and have the user agree to
it before the architecture is made.**

- Rationale: everything after is built to what the README promises the user; built first, it would
  stand on a measure no one has settled.

### 3. Write the architecture

**Write `dev/<plugin>/architecture.md` on [how a plugin works](../../dev/architecture.md), with
`architecture.json` open, and have the user agree to it.** Place its files as
[Repository structure](../../dev/architecture.md#repository-structure) says, and design the plugin
to take in what is general, as [Learning from each run](../../dev/architecture.md#learning-from-each-run)
says.

### 4. Have the README and the architecture read once

**Have a first user who does not know the discussion read the README and the architecture once, as
their readers would, and settle each finding by fixing the decision or principle it comes from.**

- Rationale: a reading after every fix turns each finding into a patch, and the documents drift
  from their aim while every reading passes.

### 5. List the slices

**List the slices to build. A slice is the smallest part of the plugin through which the user meets
one or more of the key results in the UX, from start to end. The first slice moves one key result
by the thinnest path.**

- Rationale: a slice built through shows early that its parts join as the architecture says, and
  the first lays soonest the parts that every later slice stands on. The word "unit" is kept for
  the test level, so a slice has another name.

### 6. Build each slice

**For each slice, in order, do a to e. Each part gets its unit tests first, seen to fail, and only
then its code or its prompt, as Q6 of
[code.json](../../plugins/turn/core/domain/best-practices/code.md) and Q16 of
[prompt.json](../../plugins/turn/core/domain/best-practices/prompt.md) say.**

a. **Write the unit tests of its code with `code.json` open, one for each class, each edge and
   each rule of the part's contract, as [Unit: code](../../dev/architecture.md#unit-code) says, run
   them and see them fail.**

b. **Write the code with `code.json` open until the tests pass**, as
   [Code](../../dev/architecture.md#code) says.

c. **For each prompt, a skill or an agent, write its trials with `prompt.json` open, as its Q14 to
   Q16 say and as [Unit: prompts](../../dev/architecture.md#unit-prompts) says, one case at a time:
   build each part of the trial and check it on a kept record, run the case and see it fail; then
   write the prompt with `prompt.json` open until the case passes.**

d. **Lay the lanes the prompts' steps call for with `plugins/lane/scripts/lay.py`, with
   `prompt.json` open:** write them in a proposal as
   [the lanes](../../plugins/lane/docs/lanes.md#the-proposal) gives it, read what `lay.py print`
   prints of it, and lay it with `lay.py write`. A check no lane holds is added
   to lane with `code.json` open, as
   [Checks kept in lane](../../dev/architecture.md#checks-kept-in-lane) says.
   - Rationale: the architecture tests run the lanes and routes as they are laid, so they are laid
     before those tests.

e. **Write the slice's architecture tests, one for each path through its sequences, with what
   joins the parts run real and each role an AI runs a double, as
   [Architecture: the parts joined](../../dev/architecture.md#architecture-the-parts-joined) says,
   run them, and fix what fails at the part or the handoff it lies in.**

**Change a prompt or a document after a trial only for a cause confirmed in the records, as Q15 of
`prompt.json` says, and traced to what the README and the architecture say it should be.**

- Rationale: what an AI does varies from run to run; a line added for one run's slip meets a
  different slip in the next, and the additions never settle.

### 7. Confirm the whole in real use

**Once every slice is built and every unit and architecture test passes, try the plugin as its
user on each objective's scenario, at the size of a real request, with a stand-in that holds an
intent the plugin never sees, as
[ux: the plugin in real use](../../dev/architecture.md#ux-the-plugin-in-real-use) says, to confirm
the UX.**

**Test a fault the trial finds first at the level that missed it, as
[A fault is tested at the level that must catch it](../../dev/architecture.md#a-fault-is-tested-at-the-level-that-must-catch-it)
says, and then confirm the whole again.**

### 8. Check the structure

**Pass the checks of [The manifests checked](../../dev/architecture.md#the-manifests-checked).**

### 9. Release

**Release as [Release](../../dev/architecture.md#release) says.**
