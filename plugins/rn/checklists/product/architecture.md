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
project's rule, not the architecture's: the architecture links it. An architecture built on a base
architecture writes only what is its own, and links the base for the rest.

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

<One figure, an SVG file beside the document shown as an image: a box for each logical component,
holding its name alone, its shape saying whether an AI or code does its work, with a legend, and a
frame round the boxes that run in one place or make one product; an arrow from each to the
component it acts on, labelled in a few words with what it does; the boxes placed so the arrows run
in the order they act and cross none, readable in light and dark>

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
skim the lines and read a why only where they question one. The logical view is the one figure
whose placing and frames carry what the reader takes in at a glance, so it is drawn by hand, where
a tool's layout sets them by its own rules; a box's shape shows at a glance which parts an AI does,
whose work varies from run to run, and which code does the same each time.

## Benefit

### B-1: The ground every decision rests on

Scope: its part

From the opening, can the reader tell the ground every decision of the architecture rests on: how
the product is put together, and the principles, its own each in a line and those of what it is
built on by a link?

Signs: the opening says how the product is put together, not what the document holds; each
principle of what it is built on is reached by its link, not written again; each principle is a
rule the decisions are held to, and a means, such as a tool, a format or a paper's method, is
left to the part that uses it.

Why: each decision's why can hold on its own while the decisions together break a principle no one
wrote down; principles said once are what every decision, and every change, is held to.

### B-2: The stories the scenes rest on

Scope: its part

Does every scene of the UX rest on a user story, each one way the user uses the product at its
edge?

Tried by: every scene of the UX the opening links, each set beside the story it rests on.

Signs: each scene leads to a story that holds it up; each story is a thing the user does at the
product's edge, such as a command they run, not a step inside the product; each story says what no
other does; each story is named by what the user does, so it holds when the technology changes.

Why: the components are decided from the stories; a scene no story holds up is built by guess, a
story for each step inside multiplies the components without the user doing more, and a story
shaped to a technology must be made again when the technology changes.

### B-3: The stories achieved by the components

Scope: its part

Can the reader see, from the figure and the lines beside it, how the logical components achieve
every user story, in the order they act?

Tried by: every user story followed through the figure's arrows and the lines beside it, from the
first component it reaches to its end.

Signs:
- each component a story needs has its box in the figure;
- each story is achieved by a run of arrows, each step of it told by an arrow's label or a line,
  such as what a component does with what it is handed;
- the lines give the order the arrows run in, and the why of each choice the reader would question;
- each box holds the component's name, not a description or a technology;
- each case is taken by a component that already takes others or stopped by a check already there,
  so each path and component serves more than one case.

Why: components that each do their part achieve no story unless their interactions do; a component
found missing only when a story it serves is built changes the architecture then; a component
shaped to its technology must be remade with it; and every path of its own is one more thing for
users to learn and builders to keep right.

### B-4: Each component realized

Scope: its part

Can the reader tell, from the tree and the lines beside it, where each component is placed and what
it is made of, what the product depends on outside itself and how it is started?

Tried by: every box of the figure looked up in the tree.

Signs: each component of the figure is found at its place in the tree; each place has its kind
beside it, such as `<Python 3>`; the files are shown as a tree, not drawn as boxes.

Why: the builder makes each component as it is realized; where it is placed decides who owns it,
where it runs and when a change to it reaches the user; and what the product depends on is where it
breaks for the user first.

### B-5: Each part and the stories checked by the project's rules

Scope: its part

Can the reader tell, for each kind of part in the tree and for the user stories, the project's rule
that says how it is checked, from a link to it?

Tried by: the link followed, and each kind of part in the tree and the user stories found in the
rule it reaches.

Signs:
- each kind of part, such as code or a prompt, and the user stories are checked by a rule of the
  project the link reaches;
- a check written here is one the project's rule does not give, and agrees with it;
- a case's inputs, stand-ins and bar to pass are left to the tests.

Why: what to check and how far is decided once for the project, so every product is held to the
same bar; written again in each architecture, the bars drift from the rule and from one another,
and a case's detail changes with every test while the approval rests on the architecture.

### B-6: The decisions followed together with the principles

Scope: whole

Can the builder follow each arrow, each line and each check together with the principles the
opening names and with the other lines, each giving what the others ask?

Tried by: each principle the opening names set beside every arrow, line and check it bears on, and
the lines that bear on one part set beside one another.

Signs: each arrow hands a part only what the principles let it see; each check a principle gives to
some part is made by a part; the lines that bear on one thing ask and give the same, such as what
one hands a part and what another lets that part have.

Why: a decision read alone looks right by its own why; one that breaks a principle undoes what the
principle was there to bring about, and shows only when the product fails at it; of two lines that
cannot both hold, the builder follows one and breaks the other.

### B-7: Each line a decision the approval rests on

Scope: whole

Is each line of the architecture one whose change would change what was approved, said in one place
alone?

Signs:
- how a part behaves in a case, a count, a bound, a value, or a list of what a part does step by
  step, is left to the part's tests, as a Given, a When and a Then, or to its steps;
- what the figure, the tree, another line, the UX or the architecture it is built on says is said
  there alone, and reached here by a link;
- each line says what holds now, not how a decision was reached or where the work stands;
- each term is given at the line that first uses it, and a comparison or an example is given only
  for an idea the reader does not already hold.

Why: the reader grasps how the product is put together only where nothing else stands among it; a
behavior written here is decided twice and drifts from where it is built, and every finding made
while building changes what was approved and sends it back to be approved again; two places that
say one thing come to disagree as one changes, and a history or a status read as a decision turns
wrong while it is still believed.

### B-8: Each line understood where it is read

Scope: whole

Can the reader understand each line where they meet it, reading once from the top?

Signs:
- each term of the UX is reached through the opening's link to where it is defined, and each plain
  word used in a sense of its own is explained by a line;
- each name of another product, such as a plugin the product uses, has a link or a line saying what
  it is;
- each component or thing has one name, and each name is of one thing;
- each line rests on reasons and parts that come before it.

Why: a term never explained is read with a guess at its meaning, a second name is taken for a
second thing, and a reader sent ahead or back loses the picture one reading from the top would
give; where the guess is wrong, what they approve or build differs from what was meant.
