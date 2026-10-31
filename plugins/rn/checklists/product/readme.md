# README

A README is read by someone meeting the product for the first time, with only what a newcomer has.
From it alone they decide whether the product is for them, and if it is, they get to their first
result with it. Someone joining those who build the product finds the way to its architecture and
development documents from it.

A README follows the order in which its reader explains the product to their team or their
manager: what it is, the problem that makes it needed, what becomes possible with it, the idea that
makes that possible, and what it does not do. The opening carries all of these, drawn from the
users, goals and benefits of the product's UX. A reader who has decided by then goes straight to
Requirements and Installation, so these come right after the opening. The Walkthrough shows one of
the UX's scenes on real work, and How it works shows what the product is made of. Who does what in
which order is told by the UX's scenes alone, so both link to them. What lies beyond the first
result, such as fuller use, goes in a page that Documentation names. The headings are those READMEs
commonly give, so the reader finds requirements, installation or the license where they look for
them.

The README says an aim as what becomes possible, not as a burden reduced. It says whom the product
is for as what they gain, not as their situation. A sentence true only for some versions names the
version it is about, as doc.md's "Still true later" asks. The format holds no notice to the readers
of one version, such as an evaluation release; the README holds one where it is needed, as the
meta-checklist keeps a part beyond the format that its user uses.

## Format

```markdown
# <Product name>

<One sentence, "<Name> is a <kind> that <does what>", that a user could give their manager or a
colleague who asks what it is>

<The problem: why the product is needed>

<The aim: what becomes possible with it>

<The idea that achieves the aim, said concretely; each key term named first, then defined briefly>

**Non-goals**

- <What the product does not do, or an answer to a concern the reader is likely to have, in one
  sentence>

## Requirements

- <Each thing that must be in place beforehand, said as what it is>

  <Why it is needed, where the reader would not know>

## Installation

<How to install, and how the reader sees that it is installed>

## Walkthrough

<One of the UX's scenes, on real work, from start to the result, shown with the real output the
reader sees; a link to the UX's scenes for who does what in which order>

## How it works

<An SVG figure, with the few words it needs, of what the product is made of and how it keeps the
opening's promise; a link to the UX's scenes for who does what in which order>

## Documentation

<Where fuller use and what changed in each version are written>

## Development

<A link to the entrance to the architecture and development documents>

## License
```

The opening stands under no heading. Non-goals is a bold label, not a heading, so it stays part of
the opening.

## Questions

### Q-1: Whether the product is for them

From the opening, can the reader tell whether the product is for them?

Why: the reader decides from the opening whether to read on. One shown only what the product does
takes it for any tool that does the same, so the opening gives the idea that sets it apart. One who
cannot place themselves among those it is for leaves a product that would have served them.

### Q-2: Said as what the reader gains

Does the opening say the aim as what becomes possible, and whom the product is for as what they
gain?

Why: a reader weighs a product by what it lets them do. An aim said as a burden reduced reads as
any tool's promise, and those it is for said by their situation leave a reader in another situation
unable to tell that they gain too.

### Q-3: Using it on their own work

From the Walkthrough, can the reader picture using the product on their own work, from starting to
the result?

Why: a reader who can picture it decides on what they will actually get. A Walkthrough on work of
another kind, or one without the real output the reader gets, is read as someone else's story.

### Q-4: The first result from the README alone

Can a newcomer, with only what a newcomer has, get ready what must be in place, install the product
and get the Walkthrough's result, by following the README alone?

Why: each place where the reader must look elsewhere, or where a step fails, is a place they may
stop. Whoever wrote the README has the product at hand and never meets it. A requirement said as
what it is lets a reader who already has it, or would get it another way, tell so.

### Q-5: What the product is made of

From How it works, can the reader tell what the product is made of and how that keeps the opening's
promise?

Why: a reader shown only the promise takes it on trust, and cannot tell whether it holds for their
own work. The reader explains the product to their team by what it is made of, too.

### Q-6: Each way on reached

Can the reader reach each place that Documentation, Development and License send them to?

Why: a README stays short only when the rest is somewhere the reader can reach. One who cannot find
the architecture changes the product without the decisions behind it, and one who cannot tell the
terms of use cannot decide to use it.

### Q-7: Each promise kept by the product

Does the product, when the reader runs it, do what each promise of the opening says, as widely as
it says?

Why: a promise wider than what the product does is found out by the reader at their first use, and
a README that has turned out wrong is worse than none, as it was believed.
