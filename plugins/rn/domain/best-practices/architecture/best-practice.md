# `architecture`

## Goal tree

- The developers build and change the parts of the product so that together they deliver what the README promises the users, each part putting its work on what brings the users there.
  - **C1** The developers know what each part must do, for the users or for the product's development and operation, and why.
    - **N1** Does Principles state first, in one sentence, the one idea by which the product delivers what its README promises? (Solution strategy, Principles)
    - **N2** Does each user story state a value that it brings its role on its own, in the role's words and without the product's means, and do the stories together cover each objective of the product vision and each promise of the README? (User stories)
    - **N3** Does each principle item, user story, component, and data trace to what the README promises the users, or to a need of the product's development or operation? (Principles, User stories, Components, Data model, Sequences)
  - **C2** Parts that different developers build fit together.
    - **N4** Does each principle name what it values, and each of its items one decision, with no name that a later section decides, from which two developers decide a case that no line names the same way? (Principles)
    - **N5** Does each component state its expected role, what it answers for toward the users' aim, and does each decision that the stories need belong to exactly one component? (User stories, Components)
    - **N6** Does each component state its type? (Components)
    - **N7** Does Data model say what each data is for, and show how the data relate, without their fields or any role's name? (Data model)
    - **N8** Does each user story have a sequence that shows, one action on each arrow, which component hands what to which and where the story branches, with each arrow and each branch condition tagged with the story or principle item that it carries out? (User stories, Components, Data model, Sequences)
    - **N9** Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does? (the whole)
  - **C3** The developers can place, set up, and start every part without asking anyone.
    - **N10** Does Deployment show each environment the product runs in, what runs in it, each store of data, each service outside the product, and how the product starts? (Components, Data model, Deployment)
    - **N11** Does Directory structure show the folders, with only the vital few files, and beside each top folder its purpose? (Components, Data model, Directory structure)
  - **C4** The developers find each gap between the parts before they build any part, and know, as they build, that the product does what the document and the product vision say.
    - **N12** Does Test strategy give, in its table alone, only the checks that the product's purpose needs, picked from the test strategy guide, each with its test target, its kind, and for a quality its criterion or for a benchmark what it measures? (Test strategy)
    - **N13** Is each gap that the software design and the test design found from the document mended in it, so that the two designs, made again from it, find none? (the whole)
    - **N14** Does each thing that the document says the product does rest on a part that a unit or integration test can check? (Components, Test strategy)
  - **C5** The developers can change the product without making the document wrong.
    - **N15** Does each view's Strategies give each decision of the view, tagged with the story or principle item that it carries out, with its intent? (Components, Data model, Sequences, Deployment, Directory structure)
    - **N16** Does the document hold only what stays true while the product vision and Principles stay, with no name of the implementation outside Directory structure? (the whole)

## Template

[template.md](template.md)

## Inputs

- [product-vision](../product-vision/best-practice.md), taking `Roles`, `Objectives and key results`, `Concept`
- [readme](../readme/best-practice.md), taking `the opening`, `Non-goals`, `Requirements`, `Walkthrough`, `How it works`

## Practices

### N1

Does Principles state first, in one sentence, the one idea by which the product delivers what its README promises?

Each view carries out one idea, and a developer who knows the idea builds a part that serves it. The [solution strategy](https://docs.arc42.org/section-4/) of arc42 sums up first the few decisions that shape the whole.

1. *While deciding.* Open your cut, and read the sections that `inputs` takes of each input it names: the product vision and the README, and, where the product builds on another's rules, the architecture it builds on, such as a guide to building a plugin of the host it runs in, to its end. The trace: `{inputs}` read to its end.
2. *While deciding.* Take the sentence that opens the product vision's Concept, the one idea by which the product brings its users to their objectives, such as piling up the vital few that bring a deliverable's people to their aim.
3. *While making.* Write it in one sentence that a developer can hold in mind while building any part, and put it first in Principles, before the principles that follow from it.
4. *While making.* After writing the rest, read each component's line as a developer who knows only the idea, and check that they can see which piece of the idea it carries out. Change the idea or the component where they can't.

### N2

Does each user story state a value that it brings its role on its own, in the role's words and without the product's means, and do the stories together cover each objective of the product vision and each promise of the README?

The stories are the product's requirements: what each role wants, which the views then meet. A story that names a means, such as a command, states a design as a want, so no one asks whether the design serves the want. A [user story](https://www.mountaingoatsoftware.com/agile/user-stories) doesn't prescribe the solution, which the conversation and the acceptance criteria settle, and a want that brings no value on its own, such as answering a question, is a step toward one, which the views draw.

1. *While deciding.* Open the product vision and the README, and list each objective and each promise the README makes, in its walkthrough, its Non-goals, and its How it works.
2. *While deciding.* For each objective, ask what value its role takes away on its own from a use of the product, such as the deliverable they're after, or a pause and a pick-up, and write each as a story in the role's words, without a command, a screen, or a part of the product.
3. *While deciding.* Where a want is a means toward such a value, such as answering points or signing off, leave it to Principles and Sequences, since a story of a means states a design as a want.
4. *While deciding.* Read each idea of the product vision's Concept, and ask at which moment of the use it keeps the one way holding. Where the role wants something there that no story carries, add a story for it, such as going on with a run that stopped.
5. *While making.* For each objective and each promise, name the stories that carry it, and add a story where none does. Leave an activity without a story of its own where another story already carries it.
6. *While making.* Read each story and ask whether it still holds where the product met it another way, such as a reply in place of a command. Rewrite each that doesn't, as it names a means, not a want, unless the role wants that means itself, such as working within the tool they already use.

### N3

Does each principle item, user story, component, and data trace to what the README promises the users, or to a need of the product's development or operation?

A part that nothing needs costs effort to build and to keep, and gives no one anything.

1. *While deciding.* For each story, ask which activity, doubt, or need it carries, from three sources. The README and the product vision carry what the users get: the objectives and the promises that N2 lists, and the doubts that the README's How it works answers. Development adds what the developers need to build, test, and change the parts. Operation adds what keeps the product working across runs and updates, such as where its work outlives a run.
2. *While making.* Once you have written Principles, for each principle item, name the doubt of the README's How it works, or the need of development or operation, that it carries.
3. *While making.* Once you have written the views, for each component and each data, find the strategy or the arrow of a sequence that reaches it.
4. *While making.* Remove each story or principle item that carries none, and each component or data that none reaches, from every figure, list, and sentence that names it.

### N4

Does each principle name what it values, and each of its items one decision, with no name that a later section decides, from which two developers decide a case that no line names the same way?

Developers of different parts meet the same kind of decision, and decide it apart unless a decision that every view follows settles it. A principle that names what it values carries a developer to a case that no decision names.

1. *While deciding.* Take each idea of the product vision's Concept, each key result, each user story that spans parts, and each constraint of the host, of development, or of operation, such as how much one conversation holds, and ask what every part must value for the one idea to keep holding there, such as nothing lost on a stop.
2. *While deciding.* Name each value in the people's words, as a few words that a developer weighs a case by, and write it as a principle, `P<n>`. Where two sources give the same value, keep one.
3. *While deciding.* Under each value, ask what every part must hold alike for it to come true, such as where the work's state lives. Take each from a doubt of the README's How it works whose answer the value keeps. For a value that comes from a story or a constraint and keeps no doubt's answer, take each from what that story or constraint needs. A part that held it otherwise would break a key result. Each is a decision of the principle.
4. *While making.* Write each decision under its principle as `P<n>.<m>`, one decision in one sentence, without any name that a later section decides, such as a component, a data, a tool, or a count, since Principles comes before the sections that decide them.
5. *While making.* Check that each doubt of the README's How it works lands in a value, and derive again the value it keeps where it lands in none. Remove each value that holds no decision, as it gives a developer nothing to hold to.
6. *While making.* Where your cut names an architecture that the product builds on, point to its principles, and write only what this product adds or changes.
7. *While making.* Take a case that no decision names, and decide it from each principle's value as two developers of different parts would. Where they differ, sharpen the decision that left the case open.

### N5

Does each component state its expected role, what it answers for toward the users' aim, and does each decision that the stories need belong to exactly one component?

Two components that make the same decision make it twice, and the two copies drift apart. David Parnas's information hiding gives each module one decision that's hard to make or likely to change, and hides it from the rest.

1. *While deciding.* Walk each story's steps, and name who acts at each: the role, a part of the product, or a thing outside the product. Each part of the product that acts is a component, of a kind that the architecture the product builds on offers where it offers kinds, such as a skill, a hook, or a script of a Claude Code plugin.
2. *While deciding.* Take from the stories the decisions that are hard to make or likely to change, such as where the product keeps the work's state, or the form of a file that two parts share.
3. *While deciding.* Give each decision to the one component that holds what it decides on, such as the form of the work's state to the component that writes the state. Where no component holds it, make a component for it.
4. *While deciding.* Where another component needs the same decision, leave it with the component that holds it, and draw an arrow by which the other asks it, such as a hook that asks a script whether a step is done instead of reading the state itself.
5. *While making.* Write under the figure each component with its expected role in one sentence: what it answers for toward the users' aim, not its tasks, such as `leads the run to the people's aim`, so that a developer knows what to build and what to leave to the others.
6. *While making.* Draw the roles and how they act on one another and on the data, with no implementation's name, and label each arrow with what one does to another and the data it hands on, as a word such as `uses` names no act.

### N6

Does each component state its type?

A developer who doesn't know what kind of thing a component is chooses alone, and the components stop fitting. The [C4 model](https://c4model.com/diagrams/container) gives each box its name and its type, such as a script.

1. *While deciding.* For each component, decide its type from the product's constraints and the kinds that the architecture the product builds on offers, such as a skill, a hook, or a script of a Claude Code plugin.
2. *While making.* Copy the template's skeleton of the figure to the deliverable's own.
3. *While making.* Give the figure a legend for every symbol.

### N7

Does Data model say what each data is for, and show how the data relate, without their fields or any role's name?

Two developers who build the writer and the reader of the same data must join it to the other data in the same way, while its fields stay free to change. A concept model in a class diagram of the Unified Modeling Language (UML), which most developers read, shows this. Data model comes before Components, so it names no role, and each later view names only what came before it.

1. *While deciding.* Walk each story and each principle item, and list each data that the product keeps or hands on, by the name the README gives it where it gives one, such as a run's record.
2. *While deciding.* For each pair that relates, name the relation, and give how many of each it joins at both ends, such as a run that holds one or more rounds.
3. *While making.* Draw each once, as a class by its name alone.
4. *While making.* Leave the fields to where the developer builds the data.
5. *While making.* Below the figure, say for each data what it's for, in one or two sentences, with no role's name, such as `holds what to make, why, and how far the run got`.

### N8

Does each user story have a sequence that shows, one action on each arrow, which component hands what to which and where the story branches, with each arrow and each branch condition tagged with the story or principle item that it carries out?

A developer building a step must know who hands them what, and what they hand on. A [UML](https://www.omg.org/spec/UML) sequence diagram draws a story's handoffs in order, from the role's first request to what the story gives them, while a step that stays inside one component belongs to its role, as a diagram that draws each such step buries the handoffs.

1. *While making.* For each story, draw each handoff from one component to another as an arrow with one action, the data it hands on in parentheses, named as in Data model, and write each step that stays inside one component in that component's role in place of an arrow.
2. *While making.* At each handoff, ask what can go otherwise there, from the README's walkthrough and from what each component alone decides: an input that a component refuses, a check that fails, or a choice that only the role can make, such as a question that the walkthrough shows the role answering.
3. *While making.* Draw an input refused as a branch, a check that fails as a step that sends work back to the step it repeats, and a choice of the role as a question put to the role with its answers, since each path of the story, and its integration test, rests on them.
4. *While making.* Tag each arrow and each branch condition, in brackets at its end, with the story or principle item that it carries out, such as `[P1.2]`, so that a developer sees why the step is there, and each story and principle item is carried out somewhere.
5. *While making.* Read each sequence as the developer who builds one of its steps, and check that they can tell who hands them what, along which arrow of Components, and what they hand on. Where no arrow carries a handoff, add the arrow, or give the step to another component.

### N9

Do the figures, lists, and sentences agree with one another, and with the architecture that the product builds on, on what each part does?

A developer who finds two places that say different things about a part must choose which to follow, and two developers choose differently.

1. *While making.* For each part, gather what every figure, list, and sentence says it does, and, where your cut names an architecture that the product builds on, what each of its rules asks of a part of that kind, such as a rule that every hook gives its result as JSON.
2. *While making.* Where two disagree, decide by the values of Principles and of the architecture it builds on which is right, and change the other.

### N10

Does Deployment show each environment the product runs in, what runs in it, each store of data, each service outside the product, and how the product starts?

A developer setting up the product needs to know where each part runs, what it can reach, and how it starts. A [C4 deployment diagram](https://c4model.com/diagrams/deployment) shows this.

1. *While deciding.* List each environment the product runs in, such as the user's computer or CI, with its technology.
2. *While deciding.* Place in its environment each component and each store of data by what runs there and where the data is kept, such as the run's folder in the user's repository. Name no process or other unit of the implementation.
3. *While deciding.* Add each service outside the product that the components depend on, with what they use of it, so that the figure holds what a developer sets up for the components.
4. *While making.* Write in one sentence how the product starts.
5. *While making.* Check that a developer could set the product up from nothing by the figure and that sentence.

### N11

Does Directory structure show the folders, with only the vital few files, and beside each top folder its purpose?

A developer making a change must find the one place it belongs. Simon Brown's package by component, in Robert C. Martin's *Clean Architecture*, lays out the code by the components that the architecture draws.

1. *While deciding.* Lay out the folders by component, so that each component and each data has its own place, such as a folder for the hooks and one for the code they call.
2. *While making.* Show each folder by its real name, nested as on disk, with only the files that a developer looks for first, such as the prompt of each component.
3. *While making.* Beside each top folder, write its purpose, such as what Claude Code installs for the user, and beside another folder or file only where its name doesn't say what it holds.
4. *While making.* Check that, for any change to a component, a developer can name the one folder it goes in.

### N12

Does Test strategy give, in its table alone, only the checks that the product's purpose needs, picked from the test strategy guide, each with its test target, its kind, and for a quality its criterion or for a benchmark what it measures?

A failure that no test looks for reaches the users unseen, and a case's pass or fail decides the work only where its criterion is set before anyone writes it. Where a result varies from run to run, as a prompt's does, a criterion passes or fails by chance, so a benchmark measures it and a person decides. A row for every check of the guide decides nothing for most of them, so Test strategy holds only the types the product's purpose needs.

1. *While deciding.* Read [the test strategy guide](test-strategy-guide.md) to its end. The trace: `${CLAUDE_PLUGIN_ROOT}/domain/best-practices/architecture/test-strategy-guide.md` read to its end.
2. *While deciding.* Take each check's test target from the guide. Unit tests try the parts against their contracts, each prompt among them. Integration tests try the parts joined against each element of this document. End-to-end (E2E) tests try the product in real use against each key result of the product vision. Use no other name for a test, so that each case's level tells which target it checks.
3. *While deciding.* Pick each check that the guide says to pick always, and each other check whose condition the product meets, given what it is and what it builds on, such as a contract test where the tests use a double of a host that changes on its own schedule. Write a row for each check picked.
4. *While deciding.* Make each check a benchmark where its test's path runs a prompt, as the guide's rule says, and each other check as the guide gives it.
5. *While deciding.* Take each quality's criterion that the guide recommends, or the one that the architecture the product builds on sets. Change it only where the product can't meet it, or a key result needs more, and say why in the row.
6. *While deciding.* For each benchmark, name what it measures, such as a key result or each case's results over several runs of a prompt. Set no criterion, as a person judges from the results.
7. *While deciding.* Set how many times a benchmark runs each case by its first runs: add runs until one more no longer changes what the results show, such as the mean of a key result by a step of its measure, since the AI's variance shows only across runs. Where the product can't run yet, write this rule in place of the number, for the first run to set it.
8. *While deciding.* For the trace of the architecture, set as the criterion that every element of this document, each story, principle item, component, and data, has an integration test, and that every test names an element or a case one level up that exists.
9. *While making.* Write one row for each check picked, in the guide's order, in the template's table. Name no tool and no means in it. Give each its kind as the guide or the prompt rule makes it.

### N13

Is each gap that the software design and the test design found from the document mended in it, so that the two designs, made again from it, find none?

A skeleton of the parts and test cases through it, made from the document before any body is built, show each gap between the parts while it's still cheap to mend: a case that no part can hold, or a handoff that no interface carries. Each gap mended in the document, not in the code around it, keeps the document true for each developer who builds on it.

1. *While making.* Once Test strategy is written, have the skeleton made from the document by [the software design best practice](../software-design/best-practice.md), and then the test cases by [the test design best practice](../test-design/best-practice.md), each with its list of gaps.
2. *While making.* For each gap that the lists name, change the document: give a case a part, or a decision a component; remove a part that no case reaches, as N3 says; split a component by its decisions or its reasons to change; and give a handoff an arrow and a data.
3. *While making.* Have the two designs follow the changed document as their practices say, and mend each gap they list again, until they list none.

### N14

Does each thing that the document says the product does rest on a part that a unit or integration test can check?

The E2E tests are slow and few, so they can only confirm what the lower levels already showed, and a thing that only a prompt holds varies from run to run, where only many runs on the model show it. The [Humble Object](https://martinfowler.com/bliki/HumbleObject.html) pattern of Gerard Meszaros's *xUnit Test Patterns* moves the logic out of a part that's hard to test into a part that a test can run.

1. *While deciding.* For each thing the document says the product does, name the part that holds it.
2. *While deciding.* Where only a prompt holds a rule that must hold on every run, give the rule to a part that a test can run, such as a guard of the architecture the product builds on, and draw that part in Components.
3. *While deciding.* Leave a judgment that only an AI can make, such as whether a point is the user's, with the AI, and measure it by the prompt's unit tests on the model, as N12.7 sets.

### N15

Does each view's Strategies give each decision of the view, tagged with the story or principle item that it carries out, with its intent?

A developer who doubts a decision and can't see what it was for may undo it and bring back the problem it solved. An [architecture decision record](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), by Michael Nygard, keeps a decision with its context, and its intent is what a developer needs to keep it.

1. *While deciding.* For each view, take each decision that a story or principle item rests on, such as a technology, a tool, or the form of a file that two parts share, and name the story or principle item that it carries out.
2. *While making.* Write each under its view's Strategies in one sentence, tagged in brackets with that story or principle item, such as `[P1.1]`, then `Intent:` with its purpose alone, with no means and no key result's ID.
3. *While making.* State a decision that the implementation spells out item by item as its policy, such as Lane applied to every activity of every role's steps that it can hold, since a list goes untrue at the next change.
4. *While making.* Leave out Strategies where the view takes no decision.

### N16

Does the document hold only what stays true while the product vision and Principles stay, with no name of the implementation outside Directory structure?

A line about how a component works inside becomes untrue at the next change to that component, and the developer then can't trust the document. David Parnas's [information hiding](https://doi.org/10.1145/361598.361623) keeps such details inside the module.

1. *While making.* For each line, ask whether it would become untrue if a component's internals changed while the product vision and Principles stayed.
2. *While making.* If it would, move it to where the developer builds the component.
3. *While making.* Read each line for what stays out: a name of the implementation outside Directory structure, a means or a key result's ID in an intent, a negative where the positive says it, a list that the implementation already decides, a term that no decision needs, and a sentence that another section or best practice holds. Remove each.
