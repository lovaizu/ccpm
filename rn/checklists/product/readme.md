---
name: readme
version: 1
made_from:
  checklist: 1
  usability: 1
---

# README

A README is read by someone meeting the product for the first time, with only what a newcomer has.
From it alone they decide whether the product is for them, and if it is, get to their first result
with it. Someone joining those who build it reaches the architecture and development documents from
it.

A README tells a newcomer what the product's UX holds for them before anything they must do: the
idea the product rests on, what it does that gives its benefits where other ways of doing the same
work do not; whom it is for and what they gain, from the UX's users, goals and benefits; one of the
UX's scenes as the example, the one account of using the product from starting to the result; and
what the benefits give that doing the work by hand or with another tool does not. What follows
takes a reader who has decided from there to their first result, each step one they can follow with
what they have and each statement one they find holds when they try it. What lies beyond the first
result, such as fuller use, goes in a page reached from Documentation.

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

- <Each thing that must be in place beforehand, said as what it is>

  <Why it is needed, where the reader would not know>

## Installation

<How to install, then the first use, as in the example>

## Documentation

<Where fuller use and what changed in each version are written>

## Development

<A link to the entrance to the architecture and development>

## License
```

Each section opens with its main point. A list item is one sentence understood alone, with its
explanation, where it needs one, after a blank line and indented under it; no item is set in bold.

Why: a reader looks for requirements, installation or the license under the headings READMEs
commonly give them, and finds each where they look only when every README puts it there; the
opening sits right under the name, where the reader looks first, and begins with the idea, as it is
what sets the product apart; the example comes before installation, so the reader sees using it
before deciding to install it; why to choose it follows the example, so the reader weighs it against
the use they have just seen; and the way on for those who build it stands apart from Documentation,
so a user does not read through links they do not use. The reader skims the items alone and reads
an explanation only where they need it; bold on every item marks nothing out.

## Benefit

### B-1: Whether it is for them

Scope: its part

From the opening, can the reader tell whether the product is for them?

Look for:
- a first sentence that says what the product does, but not the idea by which it gives what other
  ways of doing the same work do not;
- what the reader gains said without the kind of thing that gives it, such as a tool run from their
  editor, or replaced by how the product works;
- whom it is for left for the reader to work out.

Why: the reader decides from the opening whether to read on; one shown only what the product does
takes it for any tool that does the same, and one who cannot place themselves leaves a product that
would have served them.

### B-2: Using it on their own work

Scope: its part

From the example, can the reader picture using the product on their own work, from starting to the
result, with what they do and what they get back?

Look for:
- work of another kind than the reader's, or an example that stops before the result;
- what the product gives back described instead of shown;
- where several act in turn, such as the reader, the product and its agents, who does what and what
  passes between them not told in the order it happens.

Why: a reader who can picture it decides on what they will actually get; an example on work of
another kind, or one without what the product gives back, is read as someone else's story.

### B-3: Why this one

Scope: its part

From Why, can the reader tell what the product gives them that doing the work by hand, or with
another tool, does not?

Look for: a benefit every way of doing the work gives, such as not losing work, set among or before
those only this product gives.

Why: what only this product gives is the reason to choose it; what every way gives does not decide
the choice, and placed first it hides what does.

### B-4: The first result from the README alone

Scope: its part

Can a reader who has decided, with only what a newcomer has, get ready what must be in place,
install the product and get the example's result themselves, following the README alone?

Look for:
- a thing that must be in place given only as one way of getting it ready, so a reader who already
  has it, or would get it ready another way, cannot tell;
- a step, a file or a fact the reader must find elsewhere or guess;
- a command, a link or an address that fails when the reader uses it as written, such as a download
  address that gives 404, or one that works only from a copy the newcomer does not have yet;
- the example, run as written, giving other output than the README shows.

Why: each place the reader must look elsewhere, or a step fails, is a place they may stop; whoever
wrote the README has the product at hand and never meets it.

### B-5: Each way on reached

Scope: its part

From Documentation, Development and License, can the reader reach each place the README sends them
on to?

Look for:
- fuller use or what changed in each version with no place named;
- no entrance for those who build the product, or one set among Documentation's links;
- the license not named in the README itself;
- a place named that the reader cannot reach, with no link, or a link to what is not there for them,
  such as "the commit history" with no address, or of a repository with nothing yet committed.

Why: a README that holds only what a newcomer needs stays short only when the rest is somewhere the
reader can reach; one who cannot find the architecture changes the product without the decisions
behind it, and one who cannot tell the terms of use cannot decide to use it.

### B-6: Each part taken in on one reading

Scope: each part

Can the reader take in each part reading it once from the top, without going back or ahead and
without guessing?

Look for:
- a term the reader may not know, such as a plain word used in a sense of its own or a name taken
  from another product, that no sentence, example or figure shows where it is first used;
- a sentence resting on a word, a reason or a step that comes later, or on a link the reader must
  follow first;
- an idea given in part, such as a case named without what happens in it;
- a thing in a form that does not fit it, such as a command set in a sentence rather than in a block
  to copy, or values side by side not in a table.

Why: a reader stopped goes back or ahead, or reads on with a guess, and acts on a picture of the
product that differs from the product where the guess is wrong.

### B-7: Each sentence needed, once

Scope: whole

Does each sentence give the reader something toward deciding or their first result that no other
sentence of the README gives them?

Look for:
- a thing said again in other words in another part, such as the opening's gain again in Why, the
  example's steps again in Installation, or a figure telling what the example tells;
- a part meant for someone other than the reader, such as a reviewer, or one telling what the README
  is or does in place of the product;
- the history of how a decision was reached;
- fuller use, which belongs in the page Documentation reaches;
- a comparison or an example for an idea the reader already holds, or words that give nothing.

Why: a reader who has skimmed a run of repeats skims the one new point among them too, and two
places that say one thing come to disagree as one of them changes; each part beyond the subject
buries those the reader needs.

### B-8: Every statement holds

Scope: whole

Can the reader rely on every statement of the README at once, each true of the product as they find
it when they run it?

Look for:
- two statements that cannot both hold, found by setting each promise of the opening and Why beside
  the later lines and what the product does, such as an opening promising nothing else changes and
  a later line naming a change it makes to every input;
- a promise wider or narrower than what the product does when the reader runs it;
- one thing under two names, or one name for two things;
- a statement that turns untrue as the work goes on, such as "not yet" or "for now".

Why: the reader cannot tell which of two statements holds, and following one breaks the other; a
README that has turned wrong is worse than none, since it is believed.
