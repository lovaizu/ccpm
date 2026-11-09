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
| N2 | C1 | Does the README list what readers might expect the product to do but it doesn't? | the opening |
| N3 | C1 | Does the README say at the top where the product isn't ready for use yet? | the opening |
| N4 | C1 | Does the README name the license and link its full text? | License |
| N5 | C1 | Does the README answer each question in the order a reader comes to ask it? | the whole |
| N6 | C2 | Does the walkthrough show a real run that delivers, on typical work, the gain the opening promises? | Walkthrough |
| N7 | C2 | Does the README show, for each problem readers have today, how the product removes it? | How it works |
| N8 | C2 | Does the README show how the product does each thing a newcomer would doubt it can do? | How it works |
| N9 | C3 | Can a reader with nothing set up install the product by the README alone, and see that it works? | Requirements, Installation |
| N10 | C3 | Does the README link where to go for fuller use and for help? | Documentation |

## Practices

### N1

Does the opening say what the product is, who it's for, and what it lets them achieve?

**Thinking**

The opening names the kind of product, the people it's for by the work they want done, and what they achieve with it, taken from the objectives of the product vision. It uses words the reader already knows, and leaves out feature names and internals. Most readers decide from the opening alone whether to read on. Geoffrey Moore's positioning statement, from Crossing the Chasm, gives the form: the target customer, their need, the product category, and the key benefit.

**Steps**

1. Read only the opening, then put it away and explain the product as you would to a colleague. Shorten any part you forgot or got wrong, and replace each vague or praising word with what the product does.
2. If a reader outside the target group couldn't tell that the product isn't for them, describe the group and their work more precisely.

### N2

Does the README list what readers might expect the product to do but it doesn't?

**Thinking**

List each thing a reader could reasonably expect the product to do that it doesn't. A reader who needs one of them learns it before installing. A design document states the same in its non-goals: what lies outside its scope.

**Steps**

1. Collect what readers expect from similar products and what they ask about, and ask the user whether each is in scope.

### N3

Does the README say at the top where the product isn't ready for use yet?

**Thinking**

If the product isn't ready for use, such as a release still in development or one no longer maintained, say so at the top, with what that means for the reader's work. Otherwise a reader finds out only after their work depends on it. [repostatus.org](https://www.repostatus.org) defines the common states of a project, such as Work in Progress, Suspended, and Unsupported.

### N4

Does the README name the license and link its full text?

**Thinking**

Name the license by its identifier in the [Software Package Data Exchange (SPDX) License List](https://spdx.org/licenses/), and link its full text. Some readers rule a product in or out by its license alone, and the identifier lets them and their tools recognize it at once.

**Steps**

1. Open the link and check that it leads to the license the README names.

### N5

Does the README answer each question in the order a reader comes to ask it?

**Thinking**

Order the README by who needs what: the opening for every reader, the installation for readers who have decided, the walkthrough and How it works for readers still deciding, and links for everything after. Each reader can stop once they have what they came for. A reader who has to read past what they don't need often leaves before reaching what they do. The [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts first what every reader needs.

**Steps**

1. Read the README from the top as a newcomer, and after each section, write down the question you have next. The trace: `{deliverable}` read to its end.
2. Check that the next section answers that question. Move any section that answers a later one.
3. Remove what no reader needs at that point, or move it to a linked document.

### N6

Does the walkthrough show a real run that delivers, on typical work, the gain the opening promises?

**Thinking**

Show one real run of the use that most readers come for, on work like theirs, from what the reader gives the product to the result they keep, with the product's real output. This shows the reader the promised gain happening, not only a claim of it. Diátaxis calls this a [tutorial](https://diataxis.fr/tutorials/): one task, carried through to a result.

**Steps**

1. Choose the use from what readers ask for most and from the objectives of the product vision. The trace: `{inputs}` read to its end.
2. Take each exchange from the record of a real run, in the form the reader meets it, and cut only what the reader doesn't need to see the result.
3. If the result doesn't show the gain the opening promises, choose another piece of work or another use.

### N7

Does the README show, for each problem readers have today, how the product removes it?

**Thinking**

For each problem readers have with their current way of working, described in their words, draw a figure that shows the problem in the current way and gone with the product. Add a sentence or two on what the product does to remove it. Readers choose a product once they can picture their own problem gone. In Alexander Osterwalder's Value Proposition Canvas, these are the customer's pains and the product's pain relievers.

**Steps**

1. Take the problems from the Concept section of the product vision, one for each idea where the current way falls short, and from what readers complain about in the current way. The trace: `{inputs}` read to its end.
2. For each problem, take from the design what the product does to remove it. Ask the user about any that the design doesn't settle.
3. Look at each figure as a newcomer. If they couldn't picture from it what its text says, redraw it.

### N8

Does the README show how the product does each thing a newcomer would doubt it can do?

**Thinking**

For each thing a newcomer would doubt the product can do, draw a figure of its own that shows how, and add a sentence or two. Readers believe a product can do something once they can picture how it works. Don Norman calls this picture the conceptual model, in The Design of Everyday Things. One figure for each doubt lets the reader take in each at a glance.

**Steps**

1. Read the README as a newcomer, and mark each claim that the current way can't match. For each answer, ask what the newcomer would doubt next, until no doubt remains. The trace: `{deliverable}` read to its end.
2. For each doubt, take how the product does it from the design. Ask the user about any that the design doesn't settle.
3. Look at each figure as a newcomer. If they couldn't picture from it what its text says, redraw it.

### N9

Can a reader with nothing set up install the product by the README alone, and see that it works?

**Thinking**

Write the requirements and the installation steps for a reader with nothing set up, each as a command they can copy, and end with a sign that the product works. The author's own setup hides the gaps. [Standard Readme](https://github.com/RichardLitt/standard-readme) holds these in its Install section.

**Steps**

1. On a machine or sandbox with nothing the product needs, follow the steps exactly as written. If a step fails or needs something the README doesn't mention, add it and start again.

### N10

Does the README link where to go for fuller use and for help?

**Thinking**

The README holds only what a reader needs to decide and to start. For each later need, such as fuller use or help, it links one place. A README that holds everything goes unread, and each later need has its own kind of page, which [Diátaxis](https://diataxis.fr) sorts into tutorials, how-to guides, reference, and explanation.

**Steps**

1. Open each link.
