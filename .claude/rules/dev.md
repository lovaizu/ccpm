---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development (ccpm)

Build each plugin by [the plugin best practice](../../dev/plugin-best-practice.md), taking what
its requirements call for.

This file holds the order the work goes in. Each step names the best practice in
`plugins/turn/core/domain/best-practices/` to open while doing it. A best practice's goal says what
the deliverable's user achieves. Its template, or else its parts, says what the deliverable holds.
Its user benefits ask whether the user gets what they need from the deliverable. Its practices hold a way to make each question pass.
Open `refactor-doc.json` as well when the work is a document, and `refactor-code.json` when it is
code: that one finishes it.

When a step's work needs something that its best practice does not ask, mend that best practice as
Q8 of [meta.json](../../plugins/turn/core/domain/best-practices/meta.md) says. Do so whichever
plugin you are building. Then make the work again against the mended best practice.

- Rationale: every plugin here uses the same best practices, so a gap left in one comes back in
  every plugin that uses it.

Before you commit work made before a rule or a best practice changed, read it against the new one.

- Rationale: that work passed the rules as they were then. Committed unread, it brings back what
  the change set out to stop.

Until the user says yes, install nothing, and send nothing to a service outside the repository's
git and GitHub, such as a translator or a web API. Fetching a public page to read it needs no ask.
Say so in every brief to a subagent and in every `claude -p` you start.

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address.

Source: facts confirmed in the official docs (plugins reference / plugin marketplaces, prompting
best practices / skill authoring best practices) and the official plugins.

## Steps

### 1. Write the UX

**Settle the UX's decisions in `dev/<plugin>/design-tree.json`, the plugin's one design tree, with
`ux.json` open. Write `dev/<plugin>/ux.md` from the tree by `ux-template.md`. Have the user agree to
it before you make anything else.** Do the same for each document after it: its questions and
decisions go into the same tree, and the document is written from them by its kind's template.

- Rationale: each sentence of a document then rests on a decision of the tree, and two documents
  that rest on one decision say the same thing. The template holds each document to what its
  reader needs, as an AI told only to be brief still writes past it.
- Rationale: the README takes two things from the UX: what the user gains, and the scenario that
  its walkthrough runs. The architecture says how the plugin gives the UX. If you make them before
  the UX, they rest on a goal that the user has not agreed to.

### 2. Write the README

**Write `plugins/<plugin>/README.md` from the UX with `readme.json` open, as step 1 says. Have the
user agree to it before you make the architecture.**

- Rationale: everything after the README is built to what it promises the user. Built before it,
  that work would stand on a measure that no one has settled.

### 3. Write the architecture

**Write `dev/<plugin>/architecture.md` on [the plugin best practice](../../dev/plugin-best-practice.md),
with `architecture.json` open. Have the user agree to it.** Place its files as
[Directory structure](../../dev/plugin-best-practice.md#directory-structure) says. Design the
plugin to take in what is general, as
[Learning from each run](../../dev/plugin-best-practice.md#learning-from-each-run) says.

**Put the style of `dev/images/figures.css` into each figure with `python3 dev/scripts/figures.py
write`.** `dev/scripts/check.sh` fails on a figure whose copy of the style differs from that file.

### 4. Have the README and the architecture read once

**Have a new reader who does not know the discussion read the README and the architecture once, as
their readers would. Settle each finding by fixing the decision or principle it comes from.**

- Rationale: a reading after every fix turns each finding into a patch. The documents then drift
  from their aim while every reading passes.

### 5. List the slices

**List the slices to build. A slice is the smallest part of the plugin through which the user meets
one or more of the key results in the UX, from start to end. The first slice moves one key result
by the thinnest path.**

- Rationale: a slice built from start to end shows early that its parts join as the architecture
  says. The first slice lays, soonest, the parts that every later slice stands on. The word "unit"
  names a test level, so a slice has another name.

### 6. Build each slice

**For each slice, in order, do a to e. Write each part's unit tests first, and see them fail. Only
then write its code, as Q6 of [code.json](../../plugins/turn/core/domain/best-practices/code.md)
says.**

a. **Write the unit tests of its code with `code.json` open, as
   [Unit: code](../../dev/plugin-best-practice.md#unit-code) says: one for each class, each edge
   and each rule of the part's contract. Run them and see them fail.**

b. **Write the code with `code.json` open until the tests pass**, as
   [Development](../../dev/plugin-best-practice.md#development) says.

c. **Write each prompt, a skill or an agent, with
   [prompt.json](../../plugins/turn/core/domain/best-practices/prompt.md) open. Run no trial of it
   alone, as
   [No trial of a prompt alone](../../dev/plugin-best-practice.md#no-trial-of-a-prompt-alone)
   says.** Each rule of its steps that must hold on every run goes to a lane in d, as Q14 of
   `prompt.json` says, and e tests it.

d. **Lay the lanes the prompts' steps call for with `plugins/lane/scripts/lay.py`, with
   `prompt.json` open.** Write them in a proposal in the form
   [the lanes](../../plugins/lane/docs/lanes.md#the-proposal) gives. Read what `lay.py print`
   prints of it, and lay it with `lay.py write`. Add a check that no lane holds to Lane with
   `code.json` open, as a lane of its own in a file of its own. Each check is then written and
   tested once.
   - Rationale: the architecture tests run the lanes and routes as laid, so lay them before those
     tests.

e. **Write the slice's architecture tests, as
   [Architecture: the parts joined](../../dev/plugin-best-practice.md#architecture-the-parts-joined)
   says: one for each path through its sequences, with what joins the parts run real and a double
   for each role an AI runs. Run them, and fix each failure at the part or the handoff where it
   lies.**

**After a trial, change a prompt or a document only for a cause that the records confirm, as Q15 of
`prompt.json` says. Trace that cause to what the README and the architecture say the prompt or
document should be.**

- Rationale: what an AI does varies from run to run. A line added for one run's slip meets a
  different slip in the next run, so the additions never settle.

**Run every trial on Opus, and name the model in the run.**

- Rationale: Opus is the model the plugins' users run.
  [ux: the plugin in real use](../../dev/plugin-best-practice.md#ux-the-plugin-in-real-use) runs
  each role on the model its users run.

**Run a trial that needs a real GitHub repository in `lovaizu/playground`.** This repository is
kept for the trials that
[ux: the plugin in real use](../../dev/plugin-best-practice.md#ux-the-plugin-in-real-use) asks for.

### 7. Confirm the whole in real use

**Once every slice is built and every unit and architecture test passes, try the plugin as its
user to confirm the UX, as
[ux: the plugin in real use](../../dev/plugin-best-practice.md#ux-the-plugin-in-real-use) says.**
Try it on each objective's scenario, at the size of a real request. Use a stand-in that holds an
intent the plugin never sees.

**When the trial finds a fault, first test it at the level that missed it, as
[A fault is tested at the level that must catch it](../../dev/plugin-best-practice.md#a-fault-is-tested-at-the-level-that-must-catch-it)
says. Then confirm the whole again.**

### 8. Check the structure

**Pass the checks of [The manifests checked](../../dev/plugin-best-practice.md#the-manifests-checked).**

### 9. Release

**Release as [Release](../../dev/plugin-best-practice.md#release) says, and only when the user says
so. Before you ask the user to merge, make the [final check](final-check.md). Never merge the pull
request yourself, and never use `--admin`.**

- Rationale: the user decides what reaches users. `main` is protected, so only the user can clear
  its required review.
