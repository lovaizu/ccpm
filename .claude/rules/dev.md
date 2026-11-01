---
paths:
  - "plugins/**"
  - "dev/**"
  - ".claude-plugin/**"
---

# Plugin development (ccpm)

Read [how a plugin works](../../dev/architecture.md), the architecture every plugin is built on, and
follow it.

This file holds the order the work goes in. Each step names the template in
`plugins/turn/templates/` to open while doing it. A template says what the work of its kind must be,
and its checklist asks the questions that the work must pass. A template names in `includes` the
templates whose questions it also takes, such as `refactor-doc.json`; open those with it.

When a step's work needs something that its template does not ask, add the question to that
template, whichever plugin is being built, and make the work again against it.

- Rationale: what is made with the template open is made right as it is made; a gap left in a
  template is met again by every plugin made with it.

Work made before a rule or a template changed is read against the new one before it is committed.

- Rationale: work made earlier was checked against what the rules said then; committed unread, it
  brings back what the change was made to stop.

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

### 5. List the units

**List the units to build. A unit is the smallest slice through which the user meets one or more of
the key results in the UX, from start to end. The first unit moves one key result by the
thinnest path.**

- Rationale: a unit run end to end shows early whether the plugin keeps its promise, and the first
  shows soonest whether the user would choose it at all.

### 6. Build each unit

**For each unit, in order, do a to e.**

a. **Write its tests with `code.json` open, as
   [Unit tests: code](../../dev/architecture.md#unit-tests-code) says, run them and see them
   fail.**
   - Rationale: a test written after the code is fitted to what the code does, not to what it must
     do.

b. **Write the code with `code.json` open until the tests pass**, as
   [Code](../../dev/architecture.md#code) says.

c. **Write each prompt, a skill or an agent, with `prompt.json` open, and try it as
   [Unit tests: prompts](../../dev/architecture.md#unit-tests-prompts) says.**
   - Rationale: a trial on unchecked prompts finds the prompts' slips, not whether the plugin keeps
     its promises.

d. **Lay the lanes the prompts' steps call for with `plugins/lane/scripts/lay.py`, with
   `prompt.json` open:** write them in a proposal as
   [the lanes](../../plugins/lane/docs/lanes.md#the-proposal) gives it, read what `lay.py print`
   prints of it, and lay it with `lay.py write`. A check no lane holds is added
   to lane with `code.json` open, as
   [Checks kept in lane](../../dev/architecture.md#checks-kept-in-lane) says.

e. **Try the unit as its user, as
   [Acceptance tests: user stories](../../dev/architecture.md#acceptance-tests-user-stories) says.**

**Change a prompt or a document after a trial only for a cause confirmed in the records and traced
to what the README and the architecture say it should be.**

- Rationale: what an AI does varies from run to run; a line added for one run's slip meets a
  different slip in the next, and the additions never settle.

### 7. Check the whole

**Try the plugin as its user from start to end, as
[Acceptance tests: user stories](../../dev/architecture.md#acceptance-tests-user-stories) says.**
Settle what it finds at the unit its cause lies in, then check the whole again.

- Rationale: each unit was checked on its own; what lies between units, and key results that show
  only over the whole, such as the time a whole run takes, show only here.

### 8. Check the structure

**Pass the checks of [The manifests checked](../../dev/architecture.md#the-manifests-checked).**

### 9. Release

**Release as [Release](../../dev/architecture.md#release) says.**
