# architecture

## Goal

Whoever builds or changes the product, a person or an AI, makes each part without hesitating, on the same thinking as every other part. Together, the parts then deliver the UX. The product stays easy to read and to change.

## Parts

- **summary**: The opening: which product the document is for, and a sentence or two that say how the product delivers its UX. These sentences point to the UX instead of repeating it.
- **principles**: The principles. Where this architecture builds on another, a pointer to that one's principles comes first. Each principle has a short name the reader finds it by, its rule and its reason. The rule is one sentence that the developer builds every part by. The reason says what the rule is there for, and what goes wrong for the user or the developer without it.
- **user-stories**: The user stories: one for each way the user uses the product at its edge, such as a command they run. Each story names the user, that way, and the UX's scenarios or steps that rest on it.
- **components**: A figure of the roles the user stories need and of each store of data. The reader understands it without the text around it. Each element holds its name, its type and its technology, such as a web app in React and TypeScript or a database in PostgreSQL, and nothing more. Each arrow says what one element does to another, with the data it hands on, named as in the data model. Where it matters, the arrow also gives the protocol, such as HTTPS with JSON. A legend explains every symbol the figure uses. The figure lays out the arrows so the reader follows them in the order they act.
- **responsibilities**: Read with the components figure: what each role alone is responsible for that no arrow shows.
- **choices**: For each choice the reader would question, such as a technology or a tool: why it beat the other way. This stands where the reader meets the choice.
- **data-model**: A figure of each data the roles pass or keep, and of each relation between two data. Each data shows its name alone. Each relation shows its name, and at both ends how many of each it joins, such as one to many.
- **sequences**: For each user story, its steps in the order they happen, with each branch, each step that sends work back to an earlier one and each question put to the caller or the person. The drawing lets the reader follow the steps from first to last. It shows the user, each role the story reaches, named as in Components, and each thing outside the product that the story reaches. It also shows each step, labelled in a few words with what one does to another and the data handed on, named as in the data model.
- **deployment**: A figure of each execution environment, such as a cloud service, a phone, the user's computer or CI, with its technology. Each environment holds its deployment units, such as an app or a container. Each unit shows its technology, and, by their names in Components, the roles that run in it and the data kept in it. The figure shows each thing outside the product that the roles depend on, with what they use of it. With the figure: how to start the product, and choices.
- **directory**: The place where each role and each data lies: the folders and files that hold them, nested as on disk. Each names the role or the data it holds as Components names it, with its technology. The tree leaves out the files inside a role.
- **test-table**: A table the reader takes in at a glance. It has a row for each deployment unit, named as in Deployment, with its technology. It has a column for each test level, from narrow to wide, each named by what its tests check against. The unit level checks one part against its contract, which says what the part promises. The architecture level joins all the parts and checks them against this document. It runs every user story's sequence from start to end. The ux level checks the product in real use against the UX. Each cell holds the tool, a weight, such as ●●● or ●●○, and what it checks in a few words. Each empty cell says that it is empty, and why. The table also names the units left out because every cell of their row would be empty, with why.
- **test-rules**: For each test level: what it runs real, what doubles stand in for, who stands in for the person, what it covers and when it passes. A double stands in for a part and gives set results. The test rules also say where each double's results come from, and how the developer brings a fault that one level finds to the level that must catch it. For a result that varies from run to run, they say how many runs of how many must meet the expectation. They give each unit's weight, with what a failure costs the user. Before the table, they point to the project's shared test rules, and write only what differs from them.

## User benefits

- **Q1** (user-stories): For each step of the UX's scenarios, can the developer name the one way of using the product at its edge that carries it?
- **Q2** (summary): Having read the opening, can the developer say how the product delivers its UX, as one idea that every part carries out?
- **Q3** (user-stories, components, responsibilities): For anything the user stories need decided, can the developer point to the one role that decides it?
- **Q4** (components): Starting on a role, can the developer begin without choosing for themselves what kind of thing it is and what it is made with?
- **Q5** (data-model): When one developer makes the role that writes a data and another makes the role that reads it, do both join it to the other data the same way?
- **Q6** (user-stories, components, data-model, sequences): For each user story, can the developer follow it from the user's first request to its end, knowing at each step which role acts and what data it hands on?
- **Q7** (user-stories, components, responsibilities, data-model, sequences): Of any user story, role or data, can the developer tell which objective of the UX needs it?
- **Q8** (principles): When two developers of different parts meet a case the document does not name, does a principle's reason lead both to the same decision?
- **Q9** (components, data-model, deployment): Setting the product up from nothing, can the developer put each role where it runs and each data where it is kept, and start the product, without asking anyone?
- **Q10** (components, data-model, directory): Making or changing a role or a data, can the developer find the one place its files belong?
- **Q11** (deployment, test-table): Asked whether anything in the product goes untested, can the developer answer, for each deployment unit, which levels of test cover it, how heavily, and why a level is missing?
- **Q12** (test-table, test-rules): Writing a test at one level, can the developer do it without deciding for themselves what to run real, what to stand in with a double, what to cover and when it passes?
- **Q13** (test-table, test-rules): When the unit and architecture tests pass, can the developer be sure the product does what this document says, leaving ux only to confirm the UX?
- **Q14** (principles, components, responsibilities, sequences, deployment, directory, test-table, test-rules): Following a principle while building a part, does the developer find every figure, list and table asking the same of that part, so they never have to choose which to follow?
- **Q15** (choices, test-rules): When the developer doubts a choice the document makes, can they tell what would be lost by taking the other way?
- **Q16** (the whole): When the developer changes how a role works inside, while the UX and the principles stay, does every line of the document still hold?

## Practices

### Q1: For each step of the UX's scenarios, can the developer name the one way of using the product at its edge that carries it?

**Thinking**: A user story is one way the user meets the product at its edge, such as one command or one call. Together, the stories carry every step of the UX where the user meets the product.

**Steps**

1. Write each story naming the user, the way and the scenarios or steps it carries, such as "As <the user>, I want <the way>. Carries <the scenarios or steps>."
2. Walk each scenario of the UX step by step. Check that one story carries each step where the user, a person or an AI, meets the product. Add a story for a step that none carries.

**Grounds**

- [3. Context and Scope](https://docs.arc42.org/section-3/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "System scope and context - as the name suggests - delimits your system (i.e. your scope) from all its communication partners (neighboring systems and users, i.e. the context of your system)."
- [User Stories: What They Are, How to Write Them, and Examples](https://www.mountaingoatsoftware.com/agile/user-stories), Mountain Goat Software, mountaingoatsoftware.com, 2026: "A common template is: As a [type of user], I [need/want/am required] to [do something], so that [reason or benefit]."
- [Architectural Blueprints—The “4+1” View Model of Software Architecture](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf), Kruchten, IEEE Software, 1995: "as a driver to discover the architectural elements during the architecture design as we will describe later"

### Q2: Having read the opening, can the developer say how the product delivers its UX, as one idea that every part carries out?

**Thinking**: The opening says how the product turns what the user brings into what the UX promises. It says this in one idea seen from above, with none of a part's inner workings. Every part after it then reads as a piece of that idea.

**Steps**

1. Link the UX instead of repeating it.
2. After writing the rest, check that each part carries out a piece of the idea. Where one does not, change the idea or the part.

**Grounds**

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Start with a bird’s eye overview of the problem being solved."
- [Architecture](https://github.com/rust-lang/rust-analyzer/blob/master/docs/book/src/contributing/architecture.md), rust-analyzer team, rust-analyzer repository, no date: "On the highest level, rust-analyzer is a thing which accepts input source code from the client and produces a structured semantic model of the code."
- [Architecture Decision Record](https://martinfowler.com/bliki/ArchitectureDecisionRecord.html), Fowler, martinfowler.com, 2026: "The key is to put the most important material at the start, and push details to later in the record."
- [1. Introduction and Goals](https://docs.arc42.org/section-1/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "If requirements documents exist this overview should refer to these documents."
- [4. Solution Strategy](https://docs.arc42.org/section-4/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "These decisions form the cornerstones for your architecture. They are the basis for many other detailed decisions or implementation rules."

### Q3: For anything the user stories need decided, can the developer point to the one role that decides it?

**Thinking**: The architecture cuts the roles so that one role alone makes each decision the stories need, above all a decision hard to make or likely to change. That role hides the decision from the others.

**Steps**

1. Draw an arrow for each thing one role asks of another, labelled with what it does and the data it hands on, not with a word such as "uses".
2. With the figure, write what each role alone decides that no arrow shows.
3. Ask of each decision which role makes it. Where two roles or none answer, move the decision or split the role.

**Grounds**

- [On the Criteria to be Used in Decomposing Systems into Modules](https://prl.khoury.northeastern.edu/img/p-tr-1971.pdf), Parnas, Carnegie-Mellon University technical report, 1971: "We propose instead that one begins with a list of difficult design decisions or design decisions which are likely to change. Each module is then designed to hide such a decision from the others."
- [Component](https://c4model.com/abstractions/component), Brown, C4 model, c4model.com, no date: "in the C4 model, a component is a grouping of related functionality encapsulated behind a well-defined interface."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "Every line should be labelled, the label being consistent with the direction and intent of the relationship (e.g. dependency or data flow). Try to be as specific as possible with the label, ideally avoiding single words like, “Uses”."
- [Software architecture diagram review checklist](https://c4model.com/diagrams/checklist), Brown, C4 model, c4model.com, no date: "Do you understand what every element does?"

### Q4: Starting on a role, can the developer begin without choosing for themselves what kind of thing it is and what it is made with?

**Thinking**: Each role's box says what kind of thing it is and what it is made with. The developer then starts on it with nothing left to choose.

**Steps**

1. Add a legend that explains every shape, tag and other symbol the figure uses.
2. Read the figure without the text around it, and add to the legend or the boxes whatever the reader would still have to ask.

**Grounds**

- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "The type of every element should be explicitly specified (e.g. Person, Software System, Container or Component)."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "Every container and component should have a technology explicitly specified."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "Any notation used should be as self-describing as possible, but all diagrams should have a key/legend to make the notation explicit."
- [Notation](https://c4model.com/diagrams/notation), Brown, C4 model, c4model.com, no date: "A good way to think about this is to ask yourself whether each diagram can stand alone, and be (mostly) understood without a narrative."

### Q5: When one developer makes the role that writes a data and another makes the role that reads it, do both join it to the other data the same way?

**Thinking**: The data model draws each data that the roles pass or keep once, by its name alone. It leaves the data's fields to where the data is built. It names each relation to another data, with how many of each the relation joins.

**Steps**

1. For each relation, ask whether the role that writes it and the role that reads it would keep it the same way. Where they would not, name the relation more exactly.

**Grounds**

- [Entity Relationship Diagrams](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), Mermaid, mermaid.js.org, no date: "Relationships between entities are represented by lines with end markers representing cardinality."
- [Entity Relationship Diagrams](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), Mermaid, mermaid.js.org, no date: "Cardinality is a property that describes how many elements of another entity can be related to the entity in question."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "Similar to the advice on APIs, and for the same reasons, copy-pasting complete schema definitions should be avoided."

### Q6: For each user story, can the developer follow it from the user's first request to its end, knowing at each step which role acts and what data it hands on?

**Thinking**: The sequences draw each story as its steps in order, such as in a sequence diagram, from the user's first request to what the story gives them. In the drawing, every step has a role that takes it and data that it hands on.

**Steps**

1. Check that each step runs along an arrow of Components. Where none does, add the arrow or give the step to another role.

**Grounds**

- [6. Runtime View](https://docs.arc42.org/section-6/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "The runtime view describes concrete behavior and interactions of the system’s building blocks in form of scenarios"
- [6. Runtime View](https://docs.arc42.org/section-6/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Always map existing building blocks to the activities within runtime scenarios!"
- [Dynamic diagram](https://c4model.com/diagrams/dynamic), Brown, C4 model, c4model.com, no date: "A dynamic diagram can be useful when you want to show how elements in the static model collaborate at runtime to implement a user story, use case, feature, etc."
- [Sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html), Mermaid, mermaid.js.org, no date: "A Sequence diagram is an interaction diagram that shows how processes operate with one another and in what order."
- [Architectural Blueprints—The “4+1” View Model of Software Architecture](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf), Kruchten, IEEE Software, 1995: "as a validation and illustration role after this architecture design is complete, both on paper and as the starting point for the tests of an architectural prototype."

### Q7: Of any user story, role or data, can the developer tell which objective of the UX needs it?

**Thinking**: Every story, role and data is there because an objective of the UX needs it, on the main path that a scenario shows or off it. So each can go once no objective needs it.

**Steps**

1. Trace each role and each data to the stories whose sequences reach it. Trace each story to the step of the UX it carries or, off the main path, to the key result it serves. Remove what reaches none.

**Grounds**

- [Yagni](https://martinfowler.com/bliki/Yagni.html), Fowler, martinfowler.com, 2015: "The code for the presumptive feature adds some complexity to the software, this complexity makes it harder to modify and debug that software, thus increasing the cost of other features."

### Q8: When two developers of different parts meet a case the document does not name, does a principle's reason lead both to the same decision?

**Thinking**: A principle is a rule that every part meeting the same decision follows the same way. The principle says what it is there for, so a developer can carry it to a case it does not name.

**Steps**

1. Write as a rule also what must be absent, such as a dependency no role may have.
2. Link the principles of the architecture this one is built on, and write only what this product adds or changes.
3. Take a case no rule names, and have two developers of different parts decide it from the reasons alone. Where they differ, sharpen the reason.

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

### Q9: Setting the product up from nothing, can the developer put each role where it runs and each data where it is kept, and start the product, without asking anyone?

**Thinking**: Deployment places each role and each data in a deployment unit, within the environment where the role runs or the data is kept. The developer then knows what each can reach, and how the product starts.

**Steps**

1. Draw each thing outside the product that the roles depend on, with an arrow saying what is used.
2. Leave out any infrastructure the parts do not need.
3. Check that each role and each data of Components sits in one unit.

**Grounds**

- [Deployment diagram](https://c4model.com/diagrams/deployment), Brown, C4 model, c4model.com, no date: "A deployment diagram allows you to illustrate how instances of software systems and/or containers in the static model are deployed on to the infrastructure within a given deployment environment (e.g. production, staging, development, etc)."
- [Deployment diagram](https://c4model.com/diagrams/deployment), Brown, C4 model, c4model.com, no date: "A deployment node represents where an instance of a software system/container is running"
- [7. Deployment View](https://docs.arc42.org/section-7/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Software does not run without hardware."
- [7. Deployment View](https://docs.arc42.org/section-7/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "From a software perspective it is sufficient to capture those elements of the infrastructure that are needed to show the deployment of your building blocks."

### Q10: Making or changing a role or a data, can the developer find the one place its files belong?

**Thinking**: The tree shows the folders and files that hold the roles and the data, as they lie on disk. It joins each role and each data to the one place where it is made. The developer then finds where to change it.

**Steps**

1. Keep the folders and files that hold a role or a data, and leave out what lies inside each.
2. Check that each role and each data stands on one line. Where it stands on none or on two, move the files or the line.

**Grounds**

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "The codemap should answer “where’s the thing that does X?”."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Do name important files, modules, and types."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "A codemap is a map of a country, not an atlas of maps of its states."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Are the things you want to put near each other in the codemap adjacent when you run tree .?"

### Q11: Asked whether anything in the product goes untested, can the developer answer, for each deployment unit, which levels of test cover it, how heavily, and why a level is missing?

**Thinking**: Each level checks against one thing: a part's contract, this document's sequences or the UX. So each level whose thing says what a deployment unit must do tests that unit. A cell is empty only where that thing says nothing of the unit. The document names a level by that thing, not by its means, as a means such as end to end can serve any level.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that unit and architecture carry most of the checking and run on every change, and that ux tests are few.
3. Check that each user story's sequence runs from start to end at the architecture level in some row.

**Grounds**

- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Test levels are distinguished by the following non-exhaustive list of attributes, to avoid overlapping of test activities"
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Test analysis includes analyzing the test basis to identify testable features."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Test types are groups of test activities related to specific quality characteristics and most of those test activities can be performed at every test level."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "While testing involves verification, i.e., checking whether the system meets specified requirements, it also involves validation, which means checking whether the system meets users’ and other stakeholders’ needs in its operational environment."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Write tests with different granularity"
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Push your tests as far down the test pyramid as you can"
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "The more high-level you get the fewer tests you should have"
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "If the section is blank, the reader will wonder whether the information is coming later or whether it is indeed supposed to be blank."

### Q12: Writing a test at one level, can the developer do it without deciding for themselves what to run real, what to stand in with a double, what to cover and when it passes?

**Thinking**: The developer does not choose a test but draws it from the one thing its level checks against: the ways a part's contract divides, the paths the sequences draw, or an objective's scenario at the size of a real request. Only that thing runs real, and stand-ins take the place of the rest. A failing test then names the rule, path or scenario it breaks.

**Steps**

1. Link the project's shared test rules, and write only where this product differs from them.
2. At unit, divide each input and each result the contract names into classes that the part treats alike, the ones it refuses among them. Write one test for each class.
3. Where a class ends on an ordered scale, such as a length or a count, write one test at each end and one at the nearest value in the next class.
4. Where the contract's result turns on a combination of conditions, write a table with one rule for each combination that can occur and the result it gives. Write one test for each rule.
5. Put doubles in place of the parts that the part works with, and a stand-in in place of the person. Run a part that an AI does on the real model, with one input for each class and each rule, both where the contract says the part acts and where it says it does not.
6. At architecture, run real what joins the parts, such as the hooks, the scripts and the rules laid. Put a double in place of each role an AI runs and each thing outside the product. The level then calls no model, runs fast and gives the same result each run.
7. For each user story, list the paths through its sequence: the main flow first, then each branch, each step that sends work back to an earlier one, and each question put to the caller or the person. Go on until every move from one step to the next lies on some path. Write one test for each path, and check at each step the role that acts and the data it hands on.
8. At ux, once unit and architecture pass, run the real product on each objective's scenario, on a subject the size of a real request, without aiming to cover every case.
9. Give the AI that stands in for the person an intent that you write before the run and never show to the product. A run passes when the stand-in gets what the objective says.
10. For each key result, say what the test measures, such as the lead time from the request to the result. The UX gives a key result no target value, so set each measure against the last one by the direction the UX gives it.
11. For a test whose result varies from run to run, write how many runs of how many must meet the expectation.
12. Use each level's name the same way throughout the document.

**Grounds**

- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Black-box test techniques (also known as specification-based techniques) are based on an analysis of the specified behavior of the test object without reference to its internal structure."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Test techniques help to develop a relatively small, but sufficient, set of test cases in a systematic way."
- [Unit Testing](https://abseil.io/resources/swe-book/html/ch12.html), Kuefler, Software Engineering at Google, chapter 12, abseil.io, 2020: "A behavior is any guarantee that a system makes about how it will respond to a series of inputs while in a particular state."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "A unit test typically replaces external collaborators with test doubles"
- [Testing Overview](https://abseil.io/resources/swe-book/html/ch11.html), Bender, Software Engineering at Google, chapter 11, abseil.io, 2020: "the most important qualities we want from our test suite are speed and determinism, regardless of the scope of the test."
- [Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html), Graves, Software Engineering at Google, chapter 14, abseil.io, 2020: "The primary reason larger tests exist is to address fidelity."
- [Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html), Graves, Software Engineering at Google, chapter 14, abseil.io, 2020: "Tests can also be measured in terms of how faithful the test content is to reality."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Make sure that the higher-level test focuses on the part that the lower-level tests couldn't cover."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Therefore, one test for each partition is sufficient."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "To achieve 100% coverage with this test technique, test cases must exercise all identified partitions (including invalid partitions) by covering each partition at least once."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "BVA focuses on the boundary values of the partitions because developers are more likely to make errors with these boundary values."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "In 2-value BVA (Craig 2002, Myers 2011), for each boundary value there are two coverage items: this boundary value and its closest neighbor belonging to the adjacent partition."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Decision tables are used for testing the implementation of requirements that specify how different combinations of conditions result in different outcomes."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "In decision table testing, the coverage items are the columns containing feasible combinations of conditions."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "Test both the cases where a behavior should occur and where it shouldn't."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "A test case based on a state diagram or state table is usually represented as a sequence of events, which results in a sequence of state changes (and actions, if needed)."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Valid transitions coverage is the most widely used coverage criterion."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Typically, the first test cases are positive, confirming the correct behavior without exceptions or error conditions, and comprising the sequence of activities executed if everything goes as expected."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "After the positive test cases are done, the team should perform negative testing."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "In sequential SDLC models, the test levels are often defined such that the exit criteria of one level are part of the entry criteria for the next level."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "Acceptance testing focuses on validation and on demonstrating readiness for deployment, which means that the system fulfills the user’s business needs."
- [Certified Tester Foundation Level Syllabus](https://www.istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf), ISTQB, version 4.0.1, istqb.org, 2024: "For some non-functional quality characteristics, it is preferable to test them on a complete system in a representative test environment (e.g., usability)."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "Unlike most other evals, they often require a second LLM to simulate the user."
- [𝜏-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/html/2406.12045v1), Yao et al., arXiv:2406.12045, 2024: "Task annotation is not visible to the agent and is used only for user simulation and evaluation."
- [𝜏-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/html/2406.12045v1), Yao et al., arXiv:2406.12045, 2024: "The instruction sets up user identity, intent, and preferences in a way that guarantees only one possible outcome under the domain policy."
- [The Scrum Guide](https://scrumguides.org/scrum-guide.html), Schwaber and Sutherland, scrumguides.org, 2020: "The Definition of Done is a formal description of the state of the Increment when it meets the quality measures required for the product."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "pass^k measures the probability that all k trials succeed."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Given the shortcomings of the original names it's totally okay to come up with other names for your test layers, as long as you keep it consistent within your codebase and your team's discussions."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "Each kind of information should be recorded in exactly one place."

### Q13: When the unit and architecture tests pass, can the developer be sure the product does what this document says, leaving ux only to confirm the UX?

**Thinking**: The design is the paths its sequences draw, joined by what each part promises. Unit tests show that each real part keeps its promise. Architecture tests show that every path holds with doubles that keep only those promises. Together, the two show that every path holds for the real parts. That leaves to ux tests only what real size shows, such as lead time.

**Steps**

1. Build each double from the form that the part's contract gives its results. Set it only to results that this form allows, the refusals among them.
2. Check each double's results by the same check the part's unit tests make of the part's results, so a change to the contract fails the double as it fails the part.
3. For a fault a higher level finds, name the case or the path the lower level missed, add its test at the level that must catch it, see it fail, then fix the fault there.

**Grounds**

- [Test Doubles](https://abseil.io/resources/swe-book/html/ch13.html), Trenk and Bly, Software Engineering at Google, chapter 13, abseil.io, 2020: "Fidelity refers to how closely the behavior of a test double resembles the behavior of the real implementation that it’s replacing."
- [Test Doubles](https://abseil.io/resources/swe-book/html/ch13.html), Trenk and Bly, Software Engineering at Google, chapter 13, abseil.io, 2020: "These test doubles are very likely to exhibit behavior that violates the API contract of the type being mocked—for instance, returning null for a method that can never return null."
- [Contract Test](https://martinfowler.com/bliki/ContractTest.html), Fowler, martinfowler.com, 2011: "Contract tests check the contract of external service calls, but not necessarily the exact data."
- [Contract Test](https://martinfowler.com/bliki/ContractTest.html), Fowler, martinfowler.com, 2011: "These check that all the calls against your test doubles return the same results as a call to the external service would."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "Running contract tests against the fake and the real server ensures that the fake we use in our integration tests is a faithful test double."
- [Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html), Graves, Software Engineering at Google, chapter 14, abseil.io, 2020: "Moreover, mocks become stale."
- [Larger Testing](https://abseil.io/resources/swe-book/html/ch14.html), Graves, Software Engineering at Google, chapter 14, abseil.io, 2020: "Then, the real service uses this input/output pair in a real test to ensure that it produces that output given those inputs."
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "If a higher-level test spots an error and there's no lower-level test failing, you need to write a lower-level test"
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), Vocke, martinfowler.com, 2018: "The first rule is important because lower-level tests allow you to better narrow down errors and replicate them in an isolated way."

### Q14: Following a principle while building a part, does the developer find every figure, list and table asking the same of that part, so they never have to choose which to follow?

**Thinking**: The writer reads each principle against every part it rules. A developer then never meets a figure, a list or a table that breaks a principle.

**Steps**

1. Read each part against each principle that rules it. Where a line breaks the principle, change the part, or the principle and its reason, until the two say the same.

**Grounds**

- [8. Crosscutting Concepts](https://docs.arc42.org/section-8/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Concepts form the basis for conceptual integrity (consistency, homogeneity) of the architecture."
- [Architectural Blueprints—The “4+1” View Model of Software Architecture](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf), Kruchten, IEEE Software, 1995: "A Software Design Guidelines, which captures (among other things) the most important design decisions that must be respected to maintain the architectural integrity of the system."
- [Documenting Software Architectures: Views and Beyond](https://www.informit.com/articles/article.aspx?p=1641654&seqNum=5), Clements et al., 2nd edition, section P.5, informit.com, 2010: "Documentation that is incomplete or out of date does not reflect truth, does not obey its own rules for form and internal consistency, and is not used."

### Q15: When the developer doubts a choice the document makes, can they tell what would be lost by taking the other way?

**Thinking**: A choice that a developer would question, such as a technology, a tool or a unit's weight, carries why it beat the other way and what it costs. These stand beside the figure or table that shows the choice. The developer then keeps the choice or changes it, knowing what it was for.

**Steps**

1. Read each figure and the table as a developer new to the product, and check that each choice they would question has its reason and its cost beside it.

**Grounds**

- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "Without understanding the rationale or consequences, this person has only two choices:"
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "Blindly accept the decision."
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "Blindly change it."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "The design doc is the place to write down the trade-offs you made in designing your software."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "shows very explicitly why the selected solution is the best given the project goals and how other solutions, that the reader may be wondering about, introduce trade-offs that are less desirable given the goals."
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), Nygard, Cognitect blog, 2011: "All consequences should be listed here, not just the "positive" ones."
- [9. Architecture Decisions](https://docs.arc42.org/section-9/), Hruschka and Starke, arc42 documentation, docs.arc42.org, no date: "Please use your judgement to decide whether an architectural decision should be documented here in this central section or whether you better document it locally (e.g. within the white box template of one building block). Avoid redundant texts."

### Q16: When the developer changes how a role works inside, while the UX and the principles stay, does every line of the document still hold?

**Thinking**: The document holds only what stays while the UX and the principles stay. It leaves how each role works inside to where the role is built.

**Steps**

1. Imagine a change to how a role works inside, such as its steps, a value it uses or a data's fields, that leaves the UX and the principles as they are. Mark each line the change would make untrue.
2. Repeat with a change of another kind, until no line is marked.

**Grounds**

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "This is the main rule of thumb for ARCHITECTURE — only specify things that are unlikely to frequently change."
- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html), matklad, matklad.github.io, 2021: "Avoid going into details of how each module works, pull this into separate documents or (better) inline documentation."
- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/), Ubl, industrialempathy.com, 2020: "A clear indicator that a doc might not be necessary are design docs that are really implementation manuals."
- [Software Architecture Guide](https://martinfowler.com/architecture/), Fowler, martinfowler.com, 2019: "It means that the heart of thinking architecturally about software is to decide what is important, (i.e. what is architectural), and then expend energy on keeping those architectural elements in good condition."
