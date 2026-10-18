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
checks go back up: each unit, then each story, then how close each key result came.

The checks are built up from the least, so that a problem shows as early as it can and the product
comes closer to the user's goals for the least work. A part is checked before the whole it is in.
Its flow, whether each step happens in its order and hands on what the next takes, is checked
before its content, how good what a step makes is: the flow on the smallest task that shows it,
with stand-ins for whatever lies around the part being checked, and the content on real work,
which nothing stands in for. Each check takes the least means that shows what it is for.

Design thinks in this order:

1. From the UX's scenes, write the user stories they rest on: "As <the user>, I want <what they
   do>." Their reasons are the UX's goals and key results, and are not written again.
2. Decide the logical components that take on those stories, and the interactions between them.
   A logical component is divided by what it takes on; its physical form is not decided yet.
3. Choose the technology that realizes each component, and decide how it is realized physically
   and where it is placed. Technology is chosen here first.
4. Check each physical unit on its own, its flow and then its content, then check the whole the same
   way: its flow from end to end, each story achieved, and each key result of the UX measured
   against the version in use, in the UX's order of priority. A change is taken when every story is
   still achieved and it brings the key results closer from the highest, never a lower one at the
   cost of a higher. A key result that measures what the user pays, such as time, money or effort,
   is read from the records in its parts, not only in total, and a part that adds nothing to a
   higher key result is cut first, traded against nothing.

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
  - Flow: <the task, what stands in around the unit, the bar and where it runs>
  - Content: <the real work it makes, the bar and where it runs>, where the unit makes something

### Acceptance

- Flow: <the whole from end to end: the task, what stands in, and what shows each step happened>
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

### B-11: Each case met by a mechanism already there

Can the reader tell that each case the stories meet is taken by a component or a check already
there, with no path of its own?

Look at: each path or component that serves one case alone; one for a case another component already
handles or a check already stops fails.

Why: every path of its own is one more thing for users to learn and builders to keep right.

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

### B-12: An AI part checked on the model it names

Can the reader tell that each part run by an AI is checked on the model the part names, never a
smaller one?

Why: a smaller model's slips are not the product's, and the product's own pass unseen beside them.

### B-13: An AI part judged from its records

Can the reader tell that each part run by an AI is judged from the records of every conversation
and agent it started, not from its outcome alone?

Why: the outcome shows that something went wrong; only the records show where.

### B-14: The flow checked apart from the content

Can the reader tell that each flow is checked apart from the content, on the smallest task that
shows it, with stand-ins for whatever lies around the part being checked?

Why: a check of the flow and the content at once costs the whole work each time it runs, takes
whatever path the work leads it down rather than the one meant, and, failing, does not say which
went wrong.

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

### B-15: What the user pays seen in its parts

Can the reader tell that each key result measuring what the user pays, such as time, money or
effort, is read from the records in its parts, not only in total?

Why: in a total, a part that gives the user nothing hides among those that do, and the user pays
for it on every use.
