# `meta`

## Goal tree

- A generator that follows a best practice produces deliverables that serve their users' purpose.
  - **C1** The necessary conditions cover what users need from the deliverable.
    - **N1** Does the goal state, in one sentence, who uses the deliverable and what purpose it serves for them? (goal)
    - **N2** Do the critical success factors name the few things that must all hold for the users to reach the goal? (critical_success_factors)
    - **N3** Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs? (necessary_conditions)
    - **N7** Does following the best practice put into the deliverable only the vital few, the things without which its users fail their goal? (the whole)
  - **C2** The generator meets every necessary condition in every deliverable.
    - **N4** Does the template place each necessary condition in a section, and give each slot a note on what it holds and in what form? (template)
    - **N5** Does each practice give the steps that produce its condition's state, in the order that a practitioner who makes that kind of deliverable takes them on site, each an act on something at hand with the question to ask, the criterion for choosing where there are options, and an example where the act alone would leave the reader unsure, so that a reader of a step can say what they open next and what they do there? (why, items)
  - **C3** Each deliverable stays consistent with the deliverables it builds on and the deliverables built on it.
    - **N6** Does the best practice name the kinds of deliverable that this kind builds on, with a condition that carries each of their vital few that its users need, and the kinds that must pass before work on it starts? (inputs, preconditions)

## Template

[template.json](template.json)

## Practices

### N1

Does the goal state, in one sentence, who uses the deliverable and what purpose it serves for them?

Every later decision rests on the goal, so a goal that names the purpose the users have, not a means to it, lets each factor, condition, and step serve what the users came for.

1. *While deciding.* Open your cut, and read to its end each input it names, such as the product vision, whose roles name the product's people. The trace: `{inputs}` read to its end.
2. *While deciding.* Open `best-practice.json` in each folder of `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/`, where rn keeps its own, and of `.rn/best-practices/`, where it keeps those made on the product's runs, and take each best practice whose `inputs` hold this kind's folder name, as its users use a deliverable of this kind through the deliverable it makes.
3. *While deciding.* From the inputs and the best practices you took, list each kind of person who reads or runs a deliverable of the kind, with what they're trying to get done when they do, such as a developer who opens a README to decide whether a plugin solves their problem.
4. *While deciding.* Write one sentence with those people as the subject and what they achieve as the verb.
5. *While deciding.* Ask of the sentence why that achievement matters to the users, and write the answer as a sentence in the same form. Repeat until the next answer goes beyond what the deliverable can affect, and keep the last sentence within its reach as the goal, such as `starts using the plugin` for a README, where `ships their product sooner` goes beyond it.
6. *While deciding.* If the sentence names a part of the deliverable, such as a section or a feature, it states a means: ask why once more.
7. *While making.* Read the goal's sentence with the deliverable's name taken out. If it no longer says what the users achieve, rewrite it.

### N2

Do the critical success factors name the few things that must all hold for the users to reach the goal?

The factors decide where the generator spends its effort, so when they're the few things that the users can't reach the goal without, the effort goes where the users would otherwise fail.

1. *While deciding.* Read the goal's sentence and list each thing that must go right for the users to reach it, or they fail.
2. *While deciding.* Write down, in order, each moment of the users' use of the deliverable, from the moment they first meet it to the moment they reach the goal, such as a README's reader landing on the page, deciding to install, installing, and first using the product.
3. *While deciding.* At each moment, ask whether the users could still stop or go wrong there while every thing on the list goes right. Where they could, add to the list the thing that would stop it.
4. *While deciding.* Write each thing on the list as a state in one sentence, such as `The reader sees on the first screen which problem the product solves`.
5. *While deciding.* Of each pair of states, ask whether one can fail while the other holds. Where neither can, merge the two into one.
6. *While deciding.* Of each state, ask: if it failed, would the users still reach the goal? Where they would, drop it.

### N3

Does each necessary condition ask, as a yes-or-no question, whether the deliverable holds a state that its factor needs?

The conditions are what the generator meets and the evaluator checks, so when each is a state that someone reading only the deliverable can confirm, every deliverable meets the same states, and every evaluator judges them the same way.

1. *While deciding.* For each factor, list the states of the deliverable that make it true, such as `the first paragraph names the problem` for a README's factor that the reader sees which problem the product solves.
2. *While deciding.* Write each state as a yes-or-no question about the deliverable, under its factor, such as `Does the first paragraph name the problem that the product solves?`
3. *While deciding.* Judge each condition by three tests, and rewrite or drop one that fails any. It's checkable: two readers of the deliverable give the same answer. It's about the deliverable, not about how someone made it, as `Did the maker interview users?` is. It's necessary: if the answer were no, its factor would fail.
4. *While deciding.* If a condition needs several states of its own, make it a factor.
5. *While deciding.* If a condition only says how to meet another condition, move it into that condition's practice.
6. *While making.* Search the repository for the deliverable of the kind that the product in your cut has, by the names and folders in which the deliverables you opened at N4.1 keep theirs, such as `README.md` at the top of the repository for a README.
7. *While making.* Where the product has none, write one from the template for the product in your cut, as `trial.<ext>` in the round's folder, the folder of `{made}`, so that the trial stays out of the product.
8. *While making.* Answer each condition yes or no about that deliverable.
9. *While making.* Read that deliverable from the top as its users would. Where they would stop or go wrong in a part that every condition passes, find the level that caused it, whether the goal, a factor, a condition, or a practice, and rebuild that level from the level it serves.

### N4

Does the template place each necessary condition in a section, and give each slot a note on what it holds and in what form?

The template makes every deliverable of the kind hold each condition in the same place and the same form, so that no run invents the structure and the users find each thing where every other deliverable of the kind keeps it.

1. *While deciding.* Open three or more deliverables of the kind made for different products, from the repository or from a search of the web, such as the READMEs of popular plugins on GitHub.
2. *While deciding.* Take the format that those deliverables share as the deliverable's format, such as Markdown for a README. Where they differ, take the format that the tool or code that reads the deliverable takes, such as JSON for a file that a program loads.
3. *While deciding.* Run `git ls-files '*.schema.json'`, and read the title and description of each JSON Schema that it lists. The trace: `git ls-files '*.schema.json'` run.
4. *While deciding.* Where one of those schemas describes the deliverable, as design-tree.schema.json describes the design tree, take it as the template: its fields are the sections, and the description of each field is its note, since a second template would state each field's form twice. Elsewhere, write the template in the deliverable's format, where each heading, or in JSON each key that holds content at any depth, is a section.
5. *While deciding.* Order the sections as the users look for them, from the first thing to the last, such as a README's statement of what the product is before its install steps.
6. *While deciding.* Place each condition in the section where the users need it, and name that section in the condition's `about`.
7. *While deciding.* For each piece of text, ask whether every deliverable of the kind says it the same way. If it does, write it as fixed text. If it differs, make it a slot.
8. *While deciding.* For each slot, choose the form that keeps the content the same shape across deliverables, such as one sentence, a list of commands, or a table with fixed columns. Each run fills a slot without a form in its own way.
9. *While deciding.* Where a slot's practice calls for a figure, choose a text format that shows each change in a diff, such as Mermaid for a sequence or SVG for other figures.
10. *While making.* Mark each slot so that the reader can tell it from fixed text and the rendered page still shows it, such as `` `<name>` `` in Markdown.
11. *While making.* After each section, write one note that says, for each slot, what it holds, the form it takes, whether it's optional, and, for a figure, where the deliverable keeps its own.
12. *While making.* Start each note with a marker by which the generator finds and deletes it, in the form the deliverable's format allows, such as a note block in Markdown or a key in JSON.
13. *While making.* Where a slot holds a figure, put a skeleton of the figure in the template, labeled with the names of its slots.

### N5

Does each practice give the steps that produce its condition's state, in the order that a practitioner who makes that kind of deliverable takes them on site, each an act on something at hand with the question to ask, the criterion for choosing where there are options, and an example where the act alone would leave the reader unsure, so that a reader of a step can say what they open next and what they do there?

A practice is the only place where the generator learns how to meet a condition well, and a theory, model, or standard in place of the steps, such as a list of quality characteristics, leaves each run to work out what to do in its own way. So a practice writes the acts that practitioners of the kind take, in the way the procedures page of the Google developer documentation style guide writes a procedure: one action for each step, and the step's place and goal stated before its action.

1. *While deciding.* Search the field's guides, handbooks, and worked examples of the deliverable's kind for how practitioners who make it do the work, and write down the acts they take in the order they take them, such as a test lead who lists the key results, asks of each which failure would stop the users, and picks a type of testing for each failure. Take an act only where the source says what the practitioner opens and what they do there, since a method's name or a model alone doesn't tell the generator what to do.
2. *While deciding.* For each theory, model, standard, or list that the research turned up, such as the quality characteristics of ISO/IEC 25010, ask which act walks through it. Keep it only as the list that act uses, such as the types of testing that the act of picking a type for each failure chooses from, and drop it where no act uses it, since a step that starts from an abstract list leaves the reader to work out what to do.
3. *While making.* Write in `why`, in one or two sentences, what the condition gives the users. Name a source only where it's itself a practitioner's way of doing the work, in `why`, such as a style guide's page on writing procedures, or the list that an item uses, in that item, never a method only to cite it.
4. *While making.* List the items in the order the generator takes them on site: each decision, then each step, and last, only where the condition's own question doesn't already say how to check it, how to check the result from the users' side, such as asking whether a newcomer can say the point back.
5. *While making.* Write each item as an act on something that the generator has, such as a file, a list, or a command, with the question to ask and, where there are options, the criterion for choosing, such as `Open the product vision and list its key results` in place of `Consider the quality characteristics`.
6. *While making.* Give an example from the deliverable's kind only where the act alone would leave the generator unsure what to open or what to write, such as the form of a sentence it must write, since an example beside a plain act is one more line to read past.
7. *While making.* Make each item one thing to take, since a role names each item it took by its ID, its condition's ID and its place, such as N6.2, and a check finds one left out.
8. *While making.* Give a trace to each item that every run takes and a tool call shows: a command it runs, a file it reads in full, or a file it writes. An item with a trace takes its place by its call, among the decisions or steps whose content it supplies, such as the read of an input just before the decision that takes from it, since a checker such as Lane checks each item by its trace in the order of the calls, and the evaluator checks what the judgments made.
9. *While making.* Mark each item `decide` where the maker takes it while it settles the work's decisions, and `make` where it takes it while it makes the deliverable. No `decide` item follows a `make` item, since the maker settles the decisions before it makes the deliverable.
10. *While making.* Where the generator must find the content before it writes it, such as the users of a product vision, say what the content serves, how to derive it from that, and when to ask the user.
11. *While making.* Write each reason and each way to find the content in the item that uses it, and the form of each slot in the template's note, so that each fact stands in one place.
12. *While making.* Name a language or a tool only as an example, so that each deliverable's plan chooses its own.

### N6

Does the best practice name the kinds of deliverable that this kind builds on, with a condition that carries each of their vital few that its users need, and the kinds that must pass before work on it starts?

A deliverable must say what the deliverables it builds on say, and the deliverables built on it must follow it, so that the users never meet two deliverables that disagree.

1. *While deciding.* Go through each section of the template and ask where its content comes from. Each kind of deliverable that supplies content is an input, such as the product vision for a README.
2. *While deciding.* Of each input, ask whether work on the deliverable can start while the input still changes. Where it can't, the input's kind is a precondition too, such as an agreed product vision for a README.
3. *While deciding.* Go the other way, from each input to the deliverable, since a deliverable that drops what it rests on fails its users while every part it holds is sound: take the input's vital few, such as the concept and the key results of a product vision, and ask which of them the deliverable's users need.
4. *While deciding.* For each of those vital few that the users need, decide which part of the deliverable carries it.
5. *While deciding.* Make sure a condition asks for each of those vital few, such as a README showing what the key results promise.
6. *While making.* List the inputs in `inputs` and the preconditions in `preconditions`, each by the folder name of its best practice.
7. *While making.* Leave out the kinds built on this kind, since their best practices name it in `inputs`, and listing them here as well would write the same fact twice.
8. *While making.* Leave out the paths of the inputs, since the plan holds the paths of each deliverable's inputs and orders the deliverable after them.
9. *While making.* Where you change a best practice that exists, update, in the same change, each condition that carries what you changed in each best practice that N1.2 took, such as a README's condition on the key results when the product vision's key results change.
10. *While making.* Where an input's best practice changed since this one last changed, open it, and check each condition here that carries its vital few against what it holds now.

### N7

Does following the best practice put into the deliverable only the vital few, the things without which its users fail their goal?

A deliverable that holds the trivial many beside the vital few buries what its users need, and each round of work adds more, so when every part serves what the users can't go without, they find what they need at once.

1. *While making.* Read each item by which the generator finds the content it writes, such as the item by which a README's generator finds the problems it names, and ask what the item starts from. Where it gathers every thing of a kind and then keeps some, such as every problem that readers have, rewrite it to take the things from the part of an input or of the goal that its condition serves, such as the problems from the product vision's objectives and their key results, since gathering first fills the deliverable with the many.
2. *While making.* Read the best practice from its goal down, and for each factor, condition, and item, name what it makes true in the level it serves, such as the factor that a condition makes true. Drop each that makes nothing there true.
3. *While making.* Read the conditions and the items for any that counts or caps the parts, such as `at most five sections`, and remove it, since the few follow from the build, and such a check adds findings of its own.
