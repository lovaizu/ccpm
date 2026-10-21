---
name: readme
version: 0.2.0
---

# README

A README is read by someone meeting the product for the first time. From it alone they decide
whether the product is for them, and if it is, get to their first result with it. Someone joining
those who build it reaches the design and development documents from it. A README is made in two
stages: from the UX before the product is designed, so that it is built to what the README promises,
and from the design and what is in the repository once the product is built.

Before the design, from the UX:

1. From the UX's benefits, say in one sentence the idea the product rests on: what it does that
   gives its benefits, where other ways of doing the same work do not.
2. From the UX's users and goals, and its benefits, say in one or two sentences whom the product is
   for and what they gain.
3. Choose one of the UX's scenes and show it as an example, from start to result, with what the
   user does and what they get back.
4. From the UX's benefits, take what doing the work by hand or with another tool does not give, as
   why to choose this one.

Once built, from the design and the repository:

5. Write what the reader needs to repeat the example themselves: what must be in place beforehand,
   and installing.
6. Link the documents the reader goes on to: for users, fuller use and what changed in each
   version; for those who build it, the entrance to the design and development.
7. Write the terms on which the product may be used, the license.

Each item of `usability.md` applies to a README with deciding and getting to the first result as
its subject; what lies beyond it, such as fuller use, goes in a page reached from Documentation.
`usability.md`'s B-16 is answered by the example, which shows the reader using the product from
start to result; a README holds no figure of who does what, since it would say the example again.

## Format

### F-1: Shape

Scope: whole

Does the README follow this template, headings included?

```markdown
# <Product name>

<The idea the product rests on, in one sentence; then what the reader gains, with the kind of
thing that gives it, and whom it is for, in one or two sentences; under no heading>

## Example

<Using it on one piece of work, from starting to the result, with what the product gives back>

## Why <product name>

<What only this product gives, set against the other ways of doing the same work>

## Requirements

<Each thing that must be in place beforehand, said as what it is>

## Installation

<How to install, then the first use, as in the example>

## Documentation

<Where fuller use and what changed in each version are written>

## Development

<A link to the entrance to the design and development>

## License
```

Why: a reader looks for requirements, installation or the license under the headings READMEs
commonly give them, and finds each where they look only when every README puts it there; the
opening sits right under the name, where the reader looks first, and begins with the idea, as it is
what sets the product apart; the example comes before
installation, so the reader sees using it before deciding to install it; and why to choose it
follows the example, so the reader weighs it against the use they have just seen; and the way on for
those who build it stands apart from Documentation, so a user does not read through links they do
not use.

## Benefit

### B-9: The idea it rests on

Scope: its part

From the opening's first sentence, can the reader tell the idea the product rests on, what it does
that gives what it gives, where other ways of doing the same work do not?

Why: the idea is what sets the product apart; a reader shown only what it does takes it for any
tool that does the same, and reads the example and why to choose it without the thread that joins
them.

### B-2: Who it is for

Scope: its part

From the opening, can the reader tell whether they are someone the product is for?

Why: a reader who cannot place themselves reads on to find out, or leaves a product that would have
served them.

### B-1: What they gain

Scope: its part

From the opening, can the reader tell what they gain from the product, said with the kind of thing
that gives it, such as a tool run from their editor?

Why: the reader decides from the opening whether to read on, and weighs what they gain against what
they already use, which takes the kind of thing; when the opening says how the product works
instead, the reader is left to work out what they gain, and often leaves first.

### B-4: Using it on their own work

Scope: its part

From the example, can the reader picture using the product on their own work, from starting to the
result, with what they do and what they get back?

Why: a reader who can picture it decides on what they will actually get; an example on work of
another kind, or one without what the product gives back, is read as someone else's story.

### B-3: Why this one

Scope: its part

Can the reader tell what the product gives them that doing the work by hand, or with another tool,
does not?

Why: what only this product gives is the reason to choose it; what every way gives, such as not
losing work, does not decide the choice, and placed first it hides what does.

### B-5: Started from the README alone

Scope: whole

Can a reader who has decided to use the product get what must be in place beforehand, install it,
and repeat the example themselves, with the README alone?

Why: each place the reader has to look elsewhere is a place they may stop.

### B-8: Getting ready their own way

Scope: its part

For each thing that must be in place beforehand, can the reader get it ready in their own way, or
see that they already have it, because they are told what the thing is and not only one way of
getting it ready?

Why: one way of getting it ready, given alone, reads as the only way, and the reader follows its
steps even where they already have the thing or would get it ready another way.

### B-6: Where to go next

Scope: its part

Can the reader find where to go next: a user, fuller use and what changed in each version; someone
joining those who build it, the entrance to the design and development?

Why: a README that holds only what a newcomer needs stays short only when the rest has somewhere the
reader can reach.

### B-7: Terms of use

Scope: its part

Can the reader tell on what terms they may use the product?

Why: a reader who cannot tell whether they may use it, or on what terms, cannot decide to use it.
