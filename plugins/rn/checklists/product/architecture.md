# Architecture

An architecture is read by whoever builds or changes the product and by whoever approves it. From it
they grasp how the product is put together to give the experience its UX sets, and how each part and
each user story is checked. They build, change or approve the product by it.

An approval rests on the decisions whose change would change what was approved: the principles, the
components, how they act on one another, where each runs or is kept, where their files are kept,
and how heavily each is checked. So the architecture holds those alone. How a part behaves in each
case is decided where the part is built: in its tests if it is code, and in its steps if an AI runs
it. The contents of each data, such as its fields, are decided where the data is built too, and its
schema's file shows in the directory structure. The parts are drawn from the UX in layers. Its
scenes rest on a few user stories, each one way the user uses the product at its edge, such as a
command they run.

Whoever makes the architecture draws the components from what the user stories tell, in two kinds. A
role is one that acts in a story, and Components draws the roles with the responsibilities placed in
them. A data is what the roles pass or hold, and the data model alone draws the data. Whoever makes
the architecture cuts no component by function or by stage of processing, nor to fit a technology,
and chooses a technology for each component after.

The architecture has two views, after Kruchten's "The 4+1 View Model of Architecture" (1995). The
logical view tells what the product takes on, whatever place it runs in. The physical view tells
where the product runs and where its data is kept. The sequences of each user story are 4+1's
scenarios, and are placed in the logical view. 4+1's development view is the directory structure,
placed in the physical view. Each section and each kind of figure takes the name a software engineer
already knows, so the reader finds each where they look for it. A figure of a structure is drawn by
hand, as the placing of its boxes carries what the reader takes in at a glance. A sequence has one
layout, its order down the page, so Mermaid draws it from text. The directory structure is a tree in
text, as the files lie. How heavily a part is checked follows from what a failure of it would cost
the user, which differs from product to product, so the approver weighs it here. An architecture
built on another links that one and writes only what is its own.

## Format

````markdown
# <Product name> architecture

<How the product is put together, in a sentence or two, with a link to its UX>

<The principles it rests on: a link to those of what it is built on, and its own, each in a line>

## User stories

- As <the user>, I want <what they do with the product>.

## Architecture

### Logical view

#### Components

<One SVG figure: a box for each role the user stories need, holding its name and the
responsibilities placed in it in a few words, its shape saying whether an AI or code runs it, with a
legend; an arrow from each role to the role it hands on to, labelled with the data it hands on,
named as in the data model; the boxes placed so the arrows run in the order they act and cross
none>

- <A choice the figure shows that the reader would question, with why>

#### Data model

<One SVG figure: a box for each data the roles pass or hold, holding its name alone; a line
between two data for each relation between them, labelled in a few words with what it is>

#### Sequences

<For each user story, a Mermaid sequence diagram: a participant for each role the story reaches,
named as in Components, and a message for each step, labelled in a few words with the data
handed on, named as in the data model>

- <A choice the diagrams show that the reader would question, with why>

### Physical view

#### Deployment

<One SVG figure: a box for each machine or runtime the product runs in, such as the user's computer
or Claude Code, holding by their names the roles that run there and the data kept there; a box for
each thing outside the product they depend on, with an arrow labelled with what is used>

- <How the product is started>

#### Directory structure

```text
<A tree of the folders and files that hold the code of each role and the files of each data, such
as its schema, each named with the component it holds and what it is made of, such as `Python 3`>
```

## Test

<A link to the project's rules for how each kind of part and the user stories are checked, where it
has them>

- <How heavily a part is checked beyond those rules, such as by property tests or mutation testing,
  or that it is checked by them alone, with what a failure of it would cost the user>
````

Each SVG figure is a file beside the document, shown as an image and readable in light and dark.

## Questions

### Q-1: The ground of every decision

From the opening, can the reader tell how the product is put together and the principles every
decision is held to?

Why: each decision can hold by its own reason while the decisions together break a principle no one
wrote down. A principle is a rule the decisions are held to; a means such as a tool or a format
belongs to the part that uses it.

### Q-2: The stories the scenes rest on

Does every scene of the UX rest on a user story, a thing the user does at the product's edge?

Why: the components are drawn from the stories, so a scene no story holds up is built by guess. A
story for a step inside the product adds components without the user doing more, and a story named
by a technology rather than by what the user does must be made again when the technology changes.

### Q-3: Each story followed through the components

Can the reader follow each user story through its sequence, from the first component it reaches to
its end, along the arrows of Components, with the data each role hands on or holds at each step?

Why: components that each do their part achieve no story unless their interactions do. A component
found missing only when its story is built changes the architecture then, after the approval. A
data that the reader cannot follow from the role that makes it to the role that uses it is made in
one form and read in another.

### Q-4: Each data and how it relates

Can the builder tell from the data model each data the roles pass or hold, and how each relates to
the others?

Why: a data the roles pass is read by one role as another made it. A relation no figure draws is
made one way by the role that writes it and taken another way by the role that reads it.

### Q-5: Each component split for a reason

Is each role one that acts in a user story, and each data a thing a story passes or holds, each
split from the others by a responsibility of its own, or by a constraint the architecture names,
such as work run in parallel, a context kept apart, a stance of its own or what the platform allows?

Why: components cut by function or by stage of processing grow with each function, and scatter what
one thing knows among them; cut by the stories' roles and data, they come out fewer than the
functions or the stages. A split with no such reason adds a path for users to learn and builders to
keep right, and leaves one responsibility decided in two places.

### Q-6: Where the files of each component are kept

Can the builder find, from the directory structure, the one place that holds the code of each role
or the files of each data, and what it is made of?

Why: the builder makes and changes each component where its files are kept, and that place decides
who owns it. A component kept in no place is put where the builder guesses, and one kept in two is
made twice and drifts.

### Q-7: Where each component runs or is kept

Can whoever runs the product set it up and start it from the deployment, knowing where each role
runs, where each data is kept and what outside the product they depend on?

Why: where a role runs decides what it can reach and when a change to it reaches the user, where a
data is kept decides who can read it and whether it outlives a run, and what the product depends on
is where it breaks for the user first.

### Q-8: Each part checked as heavily as a failure would cost

Can the approver tell, for each part and for the user stories, how heavily it is checked, and weigh
that against what a failure of it would cost the user?

Why: a check costs the user time to build and to keep on every change, and a failure costs them what
the part breaks, such as data lost or a wrong result used unseen. A weight given every product alike
gives a small tool the checks of a large one. A ground such as "a checklist asks it" is one the
approver cannot weigh against their purpose. What the project's rules settle is linked, as it is
decided once for the project.

### Q-9: The decisions kept to the principles

Does each arrow, each line and each check keep the principles the opening names?

Why: a decision read alone looks right by its own reason. One that breaks a principle undoes what
the principle was there for, and shows only when the product fails at it.

### Q-10: Each line a decision the approval rests on

Is each line of the architecture a decision whose change would change what was approved?

Why: a behavior in one case, a count, a value, a data's fields or a list of what a part does step
by step is decided again where the part is built and drifts from it. Each finding made while
building would then change what was approved and send it back to be approved again.
