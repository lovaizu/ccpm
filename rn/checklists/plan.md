---
name: plan
version: 0.1.0
---

# Plan

A plan, `steering.md`, is read by the user at the Plan sign-off, to approve what they will get and
why, and by the conductor in any later conversation, to carry the work to what the user really
wants without asking again. Each item of `doc.md` applies to a plan with the goal and how it is
reached as its subject; its B-16 is answered by the tasks in order, since a plan tells of no one
acting in turn. Before the tasks that make the deliverable are planned, the items on tasks are
answered as met.

## Benefit

### B-1: Why the user wants the goal

Can the reader tell, from the plan alone, the reason the user wants the goal?

Why: every later decision is judged by that reason, in any conversation; without it the work aims
at the user's first words, which can be met while what they meant is missed.

### B-2: The criteria carry the reason

Can the reader tell that a result meeting every attractive criterion gives the user what they want
the goal for, with nothing of that reason left out?

Why: the Deliverable sign-off judges by the criteria, so what the reason holds and the criteria do
not is never built.

### B-3: Each attractive criterion is a gain the user named

Can the reader tell, for each attractive criterion, what the user or their users gain, in the
user's own words?

Look for: a criterion that says only what must not happen, which any way that avoids it meets; a
gain the conductor wrote for the user.

Why: ways are built from the gain, so a gain the user did not name is a guess they find later.

### B-4: Each fact holds at its source

Can the reader rely on each fact the plan rests on, because it says how it was checked, or that
the user decided it?

Why: a plan standing on an unchecked fact gives way in the middle of the work, after effort was
spent on it.

### B-5: What only the user knows is theirs or an assumption

Can the reader tell, for each thing the plan relies on that neither the repository nor any
documentation can show, such as what the user's records hold, whether the user told it or it is an
assumption no one has checked?

Why: a guess that holds in the repository but not where the product runs reaches the user as a
result that does not work there; an assumption stays a shortfall in every proposal until something
checks it.

### B-6: Every form an input takes

Can the reader tell, for each kind of input the criteria speak of, such as "a user with no name",
every form it takes where the product runs, and what the product does today on each?

Why: a criterion worded from the one form tried passes while the others still fail, and the user
meets them all.

### B-7: Each decision is the user's

Can the reader tell, for each point the work rests on that only the user can decide, that the user
decided it?

Why: a decision the conductor made for the user sends the work the way it guessed.

### B-8: Each criterion gets built

Once the tasks are planned, can the reader find for each acceptance criterion a task that brings
it to hold?

Why: a criterion no task serves is never built, and the deliverable misses the goal the user
approved.

### B-9: A task's completion criteria carry its purpose

Once the tasks are planned, can the reader tell from each task's completion criteria that meeting
them moves the work toward the attractive criteria the task serves, not only toward their words?

Why: a task judged by words alone moves on without having moved toward why the user would choose
the result.

### B-10: Attractive quality first

Once the tasks are planned, can the reader see that the work on must-be quality comes after the
attractive criteria are nearly met?

Why: must-be quality is easier to build and check, and started first it takes the effort while the
reason to choose the work goes unchecked, past the time to change course.

## Usability

None: each thing that makes a plan easy to carry on from is one its readers get from it, so its
item is in Benefit.

## Format

### F-1: Shape

Does the plan follow this template, front matter, headings and markers included?

```markdown
---
rn: <installed rn version>
pr: <the session's pull request URL>
status: running
artifact-language: <the language everything written to the repository is in>
conversation-language: <the language the user is spoken to in>
readme: <path of the README; README.md unless agreed otherwise>
design: <path of the design document; docs/design.md unless agreed otherwise>
verification: <path of the verification document; docs/verification.md unless agreed otherwise>
---

# Goal

<what the user wants and why, as agreed with them>

# Acceptance criteria

## Attractive quality

- A1: <what the user or their users gain, which would make them choose the result>

## Must-be quality

- M1: <what the user takes for granted>

# Assumptions

- Fact, <how it was checked, or "decided by the user">: <what the plan rests on>
- Assumption: <what the plan rests on without having checked it>

# Rules

- <what the work must follow that the goal does not tell, such as this repository's conventions>

# Tasks

### [ ] #1: Plan sign-off
### [ ] #2: Design sign-off
### [ ] #3: <task name>

Purpose: <what this task does for the goal>

Serves: <criterion IDs>

Completion criteria:

- Attractive quality: <a state checked on the real thing>
- Must-be quality: <a state checked on the real thing>

### [ ] #4: Deliverable sign-off

# Not yet specified

- <what cannot yet be stated as a task>
```

- Criterion IDs are `A1`, `A2`... and `M1`, `M2`..., never reused once given.
- Until the Design sign-off is approved, the only tasks are the Plan and Design sign-offs, and what
  the deliverable needs is under Not yet specified; the tasks planned then take the next ids, and
  the Deliverable sign-off comes last. A task added later takes the next unused id and goes before
  the sign-off it leads to.
- `status` becomes `finished` when the Deliverable sign-off is approved.

Why: the commands and checks of rn read the plan by this form, so a plan in another form stops the
session, and a later version of rn goes on from it only when the form holds.
