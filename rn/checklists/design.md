---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product. From it they quickly
understand the mechanism that brings about the UX the README and its pages define, and how that is
checked, and build or change the product to it.

Each item of `doc.md` applies to a design document with the mechanism and its checks as its
subject; its B-16 is answered by the logical figure.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to the README>

## Goals

- <What must hold for the UX to come about, in one sentence>

## Logical structure

<One figure: a box for each part, the user and what is outside the product included, holding its
name alone; an arrow from each to what it acts on, labelled with what it does>

- <A goal, and the parts that hold it, in one sentence>

## Physical structure

<One figure: a frame for each place, holding its name alone; in each, a box for each unit kept
there, holding its kind and the parts it makes; an arrow from each unit to what it depends on,
labelled with that relation>

## Verification

- <A goal>: <what shows it holds, in one sentence>
  - <How and where that is checked, in one sentence>
```

Why: the builder reads what must hold, then where it is held, then how it is checked, each the
ground of the next, and finds the same thing under the same heading in every product.

## Benefit

### B-40: What the UX needs

Can the reader tell, from the goals, everything that must hold for the UX the README and its pages
define to come about, including what the user takes for granted and what others rely on?

Why: the goals are what the builder builds toward; what the UX needs and no goal names is built by
chance or not at all.

### B-41: The parts that hold each goal

Can the reader tell, for each goal, which parts hold it?

Why: a builder who cannot tell where a goal is held builds it twice or not at all, and the one
changing a part cannot tell which goals the change can break.

### B-42: How the parts work together

Can the reader tell from the logical figure what each part does and to which other part?

Why: a goal is held by parts acting on one another; a builder who sees only the parts cannot tell
what a change to one does to the others.

### B-43: Where each part is kept

Can the reader tell from the physical figure where each part is kept, such as shipped with the
product, in the user's repository or in a service?

Why: where a part is kept decides who owns it and when a change to it reaches the user.

### B-44: Where each part runs

Can the reader tell from the physical figure where each part runs, such as on the user's machine or
in CI?

Why: a part runs only where it is placed, and is checked only there.

### B-45: What each part depends on

Can the reader tell from the physical figure what each part depends on outside the product?

Why: what the product needs in place is where it breaks for the user first.

### B-46: What shows each goal holds

Can the reader tell, for each goal, what shows it holds, and say of the product whether it does,
yes or no?

Why: a goal that cannot be shown to hold is taken as held because no one can show it does not.

### B-47: How each goal is checked

Can the reader tell, for each goal, how what shows it holds is checked, and where that check is?

Why: a check the builder cannot find or run is not made, and the goal goes unchecked after each
change.

## Usability

None: what makes the design quick to take in is `doc.md`'s.
