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

### B-40: Everything the UX needs

Can the reader tell from the goals everything that must hold for the UX the README and its pages
define to come about?

Why: the goals are what everything below is built and checked toward; what the UX needs and no goal
names is built by chance or not at all.

### B-44: Each goal needed

Can the reader tell, for each goal, what the UX would lack without it?

Why: a goal the UX does not need is built and kept for nothing, and the builder takes in more than
the mechanism needs.

### B-41: How the roles achieve the goals

Can the reader tell the roles the goals need, and how their interactions achieve every goal?

Why: a goal no interaction of roles achieves is promised and never built.

### B-42: How each role is made

Can the reader tell how each role is made physically, such as a prompt, a script, a hook or data?

Why: each is made, changed and checked in its own way, and the builder cannot make a role without
knowing which.

### B-45: Where each role is placed

Can the reader tell where each role is kept and where it runs, such as shipped with the product, in
the user's repository, on the user's machine or in CI?

Why: where a role is kept decides who owns it and when a change reaches the user, and where it runs
decides where it can be checked.

### B-46: What each role depends on

Can the reader tell what each role depends on outside the product?

Why: what the product needs in place is where it breaks for the user first.

### B-43: How each unit is checked

Can the reader tell how each unit is checked, and where?

Why: the whole is built up from units checked one by one; a unit left unchecked breaks the whole
where no check shows it.

### B-47: How the whole is checked for each goal

Can the reader tell how the whole is checked to have achieved each goal, and where?

Why: units can each pass while a goal is missed; only a check of the whole shows a goal achieved.

## Usability

None: what lets the design be understood in a short time is `doc.md`'s.
