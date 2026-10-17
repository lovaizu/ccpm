---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product. From it they understand, in a
short time, the mechanism that brings about the UX the product must give, and how that is checked,
and build or change the product to it.

The UX is what the user experiences using the product, and its key results are what is measured to
show how close the product brings them to their goals. Design turns that into a mechanism in
layers, each drawn from the one before and fewer than it: the UX's scenes rest on a few user stories, each one way the user
uses the product at its edge, such as a command they run; the stories are taken on by logical
components, each of which may serve several; and each component is realized by a technology. The
checks go back up: each unit, then each story, then how close each key result came. Design thinks
in this order:

1. From the UX's scenes, write the user stories they rest on: "As <the user>, I want <what they
   do>." Their reasons are the UX's goals and key results, and are not written again.
2. Decide the logical components that take on those stories, and the interactions between them.
   A logical component is divided by what it takes on; its physical form is not decided yet.
3. Choose the technology that realizes each component, and decide how it is realized physically
   and where it is placed. Technology is chosen here first.
4. Check each physical unit on its own, then check the whole: each story achieved, and each key
   result of the UX measured against the version in use, in the UX's order of priority. A change is
   taken when every story is still achieved and it brings the key results closer from the highest,
   never a lower one at the cost of a higher.

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

- <Each interaction the stories need, in the order it happens, in one sentence>

  <Why it is so, where the reader would ask>

### Physical view

<Where each unit is placed, how it is made, the components it realizes and what it depends on
outside the product>

## Verification

### Units

- <A unit>: <what is checked of it>
  - <Each check, its bar and where it runs, said plainly>

### Acceptance

- <A story>: <what shows it achieved, in one sentence>
  - <How and where that is checked, in one sentence>
- <The ID of each key result of the UX, in the UX's order of priority>: <what is measured>
  - <How and where it is measured, compared with the version in use on the same tasks>

<A change taken when every story is still achieved and no key result comes closer at the cost of a
higher one>
```

Why: the builder reads the user stories, then the components that achieve them and how they are
realized, then how the units and the whole are checked, each the ground of the next.

## Benefit

### B-1: The stories the scenes rest on

Does every scene of the UX rest on a user story, each one way the user uses the product at its
edge?

Look for: a story for a step inside the product, or one that says again what another does.

Why: the components are decided from the stories; a scene no story holds up is built by guess,
and a story for each step inside multiplies the components without the user doing more.

### B-2: Every logical component the stories need

Is every logical component the stories need there?

Why: a component left out is found only when a story it serves is built, and the architecture
must change then.

### B-3: The stories achieved by interactions

Do the interactions between the logical components achieve every user story?

Why: components that each do their part achieve no story unless their interactions do.

### B-4: No technology before it is chosen

Are the user stories and the logical components free of technology?

Why: technology brought in first shapes the stories and components to it, so they no longer
follow from what the UX essentially needs, and changing the technology means making the stories
again.

### B-5: How each component is realized

Can the reader tell how each component is realized physically, with the technology chosen for it?

Why: the builder makes each component as it is realized, and each way is made and changed in its
own way.

### B-6: Where each component is placed

Can the reader tell where each component is placed?

Why: where a component is placed decides who owns it, where it runs and when a change to it reaches
the user.

### B-7: What each component depends on outside

Can the reader tell what each component depends on outside the product?

Why: what the product depends on is where it breaks for the user first.

### B-8: Each unit checked, and how far

Can the reader tell what is checked of each physical unit, and the bar it must pass?

Why: the whole is built from units checked one by one; a unit left unchecked, or checked to no
stated bar, breaks the whole where no check shows it.

### B-9: Each story shown achieved

Can the reader tell, from the checks of the whole, whether each user story is achieved?

Why: units can each pass while a story is missed; only a check of the whole shows a story
achieved.

### B-10: Each change shown bringing the user closer

Can the reader tell, from the measures, whether a change brings the user closer to their goals, the
key results weighed in the UX's order of priority?

Why: a key result is not met or missed but come close to, so no check of a story shows it; a change
judged by no measure, or by one key result alone, can leave the user worse off while each version
looks better.
