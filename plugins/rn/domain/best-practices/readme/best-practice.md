# `readme`

## Goal tree

- A newcomer decides from the README alone whether the product fits their work, and if it does, starts using it.
  - **C1** The reader knows whether the product fits their work.
    - **N1** Does the opening say what the product is, who it's for, and what it lets them achieve? (the opening)
    - **N2** Does the README list what readers might expect the product to do but it doesn't? (Non-goals)
    - **N3** Does the README say at the top where the product isn't ready for use yet? (the opening)
    - **N4** Does the README name the license and link its full text? (License)
    - **N5** Does the README answer each question in the order a reader comes to ask it? (the whole)
  - **C2** The reader learns what they get from the product in work like their own.
    - **N6** Does the walkthrough show a real run on typical work that delivers what the product vision's key results promise, in a form the reader can see? (Walkthrough)
  - **C3** The reader understands why the product can give it, and trusts that it does.
    - **N7** Does How it works state first, in the reader's words, the one way that the product vision's concept puts first, and build the rest of its explanation from it? (How it works)
    - **N8** Does How it works answer the problems and doubts that bring readers to the product, each by the part of the product that answers it and how that part follows from the one way? (How it works)
  - **C4** The reader installs the product and starts using it without help.
    - **N9** Can a reader with nothing set up install the product by the README alone, and see that it works? (Requirements, Installation)
    - **N10** Does the README link where to go for fuller use and for help? (Documentation)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md)

## Practices

### N1

Does the opening say what the product is, who it's for, and what it lets them achieve?

Most readers decide from the opening alone whether to read on, so it lets a newcomer tell within a few sentences whether the product is for them.

1. *While deciding.* Open the product vision and take from Roles the people the product is for, named by the work they want done, narrowly enough that a reader outside the role can tell it isn't for them, such as `you keep a Python library that others install` in place of `you write Python`. The trace: `{inputs}` read to its end.
2. *While deciding.* Take from that role's objective what they achieve with the product, as an end they reach in their own work, not a feature, such as `release without breaking the code of those who use your library` in place of `checks for semantic versioning`.
3. *While deciding.* Take from the concept's one way the one thing the product gives the reader, in words the reader already uses, such as `finds each change in a release that breaks code that calls it`.
4. *While deciding.* Open the product's manifest, such as plugin.json or pyproject.toml, and name the kind of thing the reader installs by the word they already use for things of that kind, such as a command-line tool or a Claude Code plugin, so that they have something to compare it with.
5. *While making.* Write the opening by the template from these, and leave out feature names and internals.
6. *While making.* Read only the opening, then put it away and explain the product as you would to a colleague. Shorten any part you forgot or got wrong.
7. *While making.* Replace each vague or praising word in the opening, such as powerful or seamless, with what the product does.
8. *While making.* Read the opening as someone outside the role, such as, for a tool for those who publish libraries, a developer of an app who publishes none. If they couldn't tell that the product isn't for them, name the role's work more narrowly.

### N2

Does the README list what readers might expect the product to do but it doesn't?

A reader who needs something the product doesn't do finds out before they install it, not after their work depends on it.

1. *While deciding.* Open the READMEs of two or three products of the kind that the opening names, such as those that the product's issues mention or that a search for the kind finds first, and list what each does that a reader of this product might expect too.
2. *While deciding.* Add what the opening's benefit leads a reader to expect on the way to that end, such as undoing its changes, from a tool that edits files.
3. *While deciding.* Where the product has an issue tracker, add each request it closed without doing, such as one labeled `wontfix`.
4. *While deciding.* For each expectation, find whether the product meets it, in its commands and settings in the manifest and code, or by trying it.
5. *While deciding.* For each expectation it doesn't meet, ask whether a reader who needs it would decide against the product, and keep only those.
6. *While deciding.* Ask the user about each expectation that the product vision doesn't settle, as it neither has the users do or get it nor rules it out.
7. *While making.* List each kept expectation as a thing the product doesn't do.
8. *While making.* Where the product meets the need another way, say so in the same item, such as `doesn't undo its changes: commit before you run it, and git brings them back`.

### N3

Does the README say at the top where the product isn't ready for use yet?

A reader who builds on a product that isn't ready finds out before their work depends on it, not after.

1. *While deciding.* Open the product's manifest and its releases, such as the tags of its repository, and take its version: a version below 1.0, or no release, means what it does may still change.
2. *While deciding.* For each objective of the product vision, find the product's test of its role's use toward it, such as an end-to-end test, and check that it passes, or try the use where there's no test.
3. *While deciding.* Where the repository's archived mark or a notice in it says that no one keeps the product up, take that.
4. *While deciding.* Decide that the product is ready where it has a release of 1.0 or later, the use toward each objective works, and someone keeps it up. Otherwise, take what works now and what doesn't.
5. *While making.* Where the product isn't ready, write at the top what works now and what a reader gets who installs it today, such as `In development: it checks a release's functions, not yet its classes.`

### N4

Does the README name the license and link its full text?

Some readers rule a product in or out by its license alone, so they find it at once and recognize it.

1. *While making.* Open the product's license file, such as LICENSE in the product's folder, and read which license it holds. The trace: `{license}` read to its end.
2. *While making.* Name the license by its identifier in the [Software Package Data Exchange (SPDX) License List](https://spdx.org/licenses/), which readers and their tools recognize, such as MIT or Apache-2.0. Where the text matches no license on the list, ask the user.
3. *While making.* Link the license file by its path from the README's folder.
4. *While making.* Search the product's folder for the license files and notices of others' work, such as a copied library's own LICENSE, and name each license with the work it covers.
5. *While making.* Follow the link from the README's folder, and check that it opens the license file that the README names. The trace: `{license}` read to its end.

### N5

Does the README answer each question in the order a reader comes to ask it?

Readers come with questions in a typical order and leave when the next answer isn't where they look, so each answer stands where its question comes, and each reader stops once they have what they came for.

1. *While making.* Keep the sections in the template's order, which answers the questions in the order readers ask them: what the product is and whether it's for them, what it doesn't do, how to install it, what it gives in work like theirs, how it gives it, and where to go next.
2. *While making.* Within each section, put first what every reader of it needs, and after it what only some need, such as the one install command before the steps for another platform.
3. *While making.* Read the README from the top as a newcomer in the product vision's role, and after each section, write down the question you have next. The trace: `{deliverable}` read to its end.
4. *While making.* Where a section answers a question that a newcomer asks only later, move that answer to the section of that question.
5. *While making.* Where the next section doesn't answer the question you wrote, add the answer at its start, or, where a newcomer needs it neither to decide nor to start, link the document that holds it from Documentation.

### N6

Does the walkthrough show a real run on typical work that delivers what the product vision's key results promise, in a form the reader can see?

A reader trusts a benefit they've seen happen in work like their own more than one they only read about, so the walkthrough shows it happen.

1. *While deciding.* Open the product vision and take as the use the objective of the role that the opening names, or, where the role has several, the one whose use most readers come for, by the issues they open where the product has a tracker, and else the first.
2. *While deciding.* Choose the task from the work that readers bring to that use: the issues and questions they open, where the product has a tracker, or else the role's job in the product vision. Take one like most of theirs, small enough to show from start to end, and whose result shows the benefit the opening promises, such as, for a release checker, one release of a small library with one change that breaks its callers.
3. *While deciding.* For each key result of that objective, decide what in the run shows it. For how well, show the result in use as its users would use it, such as the caller's test that fails on the broken release. For how fast, show what the reader spent, such as the questions they answered.
4. *While deciding.* Decide the cut: keep every exchange from what the reader gives to the result they keep, and cut only output that doesn't bear on the result, such as progress lines.
5. *While making.* Run the task with the product from a fresh start, such as in a throwaway copy of the repository with an empty home folder, or take a recorded run of the same task, such as an end-to-end test's record, and keep each input and output as it came.
6. *While making.* Write each exchange from that run in the form the reader meets it: text as a code block, and a screen as an image from the run, kept in images/.
7. *While making.* Write the result first, so that the reader knows where the run goes.
8. *While making.* Check that a newcomer can say, after reading, what the product would give them on their own work.

### N7

Does How it works state first, in the reader's words, the one way that the product vision's concept puts first, and build the rest of its explanation from it?

A reader trusts a product they can explain to themselves, and they explain it from one idea, not from a list of parts.

1. *While deciding.* Open the product vision's Concept and take the one way it states first, which is what the product values most.
2. *While making.* Say it in the reader's words, as what they see the product do in their work, in one sentence, such as `It copies each file the moment you save it` in place of `continuous data protection`.
3. *While making.* Build the figure and the answers of How it works below it, so that each part shows how it carries out that one way.
4. *While making.* Check that a newcomer can say the one way back, and say how each answer follows from it.

### N8

Does How it works answer the problems and doubts that bring readers to the product, each by the part of the product that answers it and how that part follows from the one way?

A reader tries a product when what it gives them for their problem outweighs their doubts about it, so How it works answers both by a mechanism the reader can follow and trust.

1. *While deciding.* Open the product vision, and for each objective, write the problem its role has in that work today, in their words, such as, for a backup tool, `my backups fail without warning`.
2. *While deciding.* For each key result, write the doubt a reader would raise about whether the product gives it, in their words, such as `does it work with my network drive?`
3. *While deciding.* Where the product has an issue tracker or discussions, add each problem or doubt that someone raised there before they used the product.
4. *While deciding.* Keep only those whose answer would change whether the reader tries the product, and drop each that the walkthrough already settles.
5. *While deciding.* For each one left, take from the concept the idea that answers it.
6. *While deciding.* Where the concept has none, tell what's missing: an idea that matters to the users, where the answer would change what they do or get, or only the way to make it work, where they'd do and get the same.
7. *While deciding.* Where an idea that matters to the users is missing, ask the user to add it to the product vision.
8. *While deciding.* Where only the way to make it work is missing, hand it back as a requirement that the architecture meets, such as with rn's `asks`.
9. *While making.* Put those parts together as one mechanism below the one way, and say for each part how it follows from that way.
10. *While making.* Show the mechanism in one figure, with each problem and doubt beside the part that answers it, and what the reader gets from that part.
11. *While making.* Label each part in the reader's words.
12. *While making.* Where a part has a name of the product's own, explain the part in a few words.
13. *While making.* Check that a newcomer can say back how the product gives them what it promises, and why they can trust that it does.

### N9

Can a reader with nothing set up install the product by the README alone, and see that it works?

A reader who can't install the product never gets to use it, and the author's own setup hides what a newcomer lacks.

1. *While deciding.* Open the product's manifest and code, and list each requirement and install command they show, such as `engines` in package.json or `requires-python` in pyproject.toml, never from memory.
2. *While deciding.* For each install command, list what it needs on a machine with nothing on it, such as the tool it calls or an account it signs in to, and add each to the requirements.
3. *While deciding.* For each requirement, choose a command whose output shows the reader they have it, such as `git --version`.
4. *While making.* Write each install step as a command the reader can copy.
5. *While making.* End the steps with a sign the reader can see that the product works, such as the version it prints or its first command answering.
6. *While making.* Run each check and install command exactly as the README writes it, on a machine with nothing the product needs, such as a throwaway copy with an empty home folder. Where a step fails or needs something the README doesn't name, add it, and start again. The trace: `{install}` run.

### N10

Does the README link where to go for fuller use and for help?

The README stays short only if each later need has its own place to go, so a reader who has started finds where to go for fuller use and for help.

1. *While deciding.* List what the product has for a reader who has started: the documents in its folder, such as a docs folder or a changelog, and the place for help that its manifest names, such as `bugs.url` in package.json or the issues of `repository` in plugin.json.
2. *While deciding.* Keep each that serves a need the README leaves, such as fuller use, reference, help, or the changes in each version.
3. *While deciding.* Where help has no place, ask the user where readers go for it.
4. *While making.* Give one link for each, by its path from the README's folder or by its URL, with whom it's for and what it gives.
5. *While making.* Open each link from the README's folder, and check that it opens the page it names.
