---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product. From it they understand, in a
short time, the mechanism that brings about the UX the product must give, and how that is checked,
and build or change the product to it.

The UX is what the user experiences using the product. Design is analyzing the UX to find the
essential, minimal functions that make it possible, and deciding the components that take on those
functions. Many UX are held up by few functions, and one component takes on several functions, so
the numbers narrow in the order UX, functions, components.

Each item of `doc.md` applies to a design document with the mechanism and its checks as its
subject; its B-16 is answered by the logical view.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to where the UX is defined>

## Functions

- <A function, in one sentence>

## Architecture

### Logical view

<One figure: a box for each component, holding its name alone; an arrow from each to the component
it acts on, labelled with what it does>

- <A function, and the components and interactions that achieve it, in one sentence>

### Physical view

<One figure: a frame for each place, holding its name alone; in each, a box for each unit placed
there, holding how it is made and the components it realizes; an arrow from each unit to what it
depends on outside the product, labelled with that relation>

## Verification

### Units

- <A unit>: <what is checked of it, in one sentence>
  - <How and where that is checked, in one sentence>

### Acceptance

- <A function>: <what shows it achieved, in one sentence>
  - <How and where that is checked, in one sentence>
```

Why: the builder reads the functions, then the components that achieve them and how they are
realized, then how the units and the whole are checked, each the ground of the next.

## Benefit

### B-17: The minimal functions

Are the functions the minimum the UX essentially needs?

Why: functions that follow the UX one by one restate it, and the mechanism that makes it possible is
never found; the builder makes a separate mechanism for each, and the design grows with the UX.

### B-18: Every component the functions need

Is every component the functions need there?

Why: a component left out is found only when a function it serves is built, and the architecture
must change then.

### B-19: The functions achieved by interactions

Do the interactions between the components achieve every function?

Why: components that each do their part achieve no function unless their interactions do.

### B-20: How each component is realized

Can the reader tell how each component is realized physically?

Why: the builder makes each component as it is realized, and each way is made and changed in its
own way.

### B-21: Where each component is placed

Can the reader tell where each component is placed?

Why: where a component is placed decides who owns it, where it runs and when a change to it reaches
the user.

### B-22: What each component depends on outside

Can the reader tell what each component depends on outside the product?

Why: what the product depends on is where it breaks for the user first.

### B-23: Checks built up unit by unit

Can the reader tell how the checks build up unit by unit?

Why: the whole is built up from units checked one by one, and a unit left unchecked breaks the
whole where no check shows it.

### B-24: The whole checked

Can the reader tell how the whole is checked to have achieved each function?

Why: units can each pass while a function is missed; only a check of the whole shows a function
achieved.

## Usability

None: what lets the design be understood in a short time is `doc.md`'s.
