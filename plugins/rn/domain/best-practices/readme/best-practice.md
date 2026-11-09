# `readme`

## Goal

Someone who meets the product for the first time starts using it, from the README alone, only when it serves their work.

## Template

[template.md](template.md)

## Example

[example.md](example.md), a copy of [../../../README.md](../../../README.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The reader knows whether the product serves their work. |
| C2 | The reader believes the product gives what it promises, before they try it. |
| C3 | The reader gets the product working on their own. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Reading the opening, does the reader tell what the product is and what it would let them do, so that they know whether the product serves their work? | the opening |
| N2 | C1 | Before installing, does the reader see what the product doesn't do that they might expect of it, so that they know whether the product serves their work? | the opening |
| N3 | C1 | Before installing, does the reader see where the product isn't yet fit for use, so that they know whether the product serves their work now? | the opening |
| N4 | C1 | Weighing the product, does the reader find the terms on which they and their team may use it, so that they know whether the product serves their work? | License |
| N5 | C1 | Reading from the top, does the reader find each answer just when they come to need it, so that they know whether the product serves their work without reading past what they need? | the whole |
| N6 | C2 | After the walkthrough, has the reader seen the product give, on work like theirs, the gain the opening promised, so that they believe the product gives what it promises before they try it? | Walkthrough |
| N7 | C2 | For each problem they feel in the work, does the reader picture how the product makes it go away, so that they believe the product gives what it promises before they try it? | How it works |
| N8 | C2 | At each point where they would ask whether the product can really do that, does the reader picture how it does it, so that they believe the product gives what it promises before they try it? | How it works |
| N9 | C3 | Starting with nothing set up, does the reader install the product by the README's steps alone and see that it works, so that they get the product working on their own? | Requirements, Installation |
| N10 | C3 | Needing more than the README gives, such as fuller use or help, does the reader find where to go next, so that they get the product working on their own? | Documentation |

## Practices

### N1

Reading the opening, does the reader tell what the product is and what it would let them do, so that they know whether the product serves their work?

**Thinking**

The opening names the kind of thing the product is, whom it's for by the work they want done, and the end they reach with it, from the objectives of the product vision, in words the reader already uses and with no feature name or mechanism. Its first sentence says in short what the product is. From it, the reader judges whether the product serves their own end, and whether to read on. It takes the form of Geoffrey Moore's positioning statement in Crossing the Chasm: for whom, their need, the category, and the one benefit.

**Steps**

1. Read only the opening, put it away, and say it as to a colleague. Where a part goes missing or comes out otherwise, shorten it, or put what the product does in place of each vague or praising word.
2. Name the group and the work more closely where a reader outside that group couldn't tell that the product isn't for them.

### N2

Before installing, does the reader see what the product doesn't do that they might expect of it, so that they know whether the product serves their work?

**Thinking**

List each thing a reader could reasonably expect of the product and it doesn't do, as the non-goals of a design document name what lies outside its scope. A reader who needs one of them then learns that before they install.

**Steps**

1. Gather what readers might expect from similar products and from what readers ask, and ask the user whether each is in or out.

### N3

Before installing, does the reader see where the product isn't yet fit for use, so that they know whether the product serves their work now?

**Thinking**

Where the product isn't yet fit for use, such as a release still in development or one no longer kept up, say so at the top, by the state as [repostatus.org](https://www.repostatus.org) names the states of a project, such as work in progress, and what it means for the reader's work. A reader who starts on it otherwise finds out only once their work rests on it.

### N4

Weighing the product, does the reader find the terms on which they and their team may use it, so that they know whether the product serves their work?

**Thinking**

Name the license by its identifier in the [Software Package Data Exchange (SPDX) License List](https://spdx.org/licenses/) and link its full text. A reader may rule the product in or out by its license alone, and the identifier lets them and their tools recognize it at once.

**Steps**

1. Open the link, and check that it reaches the license the name says.

### N5

Reading from the top, does the reader find each answer just when they come to need it, so that they know whether the product serves their work without reading past what they need?

**Thinking**

Order the README so that each reader stops once they have what they came for: the opening for every reader, the installation for one who has chosen the product, the walkthrough and How it works for one still weighing it, and what comes after through links. A reader who must pass what they don't need leaves before what they do, as the [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts first what every reader needs.

**Steps**

1. Read the README from the top as someone who meets the product for the first time, and after each section, write the question the reader now has. The trace: `{deliverable}` read to its end.
2. Check that the next part answers that question. Move a section that answers a later one.
3. Cut what no reader needs at the point where it stands, or move it to the document a link leads to.

### N6

After the walkthrough, has the reader seen the product give, on work like theirs, the gain the opening promised, so that they believe the product gives what it promises before they try it?

**Thinking**

Show one real run of the use most readers come for, on work like theirs, from what the reader gives to the result they keep, with the product's real output. The reader then watches the gain happen. It's the one task a tutorial carries the reader through to its result, as [Diátaxis](https://diataxis.fr/tutorials/) names a tutorial.

**Steps**

1. Pick the use from what readers ask for most and from the objectives of the product vision. The trace: `{inputs}` read to its end.
2. Take each exchange from the record of a real run, in the form the reader meets it, cutting only what the reader doesn't need to see the result.
3. If the result doesn't show the gain the opening promised, pick another piece of work or another use.

### N7

For each problem they feel in the work, does the reader picture how the product makes it go away, so that they believe the product gives what it promises before they try it?

**Thinking**

Each problem the reader feels in the present way, in their own words, gets a figure in which they see it left in that way and gone with the product, and a sentence or two on what the product does that makes it go away. A reader chooses the product once they can picture their own problem gone. These are the pains and the pain relievers of the Value Proposition Canvas of Alexander Osterwalder.

**Steps**

1. Take the problems from the Concept section of the product vision, one where the present way falls short for each idea, and from what readers complain of in that way. The trace: `{inputs}` read to its end.
2. For each, take from the design what the product does that makes it go away. Ask the user each one the design doesn't settle.
3. Look at each figure as a newcomer, and where they couldn't picture from it what its line says, draw it again.

### N8

At each point where they would ask whether the product can really do that, does the reader picture how it does it, so that they believe the product gives what it promises before they try it?

**Thinking**

Each point a newcomer would doubt gets a figure of its own that draws what its line says, and a sentence or two on how the product does it. A reader believes a product can do a thing once they can picture how, as the conceptual model in Don Norman's The Design of Everyday Things lets a user predict what a thing does. One figure for each doubt lets the reader see each at a glance.

**Steps**

1. Read the README as a newcomer, and mark each thing it says that the present way can't do. Ask of each answer what the newcomer would doubt next, until no doubt remains. The trace: `{deliverable}` read to its end.
2. For each point, take how the product does it from the design. Ask the user each one the design doesn't settle.
3. Look at each figure as a newcomer, and where they couldn't picture from it what its line says, draw it again.

### N9

Starting with nothing set up, does the reader install the product by the README's steps alone and see that it works, so that they get the product working on their own?

**Thinking**

The requirements and the install steps serve a reader who has nothing set up, each as a command to copy, and end with a sign that the product works, as the Install section of [Standard Readme](https://github.com/RichardLitt/standard-readme) holds them. The author's own setup hides the gaps.

**Steps**

1. From a machine or sandbox where nothing the product needs is in place, follow the steps as written and do nothing they don't say. If a step fails or needs what the README doesn't say, write that in and start again.

### N10

Needing more than the README gives, such as fuller use or help, does the reader find where to go next, so that they get the product working on their own?

**Thinking**

The README holds what the reader needs to decide and to start. For each later need, such as fuller use or help, it links one place. No one reads a README that holds everything, and each later need has its own kind of page, as [Diátaxis](https://diataxis.fr) sorts tutorials, how-to guides, reference, and explanation.

**Steps**

1. Open each link.
