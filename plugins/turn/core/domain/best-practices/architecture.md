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

### Q2: Having read the opening, can the developer say how the product delivers its UX, as one idea that every part carries out?

**Thinking**: The opening says how the product turns what the user brings into what the UX promises. It says this in one idea seen from above, with none of a part's inner workings. Every part after it then reads as a piece of that idea.

**Steps**

1. Link the UX instead of repeating it.
2. After writing the rest, check that each part carries out a piece of the idea. Where one does not, change the idea or the part.

### Q3: For anything the user stories need decided, can the developer point to the one role that decides it?

**Thinking**: The architecture cuts the roles so that one role alone makes each decision the stories need, above all a decision hard to make or likely to change. That role hides the decision from the others.

**Steps**

1. Draw an arrow for each thing one role asks of another, labelled with what it does and the data it hands on, not with a word such as "uses".
2. With the figure, write what each role alone decides that no arrow shows.
3. Ask of each decision which role makes it. Where two roles or none answer, move the decision or split the role.

### Q4: Starting on a role, can the developer begin without choosing for themselves what kind of thing it is and what it is made with?

**Thinking**: Each role's box says what kind of thing it is and what it is made with. The developer then starts on it with nothing left to choose.

**Steps**

1. Add a legend that explains every shape, tag and other symbol the figure uses.
2. Read the figure without the text around it, and add to the legend or the boxes whatever the reader would still have to ask.

### Q5: When one developer makes the role that writes a data and another makes the role that reads it, do both join it to the other data the same way?

**Thinking**: The data model draws each data that the roles pass or keep once, by its name alone. It leaves the data's fields to where the data is built. It names each relation to another data, with how many of each the relation joins.

**Steps**

1. For each relation, ask whether the role that writes it and the role that reads it would keep it the same way. Where they would not, name the relation more exactly.

### Q6: For each user story, can the developer follow it from the user's first request to its end, knowing at each step which role acts and what data it hands on?

**Thinking**: The sequences draw each story as its steps in order, such as in a sequence diagram, from the user's first request to what the story gives them. In the drawing, every step has a role that takes it and data that it hands on.

**Steps**

1. Check that each step runs along an arrow of Components. Where none does, add the arrow or give the step to another role.

### Q7: Of any user story, role or data, can the developer tell which objective of the UX needs it?

**Thinking**: Every story, role and data is there because an objective of the UX needs it, on the main path that a scenario shows or off it. So each can go once no objective needs it.

**Steps**

1. Trace each role and each data to the stories whose sequences reach it. Trace each story to the step of the UX it carries or, off the main path, to the key result it serves. Remove what reaches none.

### Q8: When two developers of different parts meet a case the document does not name, does a principle's reason lead both to the same decision?

**Thinking**: A principle is a rule that every part meeting the same decision follows the same way. The principle says what it is there for, so a developer can carry it to a case it does not name.

**Steps**

1. Write as a rule also what must be absent, such as a dependency no role may have.
2. Link the principles of the architecture this one is built on, and write only what this product adds or changes.
3. Take a case no rule names, and have two developers of different parts decide it from the reasons alone. Where they differ, sharpen the reason.

### Q9: Setting the product up from nothing, can the developer put each role where it runs and each data where it is kept, and start the product, without asking anyone?

**Thinking**: Deployment places each role and each data in a deployment unit, within the environment where the role runs or the data is kept. The developer then knows what each can reach, and how the product starts.

**Steps**

1. Draw each thing outside the product that the roles depend on, with an arrow saying what is used.
2. Leave out any infrastructure the parts do not need.
3. Check that each role and each data of Components sits in one unit.

### Q10: Making or changing a role or a data, can the developer find the one place its files belong?

**Thinking**: The tree shows the folders and files that hold the roles and the data, as they lie on disk. It joins each role and each data to the one place where it is made. The developer then finds where to change it.

**Steps**

1. Keep the folders and files that hold a role or a data, and leave out what lies inside each.
2. Check that each role and each data stands on one line. Where it stands on none or on two, move the files or the line.

### Q11: Asked whether anything in the product goes untested, can the developer answer, for each deployment unit, which levels of test cover it, how heavily, and why a level is missing?

**Thinking**: Each level checks against one thing: a part's contract, this document's sequences or the UX. So each level whose thing says what a deployment unit must do tests that unit. A cell is empty only where that thing says nothing of the unit. The document names a level by that thing, not by its means, as a means such as end to end can serve any level.

**Steps**

1. Leave out a unit whose every cell would be empty, and say why under the table.
2. Check that unit and architecture carry most of the checking and run on every change, and that ux tests are few.
3. Check that each user story's sequence runs from start to end at the architecture level in some row.

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

### Q13: When the unit and architecture tests pass, can the developer be sure the product does what this document says, leaving ux only to confirm the UX?

**Thinking**: The design is the paths its sequences draw, joined by what each part promises. Unit tests show that each real part keeps its promise. Architecture tests show that every path holds with doubles that keep only those promises. Together, the two show that every path holds for the real parts. That leaves to ux tests only what real size shows, such as lead time.

**Steps**

1. Build each double from the form that the part's contract gives its results. Set it only to results that this form allows, the refusals among them.
2. Check each double's results by the same check the part's unit tests make of the part's results, so a change to the contract fails the double as it fails the part.
3. For a fault a higher level finds, name the case or the path the lower level missed, add its test at the level that must catch it, see it fail, then fix the fault there.

### Q14: Following a principle while building a part, does the developer find every figure, list and table asking the same of that part, so they never have to choose which to follow?

**Thinking**: The writer reads each principle against every part it rules. A developer then never meets a figure, a list or a table that breaks a principle.

**Steps**

1. Read each part against each principle that rules it. Where a line breaks the principle, change the part, or the principle and its reason, until the two say the same.

### Q15: When the developer doubts a choice the document makes, can they tell what would be lost by taking the other way?

**Thinking**: A choice that a developer would question, such as a technology, a tool or a unit's weight, carries why it beat the other way and what it costs. These stand beside the figure or table that shows the choice. The developer then keeps the choice or changes it, knowing what it was for.

**Steps**

1. Read each figure and the table as a developer new to the product, and check that each choice they would question has its reason and its cost beside it.

### Q16: When the developer changes how a role works inside, while the UX and the principles stay, does every line of the document still hold?

**Thinking**: The document holds only what stays while the UX and the principles stay. It leaves how each role works inside to where the role is built.

**Steps**

1. Imagine a change to how a role works inside, such as its steps, a value it uses or a data's fields, that leaves the UX and the principles as they are. Mark each line the change would make untrue.
2. Repeat with a change of another kind, until no line is marked.
