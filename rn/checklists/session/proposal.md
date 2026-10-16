---
name: proposal
version: 0.1.0
---

# Proposal

A proposal is read by the user at a sign-off, to say yes or no from it alone, without reading the
work over, and to read the work only where they want to. Each item of `readability.md` applies to a
proposal with the work as it now stands as its subject.

## Format

### F-1: Shape

Does the proposal follow this template, markers included?

```markdown
── {slug}: {the goal in one line} ──
✅ {#id task name / ...}
👉 #{id} {sign-off name} ── read it on the PR: /rn:ty to approve, /rn:gm <feedback> to ask for changes
⬜ {#id task name / ...}

Draft PR: {url}

{what rn proposes to do next, and why it serves the goal}

Goal: {the goal as steering.md words it}
Judged by:
- {each acceptance criterion ID}: {the criterion as steering.md words it}

Toward what you would choose it for:
- {each attractive criterion ID}: {how far the work now gives it, in the user's terms} ({since the last proposal: what came closer, or the same})

Changed since the last approval: {each change written without stopping}
Taken away: {what the product or rn did before that this design no longer does}

Decided for you
- {each point rn settled on its own}: {its ground}
- {each shortfall left}: {why}

{each checklist's name}
- ✅ {item ID} {item name}: {lines}
- ⬜ {item ID} {item name}
```

- A line that has nothing is left out.
- The map on top heads every message where rn stops: ✅ done, 👉 now, ⬜ ahead.
- The decision line `● #{id} {sign-off name} ── proposed: ... → waiting for #{id} {sign-off name}`
  comes after the proposal, as the last line of the commit that stops.

Why: the user finds the same thing in the same place at every sign-off, and the checks find the
map, the IDs and the decision line by these markers.

## Benefit

### B-2: What comes next and why

Can the user tell what rn proposes to do next, and why that serves the goal?

Why: a report of where things stand leaves the user to work out what to do next, which is the work
they left to rn.

### B-1: How close the work has come

Can the user tell, for each thing they would choose the result for, how far the work now gives it
and what came closer since the last proposal?

Why: clearing every shortfall never ends, since each fix leaves a smaller one; how close the work
has come is what lets the user decide whether it is enough.

### B-6: What changed since their last approval

Can the user tell what changed without their deciding it since the last sign-off they approved,
and what the product or rn did before that it no longer does?

Why: the user approved an earlier state, and a change they did not decide, or a loss, is theirs to
accept at the sign-off, not to find in use.

### B-4: What was decided for them

Can the user see first each point rn settled on its own, with the ground it settled it from, and
each shortfall left, with why?

Why: the user approves the work resting on those decisions, so each is theirs to overturn; one
left out reaches their approval unseen.

### B-7: Assumptions stand as shortfalls

Can the user see each assumption the work rests on as a shortfall under the criterion it puts at
risk?

Why: the user approves the work resting on it at each sign-off, so it stays before them until
something checks it.

### B-5: Each item holds where it says

Can the user trust each item shown met, because the lines it names give it when opened?

Why: no one looks again at what is called met, so a flaw it hides reaches the user's approval
unseen.

### B-3: Decided from the proposal alone

Can the user say yes or no without looking anything up or asking back?

Look for: a ground the proposal names but does not give; a word of the work's inside the user has
not met; a place named without what is there.

Why: each thing the user must fetch to decide is time spent on what they left to rn.

## Usability

None: each thing that makes a proposal quick to decide from is one the user gets from it, so its
item is in Benefit.
