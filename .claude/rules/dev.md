---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development in ccpm

Build each plugin by [the plugin guide](../../dev/plugin-development-guide.md), taking from it what
the plugin's requirements call for.

This file holds the order the work goes in. Each step names the best practice in
`plugins/rn/domain/best-practices/` to open while doing it. A best practice's goal says what the
deliverable's user achieves, and its critical success factors what must go right for that. Its
necessary conditions, each under the factor it serves, ask, each as a question, whether the
deliverable holds a state that the factor needs. Its template says where the deliverable holds each,
and each condition's practice holds a way to meet it. Finish a document with
`refactor-doc/best-practice.json` open as well, and code with `refactor-code/best-practice.json`.

**Keep each plugin whole in its own folder, `plugins/<plugin>/`, as
[the plugin guide](../../dev/plugin-development-guide.md#a-folder-that-holds-all-the-plugin-needs) asks of a plugin's folder.** `dev/scripts/standalone.py check`, which `dev/scripts/check.sh` runs, is that check.

When a step's work needs something that its best practice doesn't ask for, mend that best practice by
[the meta best practice](../../plugins/rn/domain/best-practices/meta/best-practice.md): find the
level whose gap the work met, and rebuild it from the level it serves. Do so whichever plugin you are building. Then make the work again against the mended
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

**Have three subagents make each document of steps 1 to 3 apart, each briefed by
[the generator's part of the plugin template](../../dev/plugin-template/domain/generator.md)
with only the document's best practice, its template, and its inputs, the design tree among them. Make the
document from the three, taking each vital item from the one that says it most clearly.**

- Rationale: one maker carries the whole discussion into the document, while three made apart
  show which items each finds vital from the best practice alone.
- Rationale: until rn's evaluators exist, no AI reads a document to judge it, as such a reading
  finds many small points in place of the vital few.

**In each brief by the generator's part, name as `{record}` a file in the system's temporary
folder, and have the subagent write each entry there itself, in the form of
[the record](../../dev/plugin-template/domain/record.schema.json), in place of running
`record.py`. Before you take its result, read the record against the part's steps and the best
practice's practices, as the plugin's check would. Then remove the file.**

- Rationale: no guard runs a check on a subagent here, so the main conversation reads the record
  in the check's place.

### 1. Write the product vision

**With `product-vision/best-practice.json` open, settle the product vision's decisions in the
work's one design tree, `.rn/<yyyymmdd>-<goal>/design-tree.json`, in the form of
[the design tree best practice's template](../../plugins/rn/domain/best-practices/design-tree/design-tree.schema.json). After each change, read the path from the node
changed up to the goal and every node the change touches, as
[the design tree best practice](../../plugins/rn/domain/best-practices/design-tree/best-practice.md) asks after a change to a node. Write `dev/<plugin>/product-vision.md` from the tree by
`product-vision/template.md`. Have the user agree to it before you make anything else.** Do the
same for each document after it: its questions and decisions go into the same tree, and you
write the document from them by its kind's template.

- Rationale: a change made by finding an ID or a word never shows the branch the node stands in,
  so the nodes over and under it go on saying what held before, and the tree drifts from its goal.
- Rationale: each sentence of a document then rests on a decision of the tree, and two documents
  that rest on one decision say the same thing. The template holds each document to what its
  reader needs, as an AI told only to be brief still writes past it.
- Rationale: the README takes two things from the product vision: what the user gains, and the
  objectives whose main use its walkthrough runs. The architecture says how the plugin gives
  what the README promises from it. If you make either before the product vision, it rests on a
  goal that the user hasn't agreed to.

### 2. Write the README

**With `readme/best-practice.json` open, write `plugins/<plugin>/README.md` from the product
vision, as step 1 says. Have the user agree to it before you make the architecture.**

- Rationale: you build everything after the README to what it promises the user. Built before it,
  that work would stand on a measure that no one has settled.

### 3. Write the architecture

**With `architecture/best-practice.json` open, write `dev/<plugin>/architecture.md` on
[the plugin guide](../../dev/plugin-development-guide.md). Have the user agree to it.** Place its
files as [the plugin template](../../dev/plugin-template) lays them out. Design the plugin so that each general lesson of a run reaches the plugin's repository, as
[the plugin guide](../../dev/plugin-development-guide.md#learning-from-each-run) asks of what a run learns.

**Make each figure as [the figure rules](figures.md) say.**

### 4. Build each deliverable

**For each deliverable of the design tree, in its order, have a subagent make each part of a to e.
Brief it by [the generator's part of the plugin template](../../dev/plugin-template/domain/generator.md),
filled for the part: what it makes, for whom, the best practice that the part names, the part's
inputs, and what holds at the end. Its steps have it read that best practice in full, and take
its practices in their order and at the time each names. Before you take its result, check the result
against the purpose and the best practice.**

- Rationale: the main conversation holds the whole discussion, so it takes a best practice that
  it read before as known, and skips its items. A subagent starts from its brief alone, so it
  works from the best practice itself.

a. **First write the deliverable's architecture tests, as the practices on tests of
   [the code best practice](../../plugins/rn/domain/best-practices/code/best-practice.md),
   [the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md), and
   [the plugin guide](../../dev/plugin-development-guide.md#test)
   say: one for each path through its sequences, with what joins the parts run real and a double for
   each role an AI runs. See each fail.**

b. **Make the code with `code/best-practice.json`, its unit tests by the test levels of
   [the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md), and its
   code as [the plugin guide](../../dev/plugin-development-guide.md#development) asks of a plugin's code.**

c. **Write each prompt, a skill or an agent, with
   [prompt/best-practice.json](../../plugins/rn/domain/best-practices/prompt/best-practice.md)
   open. Run no trial of it alone, as
   [the plugin guide](../../dev/plugin-development-guide.md#no-trial-of-a-prompt-alone)
   says.** Each rule of its steps that must hold on every run goes to a lane in d, as
   `prompt/best-practice.json` holds such a rule with a hook, and a tests it.

d. **Lay the lanes the prompts' steps call for, with `prompt/best-practice.json` open, by
   running the up skill of Lane.** Read the proposal that it shows, and approve it once it
   holds each rule that the steps call for. Where a step needs a check that no lane holds,
   add the check to Lane as a lane of its own, in a file of its own, with `code/best-practice.json`
   open. Each check then lives in one place in Lane, so you write and test it once.
   - Rationale: the architecture tests run the lanes and routes as laid, so lay them before those
     tests.

e. **Run the architecture tests of a, and fix each failure at the part or the handoff where it
   lies.**

**After a trial, change a prompt or a document only for a cause that the records confirm, as
`prompt/best-practice.json` says of a failed trial. Trace that cause to what the README and the architecture say the
prompt or document should be.**

- Rationale: what an AI does varies from run to run. A line added for one run's slip meets a
  different slip in the next run, so the additions never settle.

**Run every trial on Opus, and set the model in the command that starts the trial, such as
`claude --model opus`.**

- Rationale: the plugins' users run Opus.
  [The architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md)'s tests run each role on the model its users run.

**Run a trial that needs a real GitHub repository in `lovaizu/playground`.** This repository
exists for the product vision trials that
[the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md)'s tests
ask for.

### 5. Confirm the whole in real use

**Once you have built every deliverable and every unit and architecture test passes, try the plugin as its
user to confirm the product vision, as the product vision tests of
[the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md) say.**
Try it on each objective's main use, as the README's walkthrough shows it, at the size of a real
request. Use a stand-in that holds an intent the plugin never receives.

**When the trial finds a fault, first test it at the level that missed it, as
[the architecture best practice](../../plugins/rn/domain/best-practices/architecture/best-practice.md)
says of a fault that a higher level finds. Then confirm the whole again.**

### 6. Check the structure

**Pass Claude Code's check of the manifests, as [the plugin guide](../../dev/plugin-development-guide.md#the-manifests-checked) asks.**

### 7. Release

**Release with a version and a changelog entry that tell users what changed for them, as
[the plugin guide](../../dev/plugin-development-guide.md#the-version-and-the-changelog) asks, and only when the user says so. Before you ask the user to merge, make the [final check](final-check.md). Never merge the pull
request yourself, and never use `--admin`.**

- Rationale: the user decides what reaches users. `main` has branch protection, so only the user can
  clear its required review.
