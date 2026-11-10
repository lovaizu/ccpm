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
| C2 | The reader learns what they get from the product in work like their own. |
| C3 | The reader understands why the product can give it, and trusts that it does. |
| C4 | The reader installs the product and starts using it without help. |

## Necessary conditions

| ID | Factor | Condition | Sections |
| --- | --- | --- | --- |
| N1 | C1 | Does the opening say what the product is, who it's for, and what it lets them achieve? | the opening |
| N2 | C1 | Does the README list what readers might expect the product to do but it doesn't? | Non-goals |
| N3 | C1 | Does the README say at the top where the product isn't ready for use yet? | the opening |
| N4 | C1 | Does the README name the license and link its full text? | License |
| N5 | C1 | Does the README answer each question in the order a reader comes to ask it? | the whole |
| N6 | C2 | Does the walkthrough show a real run on typical work that delivers what the product vision's key results promise, in a form the reader can see? | Walkthrough |
| N7 | C3 | Does How it works state first, in the reader's words, the one way that the product vision's concept puts first, and build the rest of its explanation from it? | How it works |
| N8 | C3 | Does How it works answer the problems and doubts that bring readers to the product, each by the part of the product that answers it and how that part follows from the one way? | How it works |
| N9 | C4 | Can a reader with nothing set up install the product by the README alone, and see that it works? | Requirements, Installation |
| N10 | C4 | Does the README link where to go for fuller use and for help? | Documentation |
| N11 | C1 | Does the README hold only the vital few: nothing missing without which a reader fails to decide or to start, and nothing they could skip without loss? | the whole |

## Practices

### N1

Does the opening say what the product is, who it's for, and what it lets them achieve?

Most readers decide from the opening alone whether to read on, so it must let a newcomer tell within a few sentences whether the product is for them. Geoffrey Moore's positioning statement, from Crossing the Chasm, gives the decisions in order.

1. *While deciding.* Decide the target: the people the product is for, named by the work they want done, narrowly enough that a reader outside the group can tell it isn't for them.
2. *While deciding.* Decide their need: what they can't do well today, in their words.
3. *While deciding.* Decide the category: a kind of thing the reader already knows, such as a command-line tool, which gives them something to compare it with.
4. *While deciding.* Decide the key benefit: what they achieve with the product, taken from the objectives of the product vision, as an end they reach, not a feature.
5. *While making.* Write the opening from these four, in words the reader already uses, and leave out feature names and internals.
6. *While making.* Read only the opening, then put it away and explain the product as you would to a colleague. Shorten any part you forgot or got wrong, and replace each vague or praising word with what the product does.
7. *While making.* Read the opening as someone outside the target. If they couldn't tell that the product isn't for them, name the target and their work more precisely.

### N2

Does the README list what readers might expect the product to do but it doesn't?

A reader who needs something the product doesn't do should find out before they install it. A design document lists its non-goals for the same reason: they mark the edge of the scope where readers would otherwise guess.

1. *While deciding.* Derive the expectations from the opening: its category and its key benefit lead a reader to expect certain things, such as undoing its changes from a tool that edits files.
2. *While deciding.* For each thing the opening leads a reader to expect, ask whether the product does it, and whether its absence would change the reader's decision.
3. *While deciding.* Ask the user about each expectation whose scope the product vision doesn't settle.
4. *While making.* List only those that the product doesn't do and whose absence would. Where the product meets the need another way, say so in the same item.

### N3

Does the README say at the top where the product isn't ready for use yet?

A reader who builds on a product that isn't ready finds out only after their work depends on it.

1. *While deciding.* Decide the product's state by the states that [repostatus.org](https://www.repostatus.org) defines, such as Concept, Work in Progress, Active, and Unsupported.
2. *While making.* If the state is anything but Active, say it at the top, with what it means for the reader's work: what works now, and what they get if they install today.
3. *While making.* Check that a newcomer can say, after the opening, whether they can rely on the product today.

### N4

Does the README name the license and link its full text?

Some readers rule a product in or out by its license alone, so they must find it at once and recognize it.

1. *While making.* Take the license from the product's license file.
2. *While making.* Name the license by its identifier in the [Software Package Data Exchange (SPDX) License List](https://spdx.org/licenses/), which readers and their tools recognize, and link its full text.
3. *While making.* If the product includes work under other licenses, name each with its source.
4. *While making.* Open the link and check that it leads to the license the README names.

### N5

Does the README answer each question in the order a reader comes to ask it?

Readers come with questions in a typical order, and leave when the next answer isn't where they look. The [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts first what every reader needs, for the same reason.

1. *While deciding.* Decide the order by listing the readers and the question each has next. Every reader first asks what the product is and whether it's for them. A reader who has decided asks how to install it. A reader still deciding asks whether it really works, and how. A reader who has started asks where to learn more.
2. *While deciding.* Order the sections so that each answer comes just when its question does, and each reader can stop once they have what they came for.
3. *While making.* Read the README from the top as a newcomer, and after each section, write down the question you have next. The trace: `{deliverable}` read to its end.
4. *While making.* Check that the next section answers that question. Move any section that answers a later one.
5. *While making.* Remove what no reader needs at that point, or move it to a linked document.

### N6

Does the walkthrough show a real run on typical work that delivers what the product vision's key results promise, in a form the reader can see?

A reader trusts a benefit they've seen happen more than one they only read about. Diátaxis calls this a [tutorial](https://diataxis.fr/tutorials/): one concrete task, carried through to a visible result.

1. *While deciding.* Choose the use: the one that most readers come for, taken from what readers ask for most and from the main use of the product vision's objectives. The trace: `{inputs}` read to its end.
2. *While deciding.* Choose the task: one like the reader's own work, small enough to show from start to end, and real enough that the benefit shows in its result. If the result wouldn't show the benefit the opening promises, choose another task.
3. *While deciding.* Decide the cut: show every exchange from what the reader gives to the result they keep, with the product's real output, and cut only what doesn't bear on the result.
4. *While making.* Take each exchange from the record of a real run, in the form the reader meets it.
5. *While making.* Make each key result of the product vision show in the run, since the key results say what the product promises. For how well, show the result in use as its users would use it. For how fast, show what the reader spent, such as the questions they answered.
6. *While making.* State the result first, so that the reader knows where the run goes.
7. *While making.* Check that a newcomer can say, after reading, what the product would give them on their own work.

### N7

Does How it works state first, in the reader's words, the one way that the product vision's concept puts first, and build the rest of its explanation from it?

A reader trusts a product they can explain to themselves, and they explain it from one idea, not from a list of parts. Barbara Minto's pyramid principle, in The Minto Pyramid Principle, puts one governing thought at the top and makes everything below support it.

1. *While deciding.* Take the one way that the product vision's concept states first, which is what the product values most. Take the concept from the product vision. The trace: `{inputs}` read to its end.
2. *While making.* Say it in the reader's words, as what they see the product do in their work, in one sentence.
3. *While making.* Build the figure and the answers of How it works below it, so that each part shows how it carries out that one way.
4. *While making.* Check that a newcomer can say the one way back, and say how each answer follows from it.

### N8

Does How it works answer the problems and doubts that bring readers to the product, each by the part of the product that answers it and how that part follows from the one way?

A reader tries a product when the push of their problem and the pull of what the product gives them outweigh their doubts about it. Bob Moesta calls these the forces of progress, in Demand-Side Sales 101, from the theory of the jobs that customers hire a product for.

1. *While deciding.* List the problems that the target reader would name in their work, and the doubts they would raise about the product, in their words, such as, for a backup tool, that their backups fail without warning, or whether it works with their network drive.
2. *While deciding.* Keep only those whose answer would change whether the reader tries the product. A doubt that the walkthrough already settles needs nothing more.
3. *While deciding.* For each one left, take the part of the product that answers it, first from the product vision's concept, then from the architecture. Where neither has one, tell whether an idea that matters to the users is missing, or only the way to make it work.
4. *While deciding.* Where an idea that matters to the users is missing, ask the user to add it to the product vision. Where only the way to make it work is missing, record it in the design tree as a requirement that the architecture meets.
5. *While making.* Put those parts together as one mechanism below the one way, and say for each part how it follows from that way.
6. *While making.* Show it in one figure, with each problem and doubt beside the part that answers it, and what the reader gets from that part. Label each part in the reader's words, and where a part has a name of the product's own, explain the part in a few words.
7. *While making.* Check that a newcomer can say back how the product gives them what it promises, and why they can trust that it does.

### N9

Can a reader with nothing set up install the product by the README alone, and see that it works?

A reader who can't install the product never gets to use it, and the author's own setup hides what a newcomer lacks. [Standard Readme](https://github.com/RichardLitt/standard-readme) holds these in its Install section.

1. *While deciding.* Decide the steps by starting from a machine with nothing on it. List everything the product needs, each with a command whose output shows that the reader has it.
2. *While making.* Take each requirement and each install command from the product's manifest and code, never from memory.
3. *While making.* Write each install step as a command the reader can copy. End with a sign the reader can see that the product works. A step that only works with something the README doesn't mention is missing a requirement.
4. *While making.* On a machine or sandbox with nothing the product needs, follow the steps exactly as written. If a step fails or needs something the README doesn't mention, add it and start again.

### N10

Does the README link where to go for fuller use and for help?

The README stays short only if each later need has its own place to go. Each need has its own kind of page, which [Diátaxis](https://diataxis.fr) sorts into tutorials, how-to guides, reference, and explanation.

1. *While deciding.* Decide the links by listing what a reader needs after they start, such as fuller use, reference, help, and the changes in each version, and give one link for each, with whom it's for.
2. *While making.* Open each link.
3. *While making.* Check that each link opens the page it names.

### N11

Does the README hold only the vital few: nothing missing without which a reader fails to decide or to start, and nothing they could skip without loss?

Every line costs the reader time, and a line they don't need buries the ones they do, while a missing one stops them. The vital few, in Joseph Juran's term, come from what they serve: each section from the condition it meets, and each sentence from what its section must give.

1. *While making.* Write each section by deriving its content from its condition, not by gathering everything you could say and cutting it.
2. *While making.* Then read the whole README once as a newcomer, from the top to the first command. Mark each place where you would stop, because something you need isn't there, and each sentence you could skip without losing anything.
3. *While making.* Rebuild the section behind each mark from its condition.
4. *While making.* Check that a newcomer reaches the decision and the first command without stopping, and finds no sentence they didn't need.
