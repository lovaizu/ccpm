# meta

## Goal

A best practice it makes produces deliverables that achieve their user's purpose.

## Parts

- **goal**: What the user achieves with the deliverable.
- **template**: `<kind>-template.md`, in the deliverable's own format: its sections in the order the user meets them, the text that is the same in every deliverable of the kind, a slot `<name>` for the rest, and after each section one comment saying what each slot holds.
- **example**: `<kind>-example.md`: Turn's own deliverable of the kind, made from Turn's design tree by the template and the practices.
- **benefits**: Questions that check, by the essence, whether the deliverable achieves the goal. They ask what each section of the template, each dependency among sections and the whole bring the user. Each is answered yes or no, and they stand in the order the generator thinks them.
- **practices**: For each question, in the benefits' order, the best way of thinking that meets its essence, and steps only where the thinking alone does not lead the generator, with the grounds where they have worked.

## Benefits

- **Q1** (goal): Reading the goal, does one see a single thing the user achieves with the deliverable?
- **Q2** (template): Looking at the template, does the generator know what to write in which section, in what order, and nothing else?
- **Q3** (goal, template): Do the template's sections hold, neither more nor less, what the goal needs?
- **Q4** (benefits): With each question, can one who judges the deliverable tell whether that part serves the user?
- **Q5** (template, benefits): For each section, each dependency among sections and the whole, is there a question asking whether it serves the user?
- **Q6** (practices): Following the way of thinking and the steps, can the generator make the content the question asks for?
- **Q7** (benefits, practices): Does every question have, in the benefits' order, a way of thinking that meets its essence?
- **Q8** (example, the whole): Does a deliverable made by this best practice, and passed, let its user achieve their purpose?

## Practices

### Q1: Reading the goal, does one see a single thing the user achieves with the deliverable?

**Thinking**: The goal is what the user is trying to get done, seen from where they stand, not what the deliverable holds.

**Steps**

1. Name the one who uses the deliverable.
2. Ask what they are trying to get done when they reach for it.
3. Write that as one sentence with them as its subject, free of what the deliverable holds or how it is made.
4. Ask whether two readers would name the same achievement from it. Where they would name two, keep the one the other serves.

**Grounds**

- [The Goal Question Metric Approach](https://www.cs.umd.edu/~mvz/handouts/gqm.pdf), Basili, Caldiera and Rombach, University of Maryland: "A goal is defined for an object, for a variety of reasons, with respect to various models of quality, from various points of view, relative to a particular environment."
- [Jobs to Be Done (JTBD): The Original Framework by Tony Ulwick](https://strategyn.com/jobs-to-be-done/), Strategyn, strategyn.com, 2024: "Identify who is executing the job and define the core functional job in a single, solution-free statement."

### Q2: Looking at the template, does the generator know what to write in which section, in what order, and nothing else?

**Thinking**: Good and poor deliverables of the kind teach what it holds, and the template fixes it: an AI writes past what the task needs when only told not to, so the form leaves room for what the goal needs alone.

**Steps**

1. Gather good and poor deliverables of the kind, and list what the good ones hold that their user uses toward the goal.
2. For each such thing that is one way of doing it, such as a place, a file or a name, ask what its user gets from it, and keep that instead.
3. Write the template anew from the goal and that list, not from an old deliverable or draft: a section for each thing kept, in the order the user meets them.
4. Write as fixed text only what is the same in every deliverable of the kind, and a slot `<name>` for the rest.
5. After each section, write one comment saying only what each slot holds, and whether it is optional; the how and the why go to the practices. Open the template with the comment "Delete every comment once the document is written."
6. Draw a sequence in Mermaid and any other figure in SVG, and write a table in Markdown.

**Grounds**

- [Using Rubrics to Promote Thinking and Learning](https://ascd.org/el/articles/using-rubrics-to-promote-thinking-and-learning), Andrade, Educational Leadership, 2000: "Look at models. Review examples of good and poor work on a project like the one your students are about to undertake."
- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/raw/main/README.md), The Good Docs Project, gitlab.com/tgdp/templates, README.md, no date: "The template file is the raw template for the content type. It provides a rough outline of the suggested content and a few embedded writing tips for how to fill in the different sections of the template."
- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/raw/main/README.md), The Good Docs Project, gitlab.com/tgdp/templates, README.md, no date: "This guide provides a deeper explanation of how to fill in the template."
- [Download arc42](https://arc42.org/download), arc42, arc42.org, no date: "Plain gives you the bare structure."
- [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5), Anthropic, Claude Platform Docs, no date: "files that Claude Opus 5 writes to disk (reports, Markdown documents, summaries) are often longer than on prior models."

### Q3: Do the template's sections hold, neither more nor less, what the goal needs?

**Thinking**: Each section is there because the goal needs it, and a deliverable imagined with every section that still fails its user shows what the goal needs.

**Steps**

1. For each section, say what the user could not do toward the goal without it. Cut a section with no answer.
2. Imagine a deliverable that has every section and still fails its user, and make what it lacks a section.
3. Repeat until no such deliverable can be imagined.

**Grounds**

- [The Goal Question Metric Approach](https://www.cs.umd.edu/~mvz/handouts/gqm.pdf), Basili, Caldiera and Rombach, University of Maryland: "This means that measurement must be defined in a top-down fashion."
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "Then one tries to construct hypothetical cases in which an entity has all the properties in the proposed comlist but still lacks something that would be required or important in order to justify an assignment of merit."
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The list should be concise (to assist its mnemonic function); i.e., it should contain no superfluous criteria."

### Q4: With each question, can one who judges the deliverable tell whether that part serves the user?

**Thinking**: A question asks whether the user gets what they need, not whether a sign of good work is there, so it cannot be met in the letter while the user goes without.

**Steps**

1. Name who uses what the question asks of, and the moment they use it.
2. Ask what they need from it there toward the goal.
3. Write the question as whether they get that, answered yes or no.
4. Ask whether a deliverable could meet the question's words while the user still does not get it. If so, rewrite the question to ask whether the user gets it.
5. Ask whether the question says more than whether the work is good. If not, name what the user gets.
6. Have two evaluators judge one real deliverable by the question. Where they differ, rewrite the question until every evaluator reads it one way.

**Grounds**

- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The checkpoints should refer to criteria and not mere indicators"
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "indicators are easily corrupted, and once it becomes known that they are being used as an indicator for something important in an evaluation, people are very ingenious about faking the score on them"
- [What's Wrong—and What's Right—with Rubrics](https://ascd.org/el/articles/whats-wrong-and-whats-right-with-rubrics), Popham, Educational Leadership, 1997: "In essence, these overly general criteria allow both teachers and students to conclude that really good student responses to the task are, well, really good."
- [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/), Husain, hamel.dev, 2024: "You need to be able to say “this interaction passed because…” and “this interaction failed because…”."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "A good task is one where two domain experts would independently reach the same pass/fail verdict."

### Q5: For each section, each dependency among sections and the whole, is there a question asking whether it serves the user?

**Thinking**: The questions are complete when no deliverable can pass them all and still fail its user, and they ask each need in one place.

**Steps**

1. List each section of the template, each pair of sections where one depends on another, and the whole.
2. Give each one its question.
3. Merge questions that would fail the same deliverables for the same reason, keeping a key one on its own.
4. Imagine a deliverable that passes every question and still fails its user, and add the question that would fail it.
5. Judge real deliverables their users found short. Where one passes, add or mend the question that should have failed it.

**Grounds**

- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The list should be complete (no significant omissions)."
- [The Logic and Methodology of Checklists](https://wmich.edu/sites/default/files/attachments/u350/2014/logic%26methodology_dec07.pdf), Scriven, Western Michigan University, 2007: "The items should be contiguous, i.e., nonoverlapping"
- [Using Rubrics to Promote Thinking and Learning](https://ascd.org/el/articles/using-rubrics-to-promote-thinking-and-learning), Andrade, Educational Leadership, 2000: "After class, take time to combine criteria. Avoid creating categories that are too big, and don't bury criteria that you want to emphasize."
- [Key Evaluation Checklist](https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf), Scriven, Western Michigan University, 2007: "We can describe this as a case where they failed to clear a holistic (or overall) bar that was implicit in this example, but can often be made explicit through dialog."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "Converting user-reported failures into test cases ensures your suite reflects actual usage"

### Q6: Following the way of thinking and the steps, can the generator make the content the question asks for?

**Thinking**: A way of making comes from where it has met the essence before, and it stays only once it meets the essence here; the way of thinking carries it, and a step stands only for what the thinking alone does not lead the generator to.

**Steps**

1. For the essence the question holds, find how good deliverables met it: guides, studies and examples.
2. Write the way of thinking in one sentence.
3. Write a step only for what the way of thinking alone does not lead the generator to, one action each, in order.
4. Where a step or a source names one way of doing it, such as a place, a file or a tool, write what that way achieves, so a project that achieves it another way keeps its own.
5. Add as grounds the words of the sources, quoted from the pages opened, each with its page's title and link. Cut a step that no source holds and the way of thinking already implies.
6. Make one real deliverable by the way, and judge it by the question. Where the answer stays no, mend the way.

**Grounds**

- [Key Evaluation Checklist](https://wmich.edu/sites/default/files/attachments/u350/2014/key%20evaluation%20checklist.pdf), Scriven, Western Michigan University, 2007: "This is an iterative checklist, not a one-shot checklist."

### Q7: Does every question have, in the benefits' order, a way of thinking that meets its essence?

**Thinking**: Every essence of every question has its way, so the generator never meets a question with nothing to go by.

**Steps**

1. Order the questions in the order the generator thinks them, so that one is answered before those that build on it.
2. Give each question one practice, in that order, and make one by Q6's way for a question that has none.

### Q8: Does a deliverable made by this best practice, and passed, let its user achieve their purpose?

**Thinking**: Only a deliverable made and used shows whether the whole works, and a verdict by the questions is measured against the user's own verdict; Turn's own deliverable of the kind, made the way Turn makes one, is that deliverable and the example.

**Steps**

1. Make Turn's own deliverable of the kind from Turn's design tree by the template and the practices, keep it as `<kind>-example.md`, and pass it by the benefits.
2. Have its user, or an AI holding what the user wants, use it for the goal.
3. Set the user's verdict against the evaluator's.
4. Trace each difference to the goal, the template, a question or a practice, and mend it there.
5. Go through again with the next real deliverable.

**Grounds**

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Anthropic, anthropic.com/engineering, 2026: "LLM-as-judge graders should be closely calibrated with human experts"
- [Who Validates the Validators?](https://arxiv.org/abs/2404.12272), Shankar et al., arXiv:2404.12272, 2024: "users need criteria to grade outputs, but grading outputs helps users define criteria."
- [Using LLM-as-a-Judge For Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/), Husain, hamel.dev, 2024: "You cannot write a good judge prompt until you’ve seen the data."
- [The Good Docs Project templates](https://gitlab.com/tgdp/templates/-/raw/main/README.md), The Good Docs Project, gitlab.com/tgdp/templates, README.md, no date: "See an example of the template in action in our model documentation project: The Chronologue."
