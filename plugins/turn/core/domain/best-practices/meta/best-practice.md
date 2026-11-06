# meta

## Goal

The generator can make deliverables with which their role achieves its purpose.

## Template

[template.json](template.json)

## Example

[../product-vision/best-practice.json](../product-vision/best-practice.json)

## Intents

- **Q1** (goal): Reading the goal, does the generator see the one end the deliverable's role is after, so that every part of the deliverable serves that end?
- **Q2** (template): Filling in the template, does the generator know what each section holds and in what order, so that the deliverable holds what its role uses and nothing more?
- **Q3** (goal, template): Setting the template against the goal, does the generator find each section the goal needs and none it does not, so that the role finds all it needs and reads nothing it does not?
- **Q4** (intents): Judging a deliverable by a question, does the evaluator see what the role is after at that moment, so that it judges whether the role gets that, not whether the words are there?
- **Q5** (template, intents): Going through the template, does the generator find a question for each section, each dependency among sections and the whole, so that no way the deliverable fails its role goes unasked?
- **Q6** (practices): Following a practice, does the generator grasp what the question's role is after and why, so that it makes what serves the role even where no step says how?
- **Q7** (intents, practices): Going through the questions in order, does the generator find a practice for each, so that it meets no question with nothing to go by?
- **Q8** (example, source): Reading the example, does the generator see what the template's slots become in one deliverable, so that it fills its own to the same intent?
- **Q9** (the whole): Using a deliverable made by the best practice and passed, does its role achieve its purpose?

## Practices

### Q1: Reading the goal, does the generator see the one end the deliverable's role is after, so that every part of the deliverable serves that end?

**Thinking**: Write the end the deliverable's role is after as one sentence, with the role as its subject. Leave out what the deliverable holds, how the end is reached and how it would show. Each of these can be met while the end is missed.

**Steps**

1. Ask why of each part of the sentence until no further end shows, and keep that end.

### Q2: Filling in the template, does the generator know what each section holds and in what order, so that the deliverable holds what its role uses and nothing more?

**Thinking**: Write the template anew from the goal: a section for each thing the role uses toward the goal, fixed text for what every deliverable of the kind shares, and a slot for the rest. An AI writes past what a deliverable needs when it is only told not to, so the template leaves no room for more.

**Steps**

1. Where what the good deliverables hold is one way of doing it, such as a place, a file or a name, keep what the role gets from it instead.
2. Mark each slot as code, `` `<name>` ``, as a bare `<name>` is dropped as an HTML tag where the template is shown.
3. After each section, write one GitHub note whose first line is `DELETE_TEMPLATE_COMMENT:`, saying for each slot what it holds, what its reader uses it for and whether it is optional, as the generator fills a slot to its intent only when the note says it, and finds and deletes each note by its marker.
4. Where the deliverable is JSON, write each note as a key `DELETE_TEMPLATE_COMMENT`, as JSON holds no comment.
5. Give the content found by digging a slot for its intent and why alone, in the fewest words, and a figure in place of prose wherever a figure can say it.
6. Draw a sequence in Mermaid, and any other figure in SVG, a table among them, as a table stands in for prose.
7. Give each SVG figure of the template a skeleton of its own beside it, `images/template-<name>.svg`, that shows the figure's layout by the slots' names, give it an alt text with no slot, and say in the section's note where the deliverable puts its own figure, as a figure the template names but does not hold shows broken, and the example's figure shows one product's content in place of the layout.
8. Name the template's file in `template`.

### Q3: Setting the template against the goal, does the generator find each section the goal needs and none it does not, so that the role finds all it needs and reads nothing it does not?

**Thinking**: Keep a section only where the role would fall short of the goal without it. Add one where a deliverable with every section would still fail the role.

**Steps**

1. Repeat until no such deliverable can be imagined.

### Q4: Judging a deliverable by a question, does the evaluator see what the role is after at that moment, so that it judges whether the role gets that, not whether the words are there?

**Thinking**: Write each question as the moment the role uses the sections, what it needs from them, and what it is after in that, in a clause that begins with "so that". The evaluator then judges by the role's intent. A question that asks only for a sign of good work can be met in words while the role goes without.

**Steps**

1. Leave out the "so that" clause only where what the role needs is the goal itself.
2. Have two evaluators judge one real deliverable by the question, and rewrite it where they differ.

### Q5: Going through the template, does the generator find a question for each section, each dependency among sections and the whole, so that no way the deliverable fails its role goes unasked?

**Thinking**: Give each section, each dependency among sections and the whole a question, and add one that fails each deliverable that would pass them all and still fail its role, as the questions are complete only when none such is left.

**Steps**

1. Where two questions would fail the same deliverables for the same reason, merge them, but keep a key one on its own.
2. Dig each question until it shows the idea the role must grasp, and ask whether the role grasps it, so that the template gives it a figure.
3. Judge real deliverables that their role found short, and where one passes, add or mend the question that should have failed it.

### Q6: Following a practice, does the generator grasp what the question's role is after and why, so that it makes what serves the role even where no step says how?

**Thinking**: Write first what the deliverable must be for the question's role, and why the role needs it so, in short sentences. A generator that grasps the intent finds its own way where the case differs. One that holds only steps follows them off the mark.

**Steps**

1. Add a step only where a generator that holds the intent would still not know how, such as a format to keep or a place to look, and say what the step achieves.
2. Where the content must be found before it is written, such as the roles of a product vision, say what to look at, how to find all of it, and when to ask the user.
3. Make one real deliverable by the practice, judge it by the question, and mend the intent where the answer stays no.

### Q7: Going through the questions in order, does the generator find a practice for each, so that it meets no question with nothing to go by?

**Thinking**: Order the questions so that each comes before those that build on it, and give each one practice in that order, as the generator then meets no question with nothing to go by.

### Q8: Reading the example, does the generator see what the template's slots become in one deliverable, so that it fills its own to the same intent?

**Thinking**: Make the product's own deliverable of the kind from its design tree by the template and the practices, pass it by the questions, and name its file in `example`, as one finished deliverable shows what the comments alone do not.

**Steps**

1. Where the deliverable lies elsewhere for its own reader, such as a product vision in the developers' folder, name its path in `source` and copy it with its figures beside the best practice by `plan.py example`, as a copy made by hand drifts from the deliverable, and a symbolic link shows as a line of text on GitHub and on Windows.

### Q9: Using a deliverable made by the best practice and passed, does its role achieve its purpose?

**Thinking**: Have the role, or an AI holding what it wants, use the example for the goal, and set its verdict against the evaluator's, as only a deliverable made and used shows whether the whole works.

**Steps**

1. Trace each difference to the goal, the template, a question or a practice, and mend it there.
2. Go through again with the next real deliverable.
