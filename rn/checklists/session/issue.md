---
name: issue
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Issue

An issue, a file in the session's folder `.rn/<yyyymmdd>-<slug>/` that rn sends to rn's makers on
`lovaizu/ccpm` once the user says yes, is read by the makers, who build rn for all its users, to
decide how rn changes so that the need it shows is met in every user's later work.

An issue serves them by one learning of the session, the user approved for rn's makers, told as a
fault of rn's: what happened, in the words the learning quotes, why it matters to a user of rn, and
what rn should do instead, in the terms of rn's own steps and checklists. It holds the need and its
points alone, never the user's work: the user chose what leaves their project, and the issue is
public.

## Format

### F-1: Shape

Scope: whole

Does the issue follow this template?

```markdown
# rn: <what happens>

## What happened

<what happened in the session, quoting the words of the learning it rests on>

## Why it matters

<what it costs a user of rn, such as a change sent back or a question asked late>

## What it should be

<what rn should do instead, naming the step or the checklist of rn's it would change>

## Seen in

rn <the version the steering's front matter names>
```

The first line is the issue's title, and the rest its body, as rn sends them.

Why: the makers find the same thing under the same heading in every issue, and rn sends the title
and the body apart.

## Benefit

### B-1: What it should be, and why

Scope: its part

From the title and `## What it should be`, can rn's makers tell what rn should do, at which of its
steps or checklists, and from `## Why it matters` what a user of rn loses while it does not?

Look for:
- a title that names a slip of the session rather than what rn does;
- a change that names no step or checklist of rn's;
- a cost to the user not said, or said as a cost to the session alone.

Why: the makers decide from the need and its cost; a need tied to one session is read as that
session's, and one with no cost is weighed below every other.

### B-2: What happened, without the user's work

Scope: its part

Can the makers see what happened in the words the learning quotes, with nothing of the user's work
beyond them?

Look for:
- a fact the learning does not quote, or a quote not as the learning gives it;
- a path, a name, a line of code or words of the user's project beyond what the learning quotes;
- what the user decided about their own work, which holds nothing of rn's need.

Why: an issue resting on what the learning does not say is a guess the makers cannot check, and one
holding the user's work makes public what they never chose to send.

### B-3: One need

Scope: whole

Does the issue hold one need, that one change of rn's would meet?

Look for: two changes that could be made apart, or two learnings told as one.

Why: each need is decided and closed on its own; two in one issue are decided together or one is
left behind when the issue is closed.
