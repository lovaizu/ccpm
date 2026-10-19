---
name: checklist
check: usability
version: 0.2.0
---

# Checklist

A checklist is used by whoever makes a deliverable of one kind and whoever judges it. Answering its
items as they make it, the maker makes a deliverable that serves the kind's purpose, nothing missing
and nothing more; answering its items, the judge can tell whether a deliverable serves that purpose.

A checklist is worked out in this order, each step the ground of the next:

1. Decide its purpose: who uses a deliverable of the kind, and what they can then do, in one or two
   sentences.
2. From the purpose, decide the order in which whoever makes the kind decides it; for how readable
   a document is, the order follows what its reader meets as they read.
3. From that order, decide the template of what every deliverable of the kind holds, tied to no
   language or tool.
4. From the opening, its purpose and its order, draw the key points alone as items, each asking one
   thing; what the steps already bring about is not asked again.
5. Split the items by what answers them: what the deliverable's user has and does with it, or the
   sources it was made from, each in a checklist of its own.

This file is the checklist for checklists, and is written in the shape it asks for. Each item of
`usability.md` applies to a checklist, with what a good deliverable of the kind gives its user as
its subject.

## Format

### F-1: Shape

Scope: whole

Does the checklist follow this template?

```markdown
---
name: <kind-of-deliverable, or what it judges across kinds>
check: <usability or accuracy>
version: <x.y.z>
---

# <Kind of deliverable, or what it judges across kinds>

<The purpose in one or two sentences: who uses it, and what they can then do>

<The order the kind is worked out in, as numbered steps>

<How `usability.md` applies to the kind>

## Format

### F-1: Shape

<The template the deliverable follows>

## Benefit

### B-1: <Item name>

Scope: <its part, each part or whole>

<Question answered yes or no>

<Only what the question needs to be answered, such as a list or a template; most need nothing>

Why: <what goes wrong without it>
```

Each item, Format's included, says where in the deliverable it is answered: `its part`, at the part
or parts that give it; `each part`, in every part of the deliverable on its own, a part being a
section under a top heading of a document, with the title and opening as one, or a file of code;
`whole`, of the deliverable at once, for what lies between its parts, such as one name for each
thing.

`check` says what answers every item: `usability`, what the deliverable's user has and does with
it, such as the whole repository and running its tests for whoever maintains code; `accuracy`, the
sources it was made from, which that user does not have. A checklist for one kind is named by the
kind and is `usability`; one that judges every kind, such as `usability.md` and `accuracy.md`, is
named by what it judges. One that adds no part to its kinds' templates has no Format section.

Why: every checklist in the same shape keeps their quality even, lets a tool read any of them, and
gives the maker the purpose, then the order, then the shape, before the items, so each item is met
inside what those already set. An item asking of every part, answered where one part gives it,
passes a part that does not, and one asking what lies between the parts cannot be answered part by
part.

### F-3: Version

Scope: its part

Is the `version` in the front matter semver?

Why: a judgment names the text it was made by in a form people and tools read the same way.

### F-4: Item IDs

Scope: whole

Is each item's ID its section's first letter and a number counted up within the section, such as
`B-2`?

Across checklists, an ID is named with the checklist's `name`, such as `release-notes B-2`.

Why: a judgment names each item by its ID, and the name tells whose item it is when several
checklists are judged at once.

### F-5: An ID never used again

Scope: whole

Compared with the version last released, is every ID that a removed or moved item had left unused,
with a moved item taking a new number in its new section?

The version last released is the one in the last release of the plugin that holds the checklist,
under whatever name it had then. A checklist in no release yet has no such ID, and passes.

Why: an ID named earlier always means the same item.

### F-6: Version raised once for each release

Scope: its part

Is the `version` raised once for each release from the version last released, and not with each
change on a branch?

A checklist in no release yet is `0.1.0`.

Why: a judgment names the text it was made by, and no draft between releases takes a number.

## Benefit

### B-1: User and purpose

Scope: its part

Can whoever makes or judges a deliverable of the kind learn, from the opening, in one or two
sentences, who uses it and what they can then do?

Why: every item is judged against the user and the purpose; without them, no item can be answered.

### B-9: The order the maker decides in

Scope: its part

Can whoever makes a deliverable of the kind take its decisions in the order the opening gives,
each step drawn from the purpose and the ground of the next?

Why: a maker who decides in an order of their own decides a later thing before what it rests on,
and the deliverable is then fitted to a guess.

### B-10: A template drawn from the order

Scope: its part

Can whoever makes a deliverable of the kind fill the template with what every deliverable of the
kind holds, each part drawn from a step of the order?

Look for: a part only some deliverables need; a part from no step; a form of one language or tool.

Why: a part only some need is added to every deliverable, and a part from no step is filled with
nothing the purpose asks.

### B-7: How `usability.md` applies

Scope: its part

Can whoever makes or judges a deliverable of the kind tell from the opening how each item of
`usability.md` applies to the kind?

Look for: what the kind's subject is, for the items that ask about the reader's picture of it; and,
for each item of `usability.md` that the kind's shape settles otherwise, such as an opening its
template has no place for, how it is answered for the kind. An item not named is answered as
`usability.md` asks it.

Why: `usability.md` is answered beside the kind's checklist; an item of it that the kind's shape
cannot meet, or that is answered on a subject wider than the kind's, fails a deliverable that serves
its reader, and the maker cannot tell what passes.

### B-2: Every part of the purpose checked

Scope: whole

For each thing the opening says the user decides or does, can whoever judges learn from some item
whether the user can?

Why: items drawn from the purpose, one for each thing it names, are enough when every thing has
one; a thing with no item lets a deliverable that misses that part of the purpose pass.

### B-3: What the user gets

Scope: whole

Does a yes to each item tell whoever judges that the user gets something from the deliverable,
rather than that something is in it?

Look for: an item met by writing something in, such as an opening that tells what the deliverable
covers, whether its user needs it or not; and an item that asks of every deliverable of the kind a
part only some need, such as a figure of who does what where nothing acts in turn.

Why: an item about what is there passes a deliverable its user cannot use, and fails a good one that
does without that part; and since the maker meets every item, what such an item asks for is added
to every deliverable of the kind, needed or not.

### B-11: The key points alone

Scope: whole

Does each item ask something that following the order alone may still leave unmet?

Look for: an item whose yes follows from having taken a step, such as a test seen failing where the
order has each test written and seen failing first.

Why: an item that asks again what a step brings about is one more to answer for nothing, and the
items that matter are lost among them.

### B-4: One thing per item

Scope: whole

Can whoever judges tell, from each item answered no, the one thing that falls short?

An item that checks two things does not.

Why: when an item checks two things, the one that falls short hides behind the one that holds.

### B-5: Answered yes or no

Scope: whole

Can whoever judges answer each item yes or no?

Why: an answer that is neither leaves the deliverable neither passed nor failed, so no one can tell
whether it serves its purpose.

### B-6: Same answer from anyone

Scope: whole

Can the maker know what passes, because each item gets the same answer whoever answers it?

A question that holds a word whose bar depends on who answers, such as concrete, clear, enough or
appropriate, does not; nor does one that counts in a unit it does not say, such as one change or
one idea. Such a word is replaced by what is looked at to answer yes, and such a count by what
counts as one.

Why: when the answer depends on who judges, the maker cannot tell what passes, and judgments of the
same deliverable differ.

### B-8: Each item named by what it gives

Scope: whole

Can whoever makes the deliverable tell from each item's name alone what the user gets when the item
is met?

Look for: a name that says what is absent or kept out, such as "Nothing of the specification" or
"No case a principle settles"; it fails.

Why: an item is named alone in a judgment and in the maker's mind; a name of what is kept out is
read as a rule, and the maker writes to avoid it rather than to give the user something.

### B-13: Each item answered by what its `check` says

Scope: whole

Can each item be answered by what the checklist's `check` says answers it: in a `usability`
checklist, by one who has only what the deliverable's user has and does what they do with it; in an
`accuracy` one, by one holding the sources?

Look for: in a `usability` checklist, an item that asks whether the deliverable matches what was
decided or how the product behaves where the user cannot run it.

Why: an item given to one who cannot answer it is left without an answer, or answered by one who
holds what the user does not, so a deliverable the user cannot use passes.

### B-12: Items in the order the maker meets them

Scope: whole

Can the maker take the items in the order they work, because the items stand in the order of the
steps they are drawn from, and those that hold over the whole, such as one name for each thing,
stand last?

Why: a maker who works through the steps meets each item where its part comes, instead of holding
every item in mind at once; and an item that holds over the whole is checked once the whole is
there.
