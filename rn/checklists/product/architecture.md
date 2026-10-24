---
name: architecture
version: 1
made_from:
  checklist: 1
  usability: 1
---

# Architecture

An architecture is read by whoever builds or changes the product and by whoever approves it. From
it they grasp, in a short time, how the product is put together to give the UX the product must
give, and how each part and the user stories are checked, and build, change or approve the product
by it.

An architecture holds the principles the product rests on, the parts it is made of, how they act on
one another and where each is placed; and how each is checked. These are what an approval rests
on, as changing one changes what was approved. How each part behaves in each case is held where the
part is built and checked: in the tests of a part made of code, each a Given, a When and a Then, and
in the steps of a part run by an AI; in the architecture it would be decided twice and drift, and
every finding made while building would change what was approved.

The parts are drawn from the UX in layers, each fewer than the one before: the UX's scenes rest on a
few user stories, each one way the user uses the product at its edge, such as a command they run;
the stories are taken on by logical components, each of which may serve several; and each component
is realized by a technology, chosen at this layer alone, so the stories and the components follow
from what the UX needs. What to check of each kind of part and of the stories, and how far, is the
project's rule, not the architecture's: the architecture links it, and where the project has none
for a kind, the rule is made first. An architecture built on a base architecture writes only what is
its own, and links the base for the rest.

## Format

### F-1: Shape

Scope: whole

Does the architecture follow this template, headings included?

```markdown
# <Product name> architecture

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

## Test

<A link to the project's rules for how each kind of part and the user stories are checked>

- <What this product's checks need that the project's rules do not give, if anything>
```

Each line of a list is one sentence understood alone, its why, where it has one, after a blank line
indented under it; nothing is set in bold.

Why: the builder and the approver read the principles, then what the product gives, then the parts
that give it and where they are, then how each is checked, each the ground of the next; they
skim the lines and read a why only where they question one.

## Benefit

### B-1: The ground every decision rests on

Scope: its part

From the opening, can the reader tell the ground every decision of the architecture rests on: how
the product is put together, and the principles, its own each in a line and those of what it is
built on by a link?

Look for: an opening that says what the document holds in place of how the product is put together;
a principle of what it is built on written again rather than linked; a means, such as a tool, a
format or a paper's method, given as a principle.

Why: each decision's why can hold on its own while the decisions together break a principle no one
wrote down; principles said once are what every decision, and every change, is held to.

### B-2: The stories the scenes rest on

Scope: its part

Does every scene of the UX rest on a user story, each one way the user uses the product at its
edge?

Look for: a scene no story holds up; a story for a step inside the product; a story that says again
what another does; a story named by the technology that realizes it.

Why: the components are decided from the stories; a scene no story holds up is built by guess, a
story for each step inside multiplies the components without the user doing more, and a story
shaped to a technology must be made again when the technology changes.

### B-3: The stories achieved by the components

Scope: its part

Can the reader see, from the figure and the lines beside it, how the logical components achieve
every user story, in the order they act?

Look for:
- a component a story needs missing from the figure;
- a story no run of arrows achieves, or a step of one left for the reader to guess, such as what a
  component does with what it is handed;
- the order the arrows run in, or a choice the reader would question, left out of the lines;
- a box holding a description or a technology rather than the component's name;
- a path or a component that serves one case alone, where another component already takes it or a
  check already stops it.

Why: components that each do their part achieve no story unless their interactions do; a component
found missing only when a story it serves is built changes the architecture then; a component
shaped to its technology must be remade with it; and every path of its own is one more thing for
users to learn and builders to keep right.

### B-4: Each component realized

Scope: its part

Can the reader tell, from the tree and the lines beside it, where each component is placed and what
it is made of, what the product depends on outside itself and how it is started?

Look for: a component of the figure with no place in the tree; a place with no kind beside it, such
as `<Python 3>`; files drawn as boxes rather than as a tree.

Why: the builder makes each component as it is realized; where it is placed decides who owns it,
where it runs and when a change to it reaches the user; and what the product depends on is where it
breaks for the user first.

### B-5: Each part and the stories checked by the project's rules

Scope: its part

Can the reader tell, for each kind of part in the tree and for the user stories, the project's rule
that says how it is checked, from a link to it?

Look for:
- a kind of part, such as code or a prompt, or the user stories, that no rule of the project
  checks, which is a rule to be made first rather than a check written here;
- a check written here that the project's rule already gives, or that differs from it;
- a case's inputs, stand-ins or bar to pass, which belong to the tests.

Why: what to check and how far is decided once for the project, so every product is held to the
same bar; written again in each architecture, the bars drift from the rule and from one another,
and a case's detail changes with every test while the approval rests on the architecture.

### B-6: Every decision true together with the principles

Scope: whole

Can the reader take each arrow, each line and each check as holding together with every principle
the opening names and with every other line?

Look for: an arrow that hands a part what a principle says it must not see; a check a principle
gives to some part that no part makes; two lines, each right on its own, that ask or give opposite
things, such as one keeping a part from what another hands it.

Why: a decision read alone looks right by its own why; one that breaks a principle undoes what the
principle was there to bring about, and shows only when the product fails at it; of two lines that
cannot both hold, the builder follows one and breaks the other.

### B-7: Each line a decision the approval rests on

Scope: whole

Is each line of the architecture one whose change would change what was approved, said in one place
alone?

Look for:
- how a part behaves in a case, a count, a bound, a value, or a list of what a part does step by
  step, which belongs to the part's tests, as a Given, a When and a Then, or to its steps;
- a line that says again, in other words, what the figure, the tree, another line, the UX or the
  architecture it is built on says, which is linked instead;
- how a decision was reached, or where the work stands;
- terms gathered ahead of the lines that use them, or a comparison or an example for an idea the
  reader already holds.

Why: the reader grasps how the product is put together only where nothing else stands among it; a
behavior written here is decided twice and drifts from where it is built, and every finding made
while building changes what was approved and sends it back to be approved again; two places that
say one thing come to disagree as one changes, and a history or a status read as a decision turns
wrong while it is still believed.

### B-8: Each line understood where it is read

Scope: whole

Can the reader understand each line where they meet it, reading once from the top?

Look for:
- a term of the UX used where the opening does not link to where it is defined, or a plain word used
  in a sense of its own that no line explains;
- a name of another product, such as a plugin the product uses, with no link or line saying what it
  is;
- one component or thing under two names, or one name for two things;
- a line resting on a reason or a part that comes only after it.

Why: a term never explained is read with a guess at its meaning, a second name is taken for a
second thing, and a reader sent ahead or back loses the picture one reading from the top would
give; where the guess is wrong, what they approve or build differs from what was meant.
