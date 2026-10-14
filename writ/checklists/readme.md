---
name: readme
version: 0.2.0
---

# README

A README is read by someone meeting a product for the first time. It lets them:

- decide from its first sentence or two what the product is, what they would gain from it and
  whether it is for them;
- tell why to choose it over the other ways they could do the same work;
- picture using it on their own work, from starting to the result;
- get from deciding to their first result with the README alone;
- tell where to go for more;
- tell on what terms they may use it.

What only the product's builders need, such as its design or how to contribute, is not for this
reader. Each item of `doc.md` also applies to a README, with deciding and getting to the first result
as its subject: the whole picture, the ideas given in full and the job of each part are judged by
that, and what lies beyond it goes in a page reached from Documentation, not in the README.

## Benefit

### B-1: What they gain

From the opening, can the reader tell what they gain from the product?

Why: the reader decides from the opening whether to read on; when it says how the product works
instead, the reader is left to work out what they gain, and often leaves first.

### B-2: Who it is for

From the opening, can the reader tell whether they are someone the product is for?

Why: a reader who cannot place themselves reads on to find out, or leaves a product that would have
served them.

### B-3: Why this one

Can the reader tell what the product gives them that doing the work by hand, or with another tool,
does not?

Why: what only this product gives is the reason to choose it; what every way gives, such as not
losing work, does not decide the choice, and placed first it hides what does.

### B-4: Using it on their own work

Can a reader of those the opening says the product is for picture using it on their own work, from
starting to the result, with what they do and what they get back?

Look for an example set on a piece of work of a kind the opening names, that goes from starting to
the result and shows what the product gives back.

Why: a reader who can picture it decides on what they will actually get; an example on work of
another kind, or one without what the product gives back, is read as someone else's story.

### B-5: Started from the README alone

Can a reader who has decided to use the product get to their first result with the README alone?

Look for what must be in place beforehand, how to install the product, and a first use the reader
can repeat by following the README.

Why: each place the reader has to look elsewhere is a place they may stop.

### B-6: Where to go for more

Can the reader tell where to find what the README leaves out, such as fuller use and what changed
in each version?

Why: a reader who wants what the README leaves out and cannot tell where it is goes without it, or
takes it from somewhere that may not hold for this product.

### B-7: Terms of use

Can the reader tell on what terms they may use the product?

Why: a reader who cannot tell whether they may use it, or on what terms, cannot decide to use it.

### B-8: What it is

From the opening, can the reader tell what the product is?

Why: a reader who cannot tell what kind of thing it is cannot weigh what it gives against what they
already use, and reads on only to find out.

### B-9: Why each requirement is needed

For each thing that must be in place beforehand, can the reader tell why it is needed, from
something the product does that uses it?

Look for, for each such thing, something the product does that uses it, named in the opening, in the
example or beside the thing under Requirements.

Why: a reader who cannot tell why a thing is needed doubts it and leaves it out, or gets it ready in
a way the product cannot use, and does not reach their first result.

## Usability

### U-1: Nothing to learn of the product's inside

Can the reader decide and start without learning the names of the product's inner parts, the cases
where it acts otherwise than the example shows, or the steps it takes inside?

Look for, in the opening, the example, Requirements and Installation: a name of a part inside the
product, a case where the product acts otherwise than the example shows, and a step the product
takes that the reader neither takes nor sees in what it gives back.

Why: each such name, case or step the reader must take in before going on is effort spent on what
they do not use, and one more thing to learn before they have decided.

### U-2: Getting ready their own way

For each thing that must be in place beforehand, can the reader get it ready in their own way, or
see that they already have it, because they are told what the thing is and not only one way of
getting it ready?

Why: one way of getting it ready, given alone, reads as the only way, and the reader follows its
steps even where they already have the thing or would get it ready another way.

### U-3: An opening only for deciding

Can the reader decide from the opening whether to read on without reading anything there beyond
what the product is, what they gain and whom it is for?

It cannot when the opening also gives why to choose the product, which belongs in its own section,
or how it works, which belongs in the example.

Why: the reader decides from the opening whether to read on; each reason or working met there is
read before they know whether the product is for them, and stands between them and what they decide
by.

## Format

### F-1: Shape

Does the README follow this template, headings included?

```markdown
# <Product name>

<What the product is, and what it gives whom, in one or two sentences>

## Example

<Using it on one piece of work, from starting to the result, with what the product gives back>

## Why <product name>

<What only this product gives, set against the other ways of doing the same work>

## Requirements

<Each thing that must be in place beforehand, beside something the product does that uses it where
the opening and the example name none>

## Installation

## Documentation

<Where fuller use and what changed in each version are written>

## License
```

- The opening has no heading, so it sits right under the name, where the reader looks first.
- The example comes before installation, so the reader sees using it before deciding to install it;
  repeated after installation, it is the first use.
- Why to choose it follows the example, so the reader weighs it against the use they have just
  seen.

Why: a reader looks for requirements, installation or the license under the headings READMEs
commonly give them, and finds each where they look only when every README puts it there.
