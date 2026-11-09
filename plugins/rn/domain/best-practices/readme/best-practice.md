# `readme`

## Goal

A newcomer decides from the README alone whether the product fits their work, and if it does, starts using it.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../README.md](../../../README.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The reader knows whether the product fits their work. |
| C2 | The reader trusts, before trying it, that the product delivers what it promises. |
| C3 | The reader installs the product and starts using it without help. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does the opening say what the product is, who it's for, and what it lets them achieve? | the opening |
| N2 | C1 | Does the README list what readers might expect the product to do but it doesn't? | Non-goals |
| N3 | C1 | Does the README say at the top where the product isn't ready for use yet? | the opening |
| N4 | C1 | Does the README name the license and link its full text? | License |
| N5 | C1 | Does the README answer each question in the order a reader comes to ask it? | the whole |
| N6 | C2 | Does the walkthrough show a real run that delivers, on typical work, the benefit the opening promises? | Walkthrough |
| N7 | C2 | Does the README show how the product removes the problem that brings readers to it? | How it works |
| N8 | C2 | Does the README show how the product achieves each key result that a newcomer would doubt? | How it works |
| N9 | C3 | Can a reader with nothing set up install the product by the README alone, and see that it works? | Requirements, Installation |
| N10 | C3 | Does the README link where to go for fuller use and for help? | Documentation |

## Practices

### N1

Does the opening say what the product is, who it's for, and what it lets them achieve?

**Thinking**

Most readers decide from the opening alone whether to read on, so it must let a newcomer tell within a few sentences whether the product is for them. Geoffrey Moore's positioning statement, from Crossing the Chasm, gives the decisions in order. First, the target: the people the product is for, named by the work they want done, narrowly enough that a reader outside the group can tell it isn't for them. Second, their need: what they can't do well today, in their words. Third, the category: a kind of thing the reader already knows, such as a command-line tool, which gives them something to compare it with. Fourth, the key benefit: what they achieve with the product, taken from the objectives of the product vision, as an end they reach, not a feature. Write the opening from these four, in words the reader already uses, and leave out feature names and internals.

**Steps**

1. Read only the opening, then put it away and explain the product as you would to a colleague. Shorten any part you forgot or got wrong, and replace each vague or praising word with what the product does.
2. Read the opening as someone outside the target. If they couldn't tell that the product isn't for them, name the target and their work more precisely.

### N2

Does the README list what readers might expect the product to do but it doesn't?

**Thinking**

A reader who needs something the product doesn't do should find out before they install it. Derive the expectations from the opening: its category and its key benefit lead a reader to expect certain things, such as undoing its changes from a tool that edits files. For each thing the opening leads a reader to expect, ask whether the product does it, and whether its absence would change the reader's decision. List only those that the product doesn't do and whose absence would. Where the product meets the need another way, say so in the same item. A design document lists its non-goals for the same reason: they mark the edge of the scope where readers would otherwise guess.

**Steps**

1. Ask the user about each expectation whose scope the product vision doesn't settle.

### N3

Does the README say at the top where the product isn't ready for use yet?

**Thinking**

A reader who builds on a product that isn't ready finds out only after their work depends on it. Decide the product's state by the states that [repostatus.org](https://www.repostatus.org) defines, such as Concept, Work in Progress, Active, and Unsupported. If the state is anything but Active, say it at the top, with what it means for the reader's work: what works now, and what they get if they install today. Check that a newcomer can say, after the opening, whether they can rely on the product today.

### N4

Does the README name the license and link its full text?

**Thinking**

Some readers rule a product in or out by its license alone, so they must find it at once and recognize it. Name the license by its identifier in the [Software Package Data Exchange (SPDX) License List](https://spdx.org/licenses/), which readers and their tools recognize, and link its full text. If the product includes work under other licenses, name each with its source.

**Steps**

1. Open the link and check that it leads to the license the README names.

### N5

Does the README answer each question in the order a reader comes to ask it?

**Thinking**

Readers come with questions in a typical order, and leave when the next answer isn't where they look. Decide the order by listing the readers and the question each has next. Every reader first asks what the product is and whether it's for them. A reader who has decided asks how to install it. A reader still deciding asks whether it really works, and how. A reader who has started asks where to learn more. Order the sections so that each answer comes just when its question does, and each reader can stop once they have what they came for. The [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts first what every reader needs, for the same reason.

**Steps**

1. Read the README from the top as a newcomer, and after each section, write down the question you have next. The trace: `{deliverable}` read to its end.
2. Check that the next section answers that question. Move any section that answers a later one.
3. Remove what no reader needs at that point, or move it to a linked document.

### N6

Does the walkthrough show a real run that delivers, on typical work, the benefit the opening promises?

**Thinking**

A reader trusts a benefit they've seen happen more than one they only read about. Decide three things in order. First, the use: the one that most readers come for, taken from the main use of the product vision's objectives. Second, the task: one like the reader's own work, small enough to show from start to end, and real enough that the benefit shows in its result. If the result wouldn't show the benefit the opening promises, choose another task. Third, the cut: show every exchange from what the reader gives to the result they keep, with the product's real output, and cut only what doesn't bear on the result. State the result first, so that the reader knows where the run goes. Diátaxis calls this a [tutorial](https://diataxis.fr/tutorials/): one concrete task, carried through to a visible result. Check that a newcomer can say, after reading, what the product would give them on their own work.

**Steps**

1. Choose the use from what readers ask for most and from the objectives of the product vision. The trace: `{inputs}` read to its end.
2. Take each exchange from the record of a real run, in the form the reader meets it.

### N7

Does the README show how the product removes the problem that brings readers to it?

**Thinking**

A reader chooses a product when they recognize their own problem and see it gone. Take the problem from the product vision. The first idea of its concept is what the product values most, set against the current way of working. The problem is where the current way fails the target reader on that idea, in the reader's words, such as reading and fixing an AI's drafts round after round. Decide the one point that the reader must take away: what the product changes so that the problem goes away. The other ideas of the concept serve that change, so show each only as a part of it. Then choose the form by what the point compares, as Gene Zelazny's Say It With Charts does: decide the message, then the comparison, then the form that shows it at a glance. A change in who does what, or in where a step happens, is a before-and-after comparison. Draw the current way and the product's way side by side, with the problem in the one and gone in the other. A point that one sentence makes clear needs no figure. Check that a newcomer can say back what the product changes for them.

**Steps**

1. Take the problem from the first idea of the product vision's concept and the current way it names. The trace: `{inputs}` read to its end.
2. Take from the design what the product changes. Ask the user where the design doesn't settle it.

### N8

Does the README show how the product achieves each key result that a newcomer would doubt?

**Thinking**

A reader tries a product once they believe it gives what it promises, and the product vision's key results say what it promises: how well and how fast the reader reaches the objective. A reader believes it once they can picture it happening. Don Norman calls this picture the conceptual model, in The Design of Everyday Things. Decide each answer in order. First, for each key result, write the reader's doubt in their words, such as: does what comes out work without fixes? Second, decide the one point that resolves it, in one sentence, such as: a second AI reads each piece as its users would, and rn builds it again until they get what they need. If you can't write the point in one sentence, you don't yet understand the design well enough to explain it. Third, decide what the point compares or what motion it shows, as Gene Zelazny's Say It With Charts does. Fourth, choose the form that shows it most directly. If the real thing can show it, such as a message from the walkthrough's example, show the real thing. A flow takes a figure, a comparison takes a table, and a point that one sentence makes clear takes the sentence. Check that a newcomer can say the point back after seeing the answer.

**Steps**

1. Take each key result from the product vision's objectives. The trace: `{inputs}` read to its end.
2. For each doubt, take how the product does it from the design. Ask the user about any that the design doesn't settle.

### N9

Can a reader with nothing set up install the product by the README alone, and see that it works?

**Thinking**

A reader who can't install the product never gets to use it, and the author's own setup hides what a newcomer lacks. Decide the steps by starting from a machine with nothing on it. List everything the product needs, each with a command whose output shows that the reader has it. Write each install step as a command the reader can copy. End with a sign the reader can see that the product works. A step that only works with something the README doesn't mention is missing a requirement. [Standard Readme](https://github.com/RichardLitt/standard-readme) holds these in its Install section.

**Steps**

1. On a machine or sandbox with nothing the product needs, follow the steps exactly as written. If a step fails or needs something the README doesn't mention, add it and start again.

### N10

Does the README link where to go for fuller use and for help?

**Thinking**

The README stays short only if each later need has its own place to go. Decide the links by listing what a reader needs after they start, such as fuller use, reference, help, and the changes in each version, and give one link for each, with whom it's for. Each need has its own kind of page, which [Diátaxis](https://diataxis.fr) sorts into tutorials, how-to guides, reference, and explanation. Check that each link opens the page it names.

**Steps**

1. Open each link.
