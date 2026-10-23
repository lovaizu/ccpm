---
name: design
version: 0.3.0
---

# Design document

A design document is read by whoever builds or changes the product and by whoever approves it. From
it they grasp, in a short time, how the product is put together to give the UX the product must
give, and how far each part and the whole are checked, and build, change or approve the product by
it.

A design document holds the product's architecture: what the product rests on, the parts it is made
of, how they act on one another and where each is placed; and how far each is checked. These are
what an approval rests on, as changing one changes what was approved. How each part behaves in each
case is held where the part is built and checked: in the tests of a part made of code, each a Given,
a When and a Then, and in the steps of a part run by an AI; in the design document it would be
decided twice and drift, and every finding made while building would change what was approved.

The parts are drawn from the UX in layers, each fewer than the one before: the UX's scenes rest on a
few user stories, each one way the user uses the product at its edge, such as a command they run;
the stories are taken on by logical components, each of which may serve several; and each component
is realized by a technology, chosen at this layer alone, so the stories and the components follow
from what the UX needs. The checks go back up: each unit, then each story, then how close each key
result came.

Each item of `usability.md` applies to a design document with the architecture and its checks as its
subject; its B-16 is answered by the logical view's figure.

## Format

### F-1: Shape

Scope: whole

Does the design document follow this template, headings included?

```markdown
# <Product name> design

<How the product is put together, in a sentence or two, with a link to where the UX is defined>

<The principles it rests on: a link to those of what it is built on, and its own, each in a
line>

## User stories

- As <the user>, I want <what they do with the product>.

## Architecture

### Logical view

<One figure: a box for each logical component, holding its name alone; an arrow from each to the
component it acts on, labelled with what it does>

- <What the figure cannot show, such as the order the arrows run in or a choice the reader would
  question, with why>

### Physical view

<A tree of where each component is placed, each with what it is made of>

- <What the product depends on outside itself, and how it is started>

## Verification

### Units

- <A unit>: <what is checked of it, and how far>

### Acceptance

- <A story>: <what shows it achieved, and how far>
- <The ID of each key result of the UX, in the UX's order of priority>: <what is measured, compared
  with the version in use on the same tasks>

<A change taken when every story is still achieved and no key result comes closer at the cost of a
higher one>
```

Why: the builder and the approver read the principles, then what the product gives, then the parts
that give it and where they are, then how far each is checked, each the ground of the next.

## Benefit

### B-1: The principles it rests on

Scope: its part

Can the reader tell, from the opening, the principles every decision of the design rests on, its
own each in a line and those of what it is built on by a link?

Why: each decision's why can hold on its own while the decisions together break a principle no one
wrote down; principles said once are what every decision, and every change, is held to.

### B-2: The stories the scenes rest on

Scope: its part

Does every scene of the UX rest on a user story, each one way the user uses the product at its
edge?

Look for: a story for a step inside the product, or one that says again what another does.

Why: the components are decided from the stories; a scene no story holds up is built by guess,
and a story for each step inside multiplies the components without the user doing more.

### B-3: Every logical component the stories need

Scope: its part

Is every logical component the stories need in the figure?

Why: a component left out is found only when a story it serves is built, and the architecture
must change then.

### B-4: The stories achieved by the arrows

Scope: its part

Do the figure's arrows, in the order the lines beside it give, achieve every user story?

Why: components that each do their part achieve no story unless their interactions do.

### B-5: Stories and components that outlast a change of technology

Scope: its part

Are the user stories and the logical components free of technology?

Why: technology brought in first shapes the stories and components to it, so they no longer
follow from what the UX essentially needs, and changing the technology means making the stories
again.

### B-6: Where each component is placed, and what it is made of

Scope: its part

Can the reader tell from the tree where each component is placed and what it is made of?

Why: the builder makes each component as it is realized; where it is placed decides who owns it,
where it runs and when a change to it reaches the user.

### B-7: What the product depends on outside

Scope: its part

Can the reader tell what the product depends on outside itself, and how it is started?

Why: what the product depends on is where it breaks for the user first.

### B-8: Each unit checked, and how far

Scope: its part

Can the reader tell what is checked of each unit of the tree, and the bar it must pass?

Look for: a part run by an AI checked on another model than its users run it on, such as one smaller
than Claude Code's default, or judged from its outcome rather than the records of every
conversation and agent it started; a flow checked together with the content, rather than on the
smallest task that shows it, with stand-ins for whatever lies around the part.

Why: the whole is built from units checked one by one; a unit left unchecked, or checked to no
stated bar, breaks the whole where no check shows it. A smaller model's slips are not the product's,
and only the records show where a run went wrong; a check of the flow and the content at once costs
the whole work each time and does not say which went wrong.

### B-9: Each story shown achieved

Scope: its part

Can the reader tell, from the checks of the whole, whether each user story is achieved?

Why: units can each pass while a story is missed; only a check of the whole shows a story
achieved.

### B-10: Each change shown bringing the user closer

Scope: its part

Can the reader tell, from the measures, whether a change brings the user closer to their goals, the
key results weighed in the UX's order of priority?

Look for: a key result measuring what the user pays, such as time, money or effort, read only in
total rather than from the records in its parts.

Why: a key result is not met or missed but come close to, so no check of a story shows it; a change
judged by no measure, or by one key result alone, can leave the user worse off while each version
looks better. In a total, a part that gives the user nothing hides among those that do.

### B-11: The architecture taken in at one reading

Scope: whole

Can the reader take in the architecture from the figures, the tree and the lines beside them, each
line one whose change would change what was approved?

Look for: how a part behaves in a case, a count, a bound, a value, or a list of what a part does
step by step; each belongs to the part's tests, as a Given, a When and a Then, or to its steps.

Why: the reader grasps how the product is put together only where nothing else stands among it; a
behavior written here is decided twice and drifts from where it is built, and every finding made
while building changes what was approved and sends it back to be approved again.

### B-12: Each case met by a mechanism already there

Scope: whole

Can the reader tell that each case the stories meet is taken by a component or a check already
there, with no path of its own?

Look at: each path or component that serves one case alone; one for a case another component already
handles or a check already stops fails.

Why: every path of its own is one more thing for users to learn and builders to keep right.

### B-13: Each decision held to the principles

Scope: whole

Can the reader find that each arrow of the logical view and each check keeps every principle the
design rests on?

Look for: an arrow that hands a part what a principle says it must not see; a check a principle
gives to some part that no part makes.

Why: a decision read alone looks right by its own why; one that breaks a principle undoes what the
principle was there to bring about, and shows only when the product fails at it.
