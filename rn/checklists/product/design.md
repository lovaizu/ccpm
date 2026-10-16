---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product. From it they understand, in a
short time, the mechanism that brings about the UX the product must give, and how that is checked,
and build or change the product to it.

The UX is what the user experiences using the product. Design thinks in this order:

1. From the UX, write a user story for each thing a user does with the product, such as each
   command they run: "As <the user>, I want <what they do>." Their reasons are the UX's benefits,
   and are not written again.
2. Decide the logical components that take on those stories, and the interactions between them.
   A logical component is divided by what it takes on; its physical form is not decided yet.
3. Choose the technology that realizes each component, and decide how it is realized physically
   and where it is placed. Technology is chosen here first.
4. For each benefit the UX names, decide, with how it is realized, the qualities that come with
   giving it: must-be, what must be kept for the benefit to hold; and better the more, what
   satisfies the user more the better it is, such as less time or less cost.
5. Check each physical unit on its own, build those checks up, then check the whole.

Many scenes are held up by few stories, and one component takes on several stories, so the numbers
narrow in the order scenes, stories, components.

Each item of `readability.md` applies to a design document with the mechanism and its checks as its
subject; its B-16 is answered by the logical view.

## Format

### F-1: Shape

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<The design's main point, with a link to where the UX is defined>

## User stories

- As <the user>, I want <what they do with the product>.

## Architecture

### Logical view

<One figure: a box for each logical component, holding its name alone; an arrow from each to the
component it acts on, labelled with what it does>

- <A story, and the components and interactions that achieve it, in one sentence>

### Physical view

<One figure: a frame for each place, holding its name alone; in each, a box for each unit placed
there, holding how it is made and the components it realizes; an arrow from each unit to what it
depends on outside the product, labelled with that relation>

## Quality

- <A benefit the UX names>
  - Must-be: <what must be kept for it to hold, in one sentence>
  - Better the more: <what satisfies the user more the better it is, in one sentence>

## Verification

### Units

- <A unit>: <what is checked of it, in one sentence>
  - <How and where that is checked, in one sentence>

### Acceptance

- <A story>: <what shows it achieved, in one sentence>
  - <How and where that is checked, in one sentence>
- <A must-be quality>: <what shows it kept, in one sentence>
  - <How and where that is checked, in one sentence>
- <A better-the-more quality>: <what is measured, in one sentence>
  - <How and where it is measured and compared with the last version, in one sentence>
```

Why: the builder reads the user stories, then the components that achieve them and how they are
realized, then the qualities that come with each benefit, then how the units and the whole are
checked, each the ground of the next.

## Benefit

### B-29: Each story serving a benefit

Does each user story serve one or more of the UX's benefits?

Why: a story that serves none is something the user does for nothing, and the builder builds and
keeps it for nothing.

### B-18: Every logical component the stories need

Is every logical component the stories need there?

Why: a component left out is found only when a story it serves is built, and the architecture
must change then.

### B-19: The stories achieved by interactions

Do the interactions between the logical components achieve every user story?

Why: components that each do their part achieve no story unless their interactions do.

### B-25: No technology before it is chosen

Are the user stories and the logical components free of technology?

Why: technology brought in first shapes the stories and components to it, so they no longer
follow from what the UX essentially needs, and changing the technology means making the stories
again.

### B-20: How each component is realized

Can the reader tell how each component is realized physically, with the technology chosen for it?

Why: the builder makes each component as it is realized, and each way is made and changed in its
own way.

### B-21: Where each component is placed

Can the reader tell where each component is placed?

Why: where a component is placed decides who owns it, where it runs and when a change to it reaches
the user.

### B-22: What each component depends on outside

Can the reader tell what each component depends on outside the product?

Why: what the product depends on is where it breaks for the user first.

### B-27: The qualities that come with each benefit

Can the reader tell, for each benefit the UX names, what must be kept for it to hold and what is
better the more in giving it?

Why: these qualities come with giving a benefit in the way chosen; drawn from nothing they never
end, and a quality left unnamed is broken or given up without anyone deciding to.

### B-23: Checks built up unit by unit

Can the reader tell how the checks of each physical unit, made on its own, build up to the whole?

Why: the whole is built up from units checked one by one, and a unit left unchecked breaks the
whole where no check shows it.

### B-24: The whole checked

Can the reader tell how the whole is checked to have achieved each user story?

Why: units can each pass while a story is missed; only a check of the whole shows a story
achieved.

### B-28: Must-be, checked

Can the reader tell how each must-be quality is checked as kept?

Why: a must-be quality is not a story, so no check of a story shows it kept; left unchecked,
it breaks without anyone seeing.

### B-26: Better the more, measured

Can the reader tell, for each better-the-more quality, what is measured and how it
is compared with the last version?

Why: such a quality is neither achieved nor missed, so no check of a story shows it; left
unmeasured, it grows worse with each change without anyone seeing.
