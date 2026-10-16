---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product. From it they understand,
in a short time, the mechanism that brings about the UX the README and its pages define, and how
that is checked, and build or change the product to it.

Each item of `doc.md` applies to a design document with the mechanism and its checks as its
subject; its B-16 is answered by the logical view.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to the README>

## Goals

- <A goal, in one sentence>

## Architecture

### Logical view

<One figure: a box for each role, the user and what is outside the product included, holding its
name alone; an arrow from each to the role it acts on, labelled with what it does>

- <A goal, and the roles and interactions that achieve it, in one sentence>

### Physical view

<One figure: a frame for each place, holding its name alone; in each, a box for each unit kept
there, holding how it is made and the roles it realizes; an arrow from each unit to what it depends
on outside the product, labelled with that relation>

## Verification

### Units

- <A unit>: <what is checked of it, in one sentence>
  - <How and where that is checked, in one sentence>

### Acceptance

- <A goal>: <what shows it achieved, in one sentence>
  - <How and where that is checked, in one sentence>
```

Why: the builder reads what must be achieved, then how roles achieve it and where they are made,
then how each unit and the whole are checked, each the ground of the next.

## Benefit

### B-40: Goals

Are the goals that bring about the UX the fewest, each one such that the UX lacks something without
it and no other goal says it?

Why: the goals are what everything below is built and checked toward; a goal more is built and
kept for nothing, and two goals that say one thing are built twice.

### B-41: Roles

Are the roles the goals need found, and do their interactions achieve every goal?

Why: a goal no interaction of roles achieves is promised and never built.

### B-42: Realization

Is it clear how each role is made physically, where each is kept and runs, and what each depends on
outside the product?

Why: the builder makes and places each role from this, and what the product depends on is where it
breaks for the user first.

### B-43: Checks

Is it clear how each unit is checked, and how the whole is checked to have achieved each goal?

Why: units checked one by one build up to the whole, and only a check of the whole shows a goal
achieved.

## Usability

None: what lets the design be understood in a short time is `doc.md`'s.
