---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development in ccpm

Build each plugin by
[the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md), taking
from it what the plugin's requirements call for.

This file holds the order the work goes in. Each step names the best practice in
`plugins/rn/domain/best-practices/` to open while doing it. A best practice's goal says what the
deliverable's user achieves, and its critical success factors what must go right for that. Its
necessary conditions ask, each as a question, whether the deliverable holds a state that a factor
needs. Its template, or else its parts, says where the deliverable holds each, and its practices
hold a way to meet each one. Finish a document with
`refactor-doc/best-practice.json` open as well, and code with `refactor-code/best-practice.json`.

When a step's work needs something that its best practice doesn't ask for, mend that best practice as
N3 of [meta/best-practice.json](../../plugins/rn/domain/best-practices/meta/best-practice.md)
says. Do so whichever plugin you are building. Then make the work again against the mended
best practice.

- Rationale: every plugin here uses the same best practices, so a gap left in one comes back in
  every plugin that uses it.

Before you commit work made before a rule or a best practice changed, read it against the new one.

- Rationale: that work passed the rules as they were then. Committed unread, it brings back what
  the change set out to stop.

Until the user says yes, install nothing, and send nothing to a translator, a web API, or any other
service outside the repository's git and GitHub. Fetching a public page to read it needs no ask.
Say so in every brief to a subagent and in every `claude -p` you start.

- Rationale: text sent out may hold what the user never meant to share, such as their email
  address.

Source: facts confirmed in the official plugins and in the official docs: plugins reference, plugin
marketplaces, prompting best practices, and skill authoring best practices.

## Steps

### 1. Write the product vision

**With `product-vision/best-practice.json` open, settle the product vision's decisions in the
work's one design tree, `.rn/<yyyymmdd>-<goal>/design-tree.json`, in the form of
[the design tree best practice's template](../../plugins/rn/domain/best-practices/design-tree/design-tree.schema.json). After each change, read the path from the node
changed up to the goal and every node the change touches, as N9 of
[the design tree best practice](../../plugins/rn/domain/best-practices/design-tree/best-practice.md#n9) says. Write `dev/<plugin>/product-vision.md` from the tree by
`product-vision/template.md`. Have the user agree to it before you make anything else.** Do the
same for each document after it: its questions and decisions go into the same tree, and you
write the document from them by its kind's template.

- Rationale: a change made by finding an ID or a word never shows the branch the node stands in,
  so the nodes over and under it go on saying what held before, and the tree drifts from its goal.
- Rationale: each sentence of a document then rests on a decision of the tree, and two documents
  that rest on one decision say the same thing. The template holds each document to what its
  reader needs, as an AI told only to be brief still writes past it.
- Rationale: the README takes two things from the product vision: what the user gains, and the
  objectives whose main use its walkthrough runs. The architecture says how the plugin gives the
  product vision. If you make either before the product vision, it rests on a goal that the user
  hasn't agreed to.

### 2. Write the README

**With `readme/best-practice.json` open, write `plugins/<plugin>/README.md` from the product
vision, as step 1 says. Have the user agree to it before you make the architecture.**

- Rationale: you build everything after the README to what it promises the user. Built before it,
  that work would stand on a measure that no one has settled.

### 3. Write the architecture

**With `architecture/best-practice.json` open, write `dev/<plugin>/architecture.md` on
[the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md). Have
the user agree to it.** Place its files as
[the plugin best practice's template](../../plugins/rn/domain/best-practices/plugin/template) lays
them out. Design the plugin to take in what's general, as
[N17 of the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md#n17) says.

**Put the style of `dev/images/figures.css` into each figure with `python3 dev/scripts/figures.py
write`.** `dev/scripts/check.sh` fails on a figure whose copy of the style differs from that file.

### 4. Have the README and the architecture read once

**Have a new reader who doesn't know the discussion read the README and the architecture once, as
their readers would. Settle each finding by fixing the decision or principle it comes from.**

- Rationale: a reading after every fix turns each finding into a patch. The documents then drift
  from their aim while every reading passes.

### 5. List the slices

**List the slices to build. A slice is the smallest part of the plugin through which the user meets
one or more of the key results in the product vision, from start to end. The first slice moves
one key result by the thinnest path.**

- Rationale: a slice built from start to end shows early that its parts join as the architecture
  says. The first slice lays, soonest, the parts that every later slice stands on. The word "unit"
  names a test level, so a slice has another name.

### 6. Build each slice

**For each slice, in order, do a to e. Write each part's unit tests first, and see them fail. Only
then write its code, as N5 of
[code/best-practice.json](../../plugins/rn/domain/best-practices/code/best-practice.md)
says.**

a. **Write the unit tests of its code with `code/best-practice.json` open, as
   [N13 of the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md#n13) says: one for each class, each edge
   and each rule of the part's contract. Run them and see them fail.**

b. **Write the code with `code/best-practice.json` open until the tests pass**, as
   [N19 and N20 of the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md#n19) say.

c. **Write each prompt, a skill or an agent, with
   [prompt/best-practice.json](../../plugins/rn/domain/best-practices/prompt/best-practice.md)
   open. Run no trial of it alone, as
   [N25 of the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md#n25)
   says.** Each rule of its steps that must hold on every run goes to a lane in d, as N12 of
   `prompt/best-practice.json` says, and e tests it.

d. **Lay the lanes the prompts' steps call for with `plugins/lane/scripts/lay.py`, with
   `prompt/best-practice.json` open.** Write them in a proposal in the form
   [the lanes](../../plugins/lane/docs/lanes.md#the-proposal) gives. Read what `lay.py print`
   prints of it, and lay it with `lay.py write`. Where a step needs a check that no lane holds,
   add the check to Lane as a lane of its own, in a file of its own, with `code/best-practice.json`
   open. Each check then lives in one place in Lane, so you write and test it once.
   - Rationale: the architecture tests run the lanes and routes as laid, so lay them before those
     tests.

e. **Write the slice's architecture tests, as
   [N13 of the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md#n13) and
   [N25 of the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md#n25)
   say: one for each path through its sequences, with what joins the parts run real and a double for
   each role an AI runs. Run them, and fix each failure at the part or the handoff where it
   lies.**

**After a trial, change a prompt or a document only for a cause that the records confirm, as N17 of
`prompt/best-practice.json` says. Trace that cause to what the README and the architecture say the
prompt or document should be.**

- Rationale: what an AI does varies from run to run. A line added for one run's slip meets a
  different slip in the next run, so the additions never settle.

**Run every trial on Opus, and name the model in the run.**

- Rationale: the plugins' users run Opus.
  [N13 of the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md#n13) runs each role on the model its users run.

**Run a trial that needs a real GitHub repository in `lovaizu/playground`.** This repository
exists for the product vision trials that
[N13 of the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md#n13)
asks for.

### 7. Confirm the whole in real use

**Once you have built every slice and every unit and architecture test passes, try the plugin as its
user to confirm the product vision, as
[N13 of the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md#n13) says.**
Try it on each objective's main use, as the README's walkthrough shows it, at the size of a real
request. Use a stand-in that holds an intent the plugin never receives.

**When the trial finds a fault, first test it at the level that missed it, as
[N14 of the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md#n14)
says. Then confirm the whole again.**

### 8. Check the structure

**Pass the checks of [N22 of the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md#n22).**

### 9. Release

**Release as [N23 of the plugin best practice](../../plugins/rn/domain/best-practices/plugin/best-practice.md#n23) says, and only when the user says
so. Before you ask the user to merge, make the [final check](final-check.md). Never merge the pull
request yourself, and never use `--admin`.**

- Rationale: the user decides what reaches users. `main` has branch protection, so only the user can
  clear its required review.
