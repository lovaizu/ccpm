---
name: usability
version: 0.2.0
---

# Usability

A deliverable, a document or code, is used by a reader who comes to it for a purpose, with what
they have beside it; the reader may be a person or an AI. Reading it once from the top, they take
in what it holds in a short time, meeting nothing they do not need and left with no question, and
achieve that purpose. Below, a document is either, and each file of code is one of its parts.

Each item is answered by what the reader has and does with the deliverable alone, never by the
sources it was made from, which they do not have.

A deliverable is made usable by thinking through what the reader meets, in the order they read:

1. On opening it, they can tell whether it serves their purpose.
2. Reading on from the top, they understand each word and idea where they meet it.
3. They stop at nothing they do not need.
4. When they finish, no question is left, and they achieve their purpose.

## Format

### F-1: Shape

Scope: whole

Does the document follow this shape, inside the template its own kind gives?

```markdown
# <Title>

<The main point: what the reader can do with the document>

## <A section, in the order the reader needs it>

<The section's main point first>

- <An item said in one sentence that is understood alone>

  <Its explanation, after a blank line, indented under the item>
```

No item is set in bold, and an item that needs no explanation is the one sentence alone.

Why: the reader sees on opening it whether the document serves their purpose, reads the sections in
the order they need them, and skims the items alone, reading an explanation only where they need it;
bold marks where to stop, and on every item it marks nothing out.

## Benefit

### B-9: Whether it serves their purpose

Scope: its part

On opening the document, can the reader tell whether it serves their purpose?

Look for: the main point right under the title.

Why: a reader who cannot tell reads on to find out, or leaves a document that would have served
them; one who can reads each part knowing what it supports.

### B-12: Every term known

Scope: each part

Can the reader tell what each term means where they meet it, because they already know it or the
place where it is first used, a sentence, an example or a figure, shows what it means?

A term is any word the document uses for a thing of its subject, whether set in code or not.

Look for: a plain word used in a sense of its own, such as a word for a part of the subject or for
someone who acts in it, that no sentence explains; a name or an example taken from another product
beside it, such as another plugin of the same marketplace, which the reader may not know.

Why: a term never explained is read with a guess at its meaning, and the reader's picture differs
from the writer's where the guess is wrong.

### B-13: One name for each thing

Scope: whole

Does the reader meet each thing under one name from start to end?

Why: a reader takes a second name for a second thing.

### B-14: One meaning for each name

Scope: whole

Does each name keep one meaning for the reader from start to end?

Why: a name whose meaning shifts carries its first meaning into the place where it has changed.

### B-11: Read once from the top

Scope: each part

Can the reader read each sentence without going back or ahead, because each word, reason and step
it rests on comes before it?

Look for: a decision whose reason comes later or elsewhere; a link or a pointer that sends the reader
ahead for what a sentence rests on.

Why: each of these stops the reader, sends them back or ahead, or lets them read on with a wrong
guess, so the picture is not taken in by one reading from the top.

### B-16: Who does what, at a glance

Scope: its part

Where the document tells of several that act in turn, can the reader see who does what, what passes
between them and in what order at a glance, instead of piecing it together from sentences spread
through the document?

For a reader who is a person, that is one figure, with the text beside it saying only what the
figure cannot show; for an AI reading a prompt, it is the steps. A document that tells of no such
thing passes.

In a figure whose boxes are of different kinds, each box holds its name, with its kind beside it
as one short word in angle brackets, such as `turn:up <agent>`.

Why: pieced together in the head, it costs effort and goes wrong; a figure shows a person at once
what rows of a table make them assemble, while an AI reads a figure as text, in order; a box that
holds a description buries the name the text calls it by.

### B-20: The form that fits

Scope: each part

Is each thing shown in the form its reader takes in most easily for that thing, such as a directory
tree for where files are placed, a table for values set side by side, a figure for who acts on whom,
and sentences for a reason?

Why: a thing put in a form that does not fit it, such as files drawn as boxes, makes the reader
turn it back into the shape they know before they can use it.

### B-4: Every part used

Scope: each part

Does the reader use each part toward the purpose they came for, without skipping it or reading again
what they already took in?

Look for: a part meant for someone other than the reader, such as a reviewer; an opening or a
section that tells what the document is or does in place of telling the subject; terms gathered
ahead of the content; the history of how a decision was reached; a comparison or an example for an
idea the reader already holds.

Why: a part the reader skips or reads twice costs effort beyond the subject, and buries the parts
they need.

### B-19: As short as the subject allows

Scope: each part

Does each word the reader reads give them something they would lose without it?

Why: every word beyond what the subject asks is effort spent on how the document is written instead
of on the subject.

### B-3: Each idea taken in whole

Scope: whole

Can the reader take in each idea the document takes up whole, without guessing any part of it?

Why: an idea touched on in part is completed by a guess, and a gap covered by smooth sentences is
acted on without the reader noticing.

### B-6: Still true later

Scope: each part

Can the reader rely on what the document says for as long as the subject's purpose and decisions
stand?

What stays true is the purpose, the decisions and their reasons; steps, status and how the work went
change with each piece of work.

Why: a document that has turned wrong is worse than none, since it is believed.

### B-7: Said in one place

Scope: whole

Can the reader take each thing the document says as the one account of it, because it is said in
one place, with every case where it does not hold beside it, and not also in another place of the
document?

Look for: a part that says again, in other words or in a figure, what another part says.

Why: two places that say one thing come to disagree as one of them changes, and the reader cannot
tell which holds; once the reader skims a run of repeats, they skim the one new point among them
too; a rule read apart from the case where it does not hold is followed there too.
