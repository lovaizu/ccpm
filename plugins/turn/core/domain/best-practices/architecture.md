# architecture

## Goal

Whoever builds or changes the product, a person or an AI, makes each part without hesitating and on the same thinking as every other part, so the parts together deliver the UX and the product stays easy to read and to change.

## Parts

- **summary**: The opening: which product the document is for, and a sentence or two that say how the product delivers its UX, pointing to the UX instead of repeating it.
- **principles**: The principles, after a pointer to the principles of the architecture this one is built on, where there is one. Each has a short name the reader finds it by, the rule, one sentence that every part is built by, and the reason, which says what the rule is there for and what goes wrong for the user or the builder without it.
- **user-stories**: The user stories: one for each way the user uses the product at its edge, such as a command they run, each naming the user, that way, and the UX's scenarios or steps that rest on it.
- **components**: A figure of the roles the user stories need and each store of data, read without the text around it. Each element holds its name, its type and its technology, such as a web app in React and TypeScript or a database in PostgreSQL, and nothing more. Each arrow says what one does to another, with the data it hands on, named as in the data model, and the protocol where it matters, such as HTTPS with JSON. A legend explains every symbol the figure uses. The arrows are laid out so the reader follows them in the order they act.
- **responsibilities**: Read with the components figure: what each role alone is responsible for that no arrow shows.
- **choices**: For each choice the reader would question, such as a technology or a tool, why it was made over the other way, set where the reader meets the choice.
- **data-model**: A figure of each data the roles pass or keep, showing its name alone, and of each relation between two data, labelled with the relation's name and marked at both ends with how many of each it joins, such as one to many.
- **sequences**: For each user story, its steps in the order they happen, drawn so the reader follows them from first to last. It shows the user, each role the story reaches, named as in Components, and each thing outside the product it reaches; and each step, labelled in a few words with what one does to another and the data handed on, named as in the data model.
- **deployment**: A figure of each execution environment, such as a cloud service, a phone, the user's computer or CI, with its technology. Each environment holds its deployment units, such as an app or a container, each with its technology and, by their names in Components, the roles that run in it and the data kept in it. Each thing outside the product that they depend on is shown, with what is used. With the figure, how the product is started, and choices.
- **directory**: The place where each role and each data lies: the folders and files that hold them, nested as on disk, each naming the role or the data it holds as in Components, with its technology, and none of the files inside a role.
- **test-table**: A table the reader takes in at a glance: a row for each deployment unit, named as in Deployment with its technology; a column for each test type the product uses, from narrow scope to wide, such as unit, integration and end-to-end; in each cell the tool, a weight, such as ●●● or ●●○, and what it checks in a few words; each empty cell marked as empty, with why it is empty; and the units left out because every cell of their row would be empty, with why.
- **test-rules**: For each test type, including any the product adds, what it makes real, what it fakes and when it passes, and, for a result that varies from run to run, how many runs of how many must meet the expectation; each unit's weight with what a failure costs the user; and, before the table, a pointer to the project's shared test rules, with only what differs written here.

## Benefits

- **Q1** (user-stories): For each step of the UX's scenarios, can the builder name the one way of using the product at its edge that carries it?
- **Q2** (summary): Having read the opening, can the builder say how the product delivers its UX, as one idea that every part carries out?
- **Q3** (user-stories, components, responsibilities): For anything the user stories need decided, can the builder point to the one role that decides it?
- **Q4** (components): Starting on a role, can the builder begin without choosing for themselves what kind of thing it is and what it is made with?
- **Q5** (data-model): When one builder makes the role that writes a data and another makes the role that reads it, do both join it to the other data the same way?
- **Q6** (user-stories, components, data-model, sequences): For each user story, can the builder follow it from the user's first request to its end, knowing at each step which role acts and what data it hands on?
- **Q7** (user-stories, components, responsibilities, data-model, sequences): Of any user story, role or data, can the builder tell which objective of the UX needs it?
- **Q8** (principles): When two builders of different parts meet a case the document does not name, does a principle's reason lead both to the same decision?
- **Q9** (components, data-model, deployment): Setting the product up from nothing, can the builder put each role where it runs and each data where it is kept, and start the product, without asking anyone?
- **Q10** (components, data-model, directory): Making or changing a role or a data, can the builder find the one place its files belong?
- **Q11** (deployment, test-table): Asked whether anything in the product goes untested, can the builder answer, for each deployment unit, which types of test cover it, how heavily, and why a type is missing?
- **Q12** (test-table, test-rules): Writing a test of one type, can the builder do it without deciding for themselves what to make real, what to fake and when it passes?
- **Q13** (principles, components, responsibilities, sequences, deployment, directory, test-table, test-rules): Following a principle while building a part, does the builder find every figure, list and table asking the same of that part, so they never have to choose which to follow?
- **Q14** (choices, test-rules): When the builder doubts a choice the document makes, can they tell what would be lost by taking the other way?
- **Q15** (the whole): When the builder changes how a role works inside, while the UX and the principles stay, does every line of the document still hold?

## Practices

### Q1: For each step of the UX's scenarios, can the builder name the one way of using the product at its edge that carries it?

**Thinking**: A user story is one way the user meets the product at its edge, such as one command or one call, and the stories together carry every step of the UX where the user meets the product.

**Steps**

1. Write each story naming the user, the way and the scenarios or steps it carries, such as "As <the user>, I want <the way>. Carries <the scenarios or steps>."
2. Walk each scenario of the UX step by step, and check that each step where the user, a person or an AI, meets the product is carried by one story; add a story for a step that none carries.

**Grounds**

- [3. Context and Scope](https://docs.arc42.org/section-3/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "System scope and context - as the name suggests - delimits your system (i.e. your scope) from all its communication partners (neighboring systems and users, i.e. the context of your system)."
- [User Stories: What They Are, How to Write Them, and Examples](https://www.mountaingoatsoftware.com/agile/user-stories), Mountain Goat Software, mountaingoatsoftware.com, 2026: "A common template is: As a [type of user], I [need/want/am required] to [do something], so that [reason or benefit]."
- [Architectural Blueprints—The “4+1” View Model of Software Architecture](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf), Kruchten, IEEE Software, 1995: "as a driver to discover the architectural elements during the architecture design as we will describe later"

### Q2: Having read the opening, can the builder say how the product delivers its UX, as one idea that every part carries out?

**Thinking**: The opening says, in one idea seen from above and with none of a part's inner workings, how the product turns what the user brings into what the UX promises, so every part after it reads as a piece of that idea.

**Steps**

1. Link the UX instead of repeating it.
2. Once the rest is written, check that each part carries out a piece of the idea; where one does not, change the idea or the part.

**Grounds**

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Start with a bird’s eye overview of the problem being solved."
- [Architecture](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md), rust-analyzer team, rust-analyzer repository, no date: "On the highest level, rust-analyzer is a thing which accepts input source code from the client and produces a structured semantic model of the code."
- [Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html), Fowler, martinfowler.com, 2026: "The key is to put the most important material at the start, and push details to later in the record."
- [1. Introduction and Goals](https://docs.arc42.org/section-1/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "If requirements documents exist this overview should refer to these documents."
- [4. Solution Strategy](https://docs.arc42.org/section-4/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "These decisions form the cornerstones for your architecture. They are the basis for many other detailed decisions or implementation rules."

### Q3: For anything the user stories need decided, can the builder point to the one role that decides it?

**Thinking**: Roles are cut so that each decision the stories need, above all one hard to make or likely to change, is made in one role alone and hidden from the others.

**Steps**

1. Draw an arrow for each thing one role asks of another, labelled with what it does and the data it hands on, not with a word such as "uses".
2. With the figure, write what each role alone decides that no arrow shows.
3. Ask of each decision which role makes it; where two roles or none answer, move the decision or split the role.

**Grounds**

- [On the Criteria to be Used in Decomposing Systems into Modules](https://prl.khoury.northeastern.edu/img/p-tr-1971.pdf), Parnas, Carnegie-Mellon University technical report, 1971: "We propose instead that one begins with a list of difficult design decisions or design decisions which are likely to change. Each module is then designed to hide such a decision from the others."
- [Component](https://c4model.com/abstractions/component), Brown, C4 model, c4model.com, no date: "in the C4 model, a component is a grouping of related functionality encapsulated behind a well-defined interface."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "Every line should be labelled, the label being consistent with the direction and intent of the relationship (e.g. dependency or data flow). Try to be as specific as possible with the label, ideally avoiding single words like, “Uses”."
- [Software architecture diagram review checklist](https://c4model.com/diagrams/checklist), Brown, C4 model, c4model.com, no date: "Do you understand what every element does?"

### Q4: Starting on a role, can the builder begin without choosing for themselves what kind of thing it is and what it is made with?

**Thinking**: Each role's box says what kind of thing it is and what it is made with, so the builder starts on it with nothing left to choose.

**Steps**

1. Add a legend that explains every shape, tag and other symbol the figure uses.
2. Read the figure without the text around it, and add to the legend or the boxes whatever the reader would still have to ask.

**Grounds**

- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "The type of every element should be explicitly specified (e.g. Person, Software System, Container or Component)."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "Every container and component should have a technology explicitly specified."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "Any notation used should be as self-describing as possible, but all diagrams should have a key/legend to make the notation explicit."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "A good way to think about this is to ask yourself whether each diagram can stand alone, and be (mostly) understood without a narrative."

### Q5: When one builder makes the role that writes a data and another makes the role that reads it, do both join it to the other data the same way?

**Thinking**: Each data the roles pass or keep is drawn once, by its name alone, with its fields left to where it is built, and each relation to another data is named with how many of each it joins.

**Steps**

1. For each relation, ask whether the role that writes it and the role that reads it would keep it the same way; where they would not, name the relation more exactly.

**Grounds**

- [Entity Relationship Diagrams](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), Mermaid, mermaid.js.org, no date: "Relationships between entities are represented by lines with end markers representing cardinality."
- [Entity Relationship Diagrams](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), Mermaid, mermaid.js.org, no date: "Cardinality is a property that describes how many elements of another entity can be related to the entity in question."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "Similar to the advice on APIs, and for the same reasons, copy-pasting complete schema definitions should be avoided."

### Q6: For each user story, can the builder follow it from the user's first request to its end, knowing at each step which role acts and what data it hands on?

**Thinking**: Each story is drawn as its steps in order, such as a sequence diagram, from the user's first request to what the story gives them, so every step has a role that takes it and data that it hands on.

**Steps**

1. Check that each step runs along an arrow of Components; where none does, add the arrow or give the step to another role.

**Grounds**

- [6. Runtime View](https://docs.arc42.org/section-6/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "The runtime view describes concrete behavior and interactions of the system’s building blocks in form of scenarios"
- [6. Runtime View](https://docs.arc42.org/section-6/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Always map existing building blocks to the activities within runtime scenarios!"
- [Dynamic diagram](https://c4model.com/diagrams/dynamic), Brown, C4 model, c4model.com, no date: "A dynamic diagram can be useful when you want to show how elements in the static model collaborate at runtime to implement a user story, use case, feature, etc."
- [Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html), Mermaid, mermaid.js.org, no date: "A Sequence diagram is an interaction diagram that shows how processes operate with one another and in what order."
- [Architectural Blueprints—The “4+1” View Model of Software Architecture](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf), Kruchten, IEEE Software, 1995: "as a validation and illustration role after this architecture design is complete, both on paper and as the starting point for the tests of an architectural prototype."

### Q7: Of any user story, role or data, can the builder tell which objective of the UX needs it?

**Thinking**: Every story, role and data is there because an objective of the UX needs it, on the main path a scenario shows or off it, so each can go once no objective needs it.

**Steps**

1. Trace each role and each data to the stories whose sequences reach it, and each story to the step of the UX it carries or, off the main path, to the key result it serves; remove what reaches none.

**Grounds**

- [Yagni](https://martinfowler.com/bliki/Yagni.html), Fowler, martinfowler.com, 2015: "The code for the presumptive feature adds some complexity to the software, this complexity makes it harder to modify and debug that software, thus increasing the cost of other features."

### Q8: When two builders of different parts meet a case the document does not name, does a principle's reason lead both to the same decision?

**Thinking**: A principle is a rule that every part meeting the same decision follows the same way, written with what it is there for, so a builder can carry it to a case it does not name.

**Steps**

1. Write as a rule also what must be absent, such as a dependency no role may have.
2. Link the principles of the architecture this one is built on, and write only what this product adds or changes.
3. Take a case no rule names, and have two builders of different parts decide it from the reasons alone; where they differ, sharpen the reason.

**Grounds**

- [8. Crosscutting Concepts](https://docs.arc42.org/section-8/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Such concepts are often related to multiple building blocks."
- [8. Crosscutting Concepts](https://docs.arc42.org/section-8/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "It might be easier to communicate or document such cross-cutting topics at a central location, instead of repeating them in the description of the concerned building blocks, hardware elements or development processes."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Explicitly call-out architectural invariants."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Often, important invariants are expressed as an absence of something, and it’s pretty hard to divine that from reading the code."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "For the most important decisions, you should record why you made them the way you did. You should also record the important or most likely alternatives you rejected and state why."
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can give Claude more information about your goals and help it deliver more targeted responses."
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Claude can generalize from the explanation."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "The most dangerous kind of ambiguity is undetected ambiguity. Here, each reader will think he or she understands the document, but unwittingly each reader will come to different conclusions about what it is saying."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "Each kind of information should be recorded in exactly one place."

### Q9: Setting the product up from nothing, can the builder put each role where it runs and each data where it is kept, and start the product, without asking anyone?

**Thinking**: Each role and each data is placed in a deployment unit within the environment where it runs or is kept, so the builder knows what it can reach, and how the product starts.

**Steps**

1. Draw each thing outside the product that the roles depend on, with an arrow saying what is used.
2. Leave out any infrastructure the parts do not need.
3. Check that each role and each data of Components sits in one unit.

**Grounds**

- [Deployment diagram](https://c4model.com/diagrams/deployment), Brown, C4 model, c4model.com, no date: "A deployment diagram allows you to illustrate how instances of software systems and/or containers in the static model are deployed on to the infrastructure within a given deployment environment (e.g. production, staging, development, etc)."
- [Deployment diagram](https://c4model.com/diagrams/deployment), Brown, C4 model, c4model.com, no date: "A deployment node represents where an instance of a software system/container is running"
- [7. Deployment View](https://docs.arc42.org/section-7/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Software does not run without hardware."
- [7. Deployment View](https://docs.arc42.org/section-7/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "From a software perspective it is sufficient to capture those elements of the infrastructure that are needed to show the deployment of your building blocks."

### Q10: Making or changing a role or a data, can the builder find the one place its files belong?

**Thinking**: The tree of the folders and files that hold the roles and the data, as they lie on disk, joins each role and each data to the one place where it is made, so the builder finds where to change it.

**Steps**

1. Keep the folders and files that hold a role or a data, and leave out what lies inside each.
2. Check that each role and each data stands on one line; where it stands on none or on two, move the files or the line.

**Grounds**

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "The codemap should answer “where’s the thing that does X?”."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Do name important files, modules, and types."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "A codemap is a map of a country, not an atlas of maps of its states."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Are the things you want to put near each other in the codemap adjacent when you run tree .?"

### Q11: Asked whether anything in the product goes untested, can the builder answer, for each deployment unit, which types of test cover it, how heavily, and why a type is missing?

**Thinking**: A table of each deployment unit against each scope of test, from narrow to wide, shows at a glance what is tested, how heavily, and why a gap is there.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that the wider tests are fewer, and that each user story is run end to end in some row.

**Grounds**

- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Write tests with different granularity"
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "The more high-level you get the fewer tests you should have"
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, chapter 11, abseil.io, 2020: "Scope refers to the specific code paths we are verifying."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "If the section is blank, the reader will wonder whether the information is coming later or whether it is indeed supposed to be blank."

### Q12: Writing a test of one type, can the builder do it without deciding for themselves what to make real, what to fake and when it passes?

**Thinking**: Each test type is set once, with what it makes real, what it fakes and when it passes, so every test of that type means the same to every builder.

**Steps**

1. Link the project's shared test rules, and write only where this product differs from them.
2. For a test whose result varies from run to run, write how many runs of how many must meet the expectation.
3. Use each type's name the same way throughout the document.

**Grounds**

- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "A unit test typically replaces external collaborators with test doubles"
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "For your automated tests this means you don't just need to run your own application but also the component you're integrating with."
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), Schwaber and Sutherland, scrumguides.org, 2020: "The Definition of Done is a formal description of the state of the Increment when it meets the quality measures required for the product."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "pass^k measures the probability that all k trials succeed."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Given the shortcomings of the original names it's totally okay to come up with other names for your test layers, as long as you keep it consistent within your codebase and your team's discussions."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "Each kind of information should be recorded in exactly one place."

### Q13: Following a principle while building a part, does the builder find every figure, list and table asking the same of that part, so they never have to choose which to follow?

**Thinking**: Each principle is read against every part it rules, so a builder never meets a figure, a list or a table that breaks one.

**Steps**

1. Read each part against each principle it rules; where a line breaks it, change the part, or the principle and its reason, until the two say the same.

**Grounds**

- [8. Crosscutting Concepts](https://docs.arc42.org/section-8/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Concepts form the basis for conceptual integrity (consistency, homogeneity) of the architecture."
- [Architectural Blueprints—The “4+1” View Model of Software Architecture](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf), Kruchten, IEEE Software, 1995: "A Software Design Guidelines, which captures (among other things) the most important design decisions that must be respected to maintain the architectural integrity of the system."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "Documentation that is incomplete or out of date does not reflect truth, does not obey its own rules for form and internal consistency, and is not used."

### Q14: When the builder doubts a choice the document makes, can they tell what would be lost by taking the other way?

**Thinking**: A choice a builder would question, such as a technology, a tool or a unit's weight, carries why it beat the other way and what it costs, beside the figure or table that shows it, so the builder keeps it or changes it knowing what it was for.

**Steps**

1. Read each figure and the table as a builder new to the product, and check that each choice they would question has its reason and its cost beside it.

**Grounds**

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "Without understanding the rationale or consequences, this person has only two choices:"
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "Blindly accept the decision."
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "Blindly change it."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "The design doc is the place to write down the trade-offs you made in designing your software."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "shows very explicitly why the selected solution is the best given the project goals and how other solutions, that the reader may be wondering about, introduce trade-offs that are less desirable given the goals."
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "All consequences should be listed here, not just the "positive" ones."
- [9. Architecture Decisions](https://docs.arc42.org/section-9/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Please use your judgement to decide whether an architectural decision should be documented here in this central section or whether you better document it locally (e.g. within the white box template of one building block). Avoid redundant texts."

### Q15: When the builder changes how a role works inside, while the UX and the principles stay, does every line of the document still hold?

**Thinking**: The document holds only what stays while the UX and the principles stay, and leaves how each role works inside to where it is built.

**Steps**

1. Imagine a change to how a role works inside, such as its steps, a value it uses or a data's fields, that leaves the UX and the principles as they are, and mark each line the change would make untrue.
2. Repeat with a change of another kind, until no line is marked.

**Grounds**

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "This is the main rule of thumb for ARCHITECTURE — only specify things that are unlikely to frequently change."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Avoid going into details of how each module works, pull this into separate documents or (better) inline documentation."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "A clear indicator that a doc might not be necessary are design docs that are really implementation manuals."
- [Software Architecture Guide](https://martinfowler.com/architecture/), Fowler, martinfowler.com, 2019: "It means that the heart of thinking architecturally about software is to decide what is important, (i.e. what is architectural), and then expend energy on keeping those architectural elements in good condition."
