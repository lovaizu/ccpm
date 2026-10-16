---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product. From it they understand, in a
short time, the mechanism that brings about the UX the product must bring about, and how that is
checked, and build or change the product to it.

Each item of `doc.md` applies to a design document with the mechanism and its checks as its
subject; its B-16 is answered by the logical view.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to where the UX is defined>

## Goals

- <A goal, in one sentence>

## Architecture

### Logical view

<One figure: a box for each role, holding its name alone; an arrow from each to the role it acts
on, labelled with what it does>

- <A goal, and the roles and interactions that achieve it, in one sentence>

### Physical view

<One figure: a frame for each place, holding its name alone; in each, a box for each unit placed
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

Why: the builder reads the goals, then the roles that achieve them and how they are realized, then
how the units and the whole are checked, each the ground of the next.

## Benefit

### B-17: Each goal needed

Can the reader tell, for each goal, what the UX would lack without it?

Why: the goals bringing about the UX are the fewest only when each is needed; a goal more is built
and kept for nothing.

### B-18: No two goals overlapping

Can the reader tell, for each goal, what it holds that no other goal holds?

Why: two goals that hold one thing are achieved twice, in two ways that may not fit together.

### B-19: The roles the goals need

Can the reader tell every role the goals need?

Why: a role left out is found only when a goal it serves is built, and the architecture must
change then.

### B-20: Each goal achieved by interactions

Can the reader tell, for each goal, how the interactions between roles achieve it?

Why: roles that each do their part achieve no goal unless their interactions do.

### B-21: How each role is realized

Can the reader tell how each role is realized physically?

Why: the builder makes each role as it is realized, and each way of realizing is made and changed
in its own way.

### B-22: Where each role is placed

Can the reader tell where each role is placed?

Why: where a role is placed decides who owns it, where it runs and when a change to it reaches the
user.

### B-23: What each role depends on outside

Can the reader tell what each role depends on outside the product?

Why: what the product depends on is where it breaks for the user first.

### B-24: Checks built up unit by unit

Can the reader tell, for each unit of the physical view, how it is checked?

Why: the check of the whole is built up from units checked one by one, and a unit left unchecked
breaks the whole where no check shows it.

### B-25: The whole checked for each goal

Can the reader tell, for each goal, how the whole is checked to have achieved it?

Why: units can each pass while a goal is missed; only a check of the whole shows a goal achieved.

## Usability

None: what lets the design be understood in a short time is `doc.md`'s.
