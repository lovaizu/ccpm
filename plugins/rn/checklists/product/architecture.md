# Architecture

An architecture is read by whoever builds or changes the product and by whoever approves it. From it
they grasp how the product is put together to give the experience its UX sets, and how each part and
each user story is checked. They build, change or approve the product by it.

An approval rests on the decisions whose change would change what was approved: the principles, the
parts, how they act on one another, where the code of each is kept, where each runs, and how heavily
each is checked. So the architecture holds those alone. How a part behaves in each case is decided
where the part is built: in its tests if it is code, and in its steps if an AI runs it. The parts
are drawn from the UX in layers. Its scenes rest on a few user stories, each one way the user uses
the product at its edge, such as a command they run. The stories are taken on by logical components,
and each component is split from the others by its responsibility, or by a constraint that splits
one responsibility. Each component is then made with a technology, chosen at this layer alone. Each
view answers a concern of its own (Kruchten, "The 4+1 View Model of Architecture", 1995): the
logical view what the product gives its users, the process view how it behaves as it runs, the
development view where its code is kept, and the physical view where it runs. A structure is drawn
by hand, as its placing and frames carry what the reader takes in at a glance; a sequence has one
layout, its order down the page, so Mermaid draws it from text. How heavily a part is checked
follows from what a failure of it would cost the user, which differs from product to product, so the
approver weighs it here. An architecture built on another links that one and writes only what is its
own.

## Format

```markdown
# <Product name> architecture

<How the product is put together, in a sentence or two, with a link to its UX>

<The principles it rests on: a link to those of what it is built on, and its own, each in a line>

## User stories

- As <the user>, I want <what they do with the product>.

## Architecture

### Logical view

<One SVG figure: a box for each logical component, holding its name alone, its shape saying whether
an AI or code does its work, with a legend, and a frame round the boxes that run in one place or
make one product; an arrow from each to the component it acts on, labelled in a few words with
what it does; the boxes placed so the arrows run in the order they act and cross none>

- <A choice the figure shows that the reader would question, with why>

### Process view

<For each user story, a Mermaid sequence diagram: a participant for each logical component the story
reaches, named as in the logical view, and a message for each step, labelled in a few words with
what is handed on>

- <A choice the diagrams show that the reader would question, with why>

### Development view

<One SVG figure: a box for each place code is kept, such as a folder, named by its path, holding the
logical components kept there by their names, each with what it is made of, such as `Python 3`>

### Physical view

<One SVG figure: a box for each machine or runtime the product runs in, such as the user's computer
or Claude Code, holding the logical components that run there by their names; a box for each thing
outside the product they depend on, with an arrow labelled with what is used>

- <How the product is started>

## Test

<A link to the project's rules for how each kind of part and the user stories are checked, where it
has them>

- <How heavily a part is checked beyond those rules, such as by property tests or mutation testing,
  or that it is checked by them alone, with what a failure of it would cost the user>
```

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

Can the reader follow each user story through the process view, from the first component it reaches
to its end, along the arrows of the logical view?

Why: components that each do their part achieve no story unless their interactions do. A component
found missing only when its story is built changes the architecture then, after the approval.

### Q-4: Each component split for a reason

Does each component take a responsibility of its own, or a part of another's for a constraint the
architecture names, such as work run in parallel, a context kept apart, a stance of its own or what
the platform allows?

Why: a split with no such reason adds a path for users to learn and builders to keep right, and
leaves one responsibility decided in two places.

### Q-5: Where the code of each component is kept

Can the builder find, for each component, the one place its code is kept and what it is made of?

Why: the builder makes and changes each component where its code is kept, and that place decides who
owns it. A component kept in no place is put where the builder guesses, and one kept in two is made
twice and drifts.

### Q-6: Where each component runs

Can whoever runs the product set it up and start it from the physical view, knowing where each
component runs and what outside the product it depends on?

Why: where a component runs decides what it can reach and when a change to it reaches the user, and
what the product depends on is where it breaks for the user first.

### Q-7: Each part checked as heavily as a failure would cost

Can the approver tell, for each part and for the user stories, how heavily it is checked, and weigh
that against what a failure of it would cost the user?

Why: a check costs the user time to build and to keep on every change, and a failure costs them what
the part breaks, such as data lost or a wrong result used unseen. A weight given every product alike
gives a small tool the checks of a large one. A ground such as "a checklist asks it" is one the
approver cannot weigh against their purpose. What the project's rules settle is linked, as it is
decided once for the project.

### Q-8: The decisions kept to the principles

Does each arrow, each line and each check keep the principles the opening names?

Why: a decision read alone looks right by its own reason. One that breaks a principle undoes what
the principle was there for, and shows only when the product fails at it.

### Q-9: Each line a decision the approval rests on

Is each line of the architecture a decision whose change would change what was approved?

Why: a behavior in one case, a count, a value or a list of what a part does step by step is decided
again where the part is built and drifts from it. Each finding made while building would then change
what was approved and send it back to be approved again.
