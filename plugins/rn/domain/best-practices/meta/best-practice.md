# `meta`

## Goal

The generator can make deliverables with which their role achieves its purpose.

## Template

[template.json](template.json)

## Example

[../product-vision/best-practice.json](../product-vision/best-practice.json)

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | goal | Reading the goal, does the generator see the one end the deliverable's role is after, so that every part of the deliverable serves that end? |
| Q2 | template | Filling in the template, does the generator know what each section holds and in what order, so that the deliverable holds what its role uses and nothing more? |
| Q3 | goal, template | Setting the template against the goal, does the generator find each section the goal needs and none it doesn't, so that the role finds all it needs and reads nothing it doesn't? |
| Q4 | inputs, preconditions | Setting each section against what fills it, does the generator find the kinds it makes a deliverable from and those that must pass before it makes one, so that it makes no deliverable of the kind before what the deliverable takes? |
| Q5 | intents | Judging a deliverable by a question, does the evaluator see what the role is after at that moment, so that it judges whether the role gets that, not whether the words are there? |
| Q6 | template, intents | Going through the template, does the generator find a question for each section, each dependency among sections and the whole, so that no way the deliverable fails its role goes unasked? |
| Q7 | practices | Following a practice, does the generator grasp what the question's role is after and why, so that it makes what serves the role even where no step says how? |
| Q8 | intents, practices | Going through the questions in order, does the generator find a practice for each, so that it meets no question with nothing to go by? |
| Q9 | example, source | Reading the example, does the generator see what the template's slots become in one deliverable, so that it fills its own to the same intent? |
| Q10 | the whole | Using a deliverable made by the best practice and passed, does its role achieve its purpose? |

## Practices

### Q1

Reading the goal, does the generator see the one end the deliverable's role is after, so that every part of the deliverable serves that end?

**Thinking**

Write the end the deliverable's role is after as one sentence, with the role as its subject. Leave out what the deliverable holds, how the role reaches the end, and how it would show. The deliverable can meet each of these while the role misses the end.

**Steps**

1. Ask why of each part of the sentence until no further end shows, and keep that end.

### Q2

Filling in the template, does the generator know what each section holds and in what order, so that the deliverable holds what its role uses and nothing more?

**Thinking**

Write the template anew from the goal: a section for each thing the role uses toward the goal, fixed text for what every deliverable of the kind shares, and a slot for the rest. An AI writes past what a deliverable needs when it only gets an instruction not to, so the template leaves no room for more.

**Steps**

1. Where what the good deliverables hold is one way of doing it, such as a place, a file or a name, keep what the role gets from it instead.
2. Mark each slot so that its reader can tell it from fixed text and the page that shows the template keeps it, such as `` `<name>` `` in Markdown, as such a page drops a bare `<name>` as an HTML tag.
3. After each section, write one note saying for each slot what it holds, what its reader uses it for and whether it's optional, and open it with a marker by which the generator finds and deletes it. Write the note in the form the deliverable's format holds, such as a comment in Markdown or a key in JSON, which holds no comment. The generator fills a slot to its intent only when the note says it.
4. Where the deliverable has a JSON Schema of its own, such as the design tree, make the schema the template, its top fields the sections, and write each slot's note in the description of its field, as a second note beside the schema drifts from it.
5. Give the content found by digging a slot for its intent and why alone, in the fewest words, and a figure in place of prose wherever a figure can say it.
6. Draw each figure in a form that stays text, so that a change to it shows in a diff, such as Mermaid for a sequence and SVG for any other figure. A table counts as a figure too, as it stands in for prose.
7. Give each figure of the template a skeleton of its own that shows the figure's layout by the slots' names, with an alt text that holds no slot, and say in the section's note where the deliverable puts its own figure. A figure that the template names but doesn't hold shows broken, and the example's figure shows one product's content in place of the layout.
8. Name the template's file in `template`.

### Q3

Setting the template against the goal, does the generator find each section the goal needs and none it doesn't, so that the role finds all it needs and reads nothing it doesn't?

**Thinking**

Keep a section only where the role would fall short of the goal without it. Add one where a deliverable with every section would still fail the role.

**Steps**

1. Repeat until you can imagine no such deliverable.

### Q4

Setting each section against what fills it, does the generator find the kinds it makes a deliverable from and those that must pass before it makes one, so that it makes no deliverable of the kind before what the deliverable takes?

**Thinking**

Name in inputs each kind whose deliverables the generator makes a deliverable of this kind from, and in preconditions each kind whose deliverables must pass before it makes one of this kind, each by the name of its best practice's folder. The plan holds each deliverable's own inputs and preconditions, the paths of the deliverables it takes, to these kinds, and orders it after them. A kind left out lets the generator make a deliverable on what isn't there yet, and a kind named without need holds the deliverable back.

### Q5

Judging a deliverable by a question, does the evaluator see what the role is after at that moment, so that it judges whether the role gets that, not whether the words are there?

**Thinking**

Write each question as the moment the role uses the sections, what it needs from them, and what it's after in that, in a "so that" clause. The evaluator then judges by the role's intent. A deliverable can meet a question that asks only for a sign of good work with words alone, while the role goes without.

**Steps**

1. Leave out the "so that" clause only where what the role needs is the goal itself.

### Q6

Going through the template, does the generator find a question for each section, each dependency among sections and the whole, so that no way the deliverable fails its role goes unasked?

**Thinking**

Give each section, each dependency among sections and the whole a question, and add one that fails each deliverable that would pass them all and still fail its role, as the questions are complete only when none such remains.

**Steps**

1. To better a best practice, start from what stands: keep its questions, take in what research shows missing, and drop a question only for a reason in its role's purpose. A best practice made anew loses what its use has taught it.
2. Where two questions would fail the same deliverables for the same reason, merge them, but keep a key one on its own.
3. Dig each question until it shows the idea the role must grasp, and ask whether the role grasps it, so that the template gives it a figure.
4. Judge real deliverables that their role found short, and where one passes, add or mend the question that should have failed it.

### Q7

Following a practice, does the generator grasp what the question's role is after and why, so that it makes what serves the role even where no step says how?

**Thinking**

Write first what the deliverable must be for the question's role, and why the role needs it so, in short sentences. A generator that grasps the intent finds its own way where the case differs. One that holds only steps follows them off the mark. Take each practice from the way the field has established for its case, found by research, and name its source, as a way reasoned out alone misses what the field has learned. Call an established idea by its established name, such as single responsibility or Given-When-Then, with why it serves the role, as the name carries the field's knowledge to a maker who knows it. Write the practice for any language and tool that makes the kind, and name one only as an example. Give the intent, its established ways and when each fits, and leave the way and the tool for each deliverable to its plan, as a practice tied to one tool fails a deliverable made with another.

**Steps**

1. Add a step only where a generator that holds the intent would still not know how, such as a format to keep or a place to look, and say what the step achieves.
2. Give each step its trace, the call that shows it done: a command it runs, a file it reads to its end, or a file it makes. Order the steps as their calls come, as a checker such as Lane holds the role to each step by its trace alone, in the steps' order, and holds its end until each trace comes back. Leave the trace out in two cases. One is where some runs rightly skip the call, such as on a step of a case, as Lane would stop the end of each such run. The other is where no call shows the action, such as a judgment, which the evaluator then checks.
3. Where the generator must find the content before it writes it, such as the roles of a product vision, say what to look at, how to find all of it, and when to ask the user.

### Q8

Going through the questions in order, does the generator find a practice for each, so that it meets no question with nothing to go by?

**Thinking**

Order the questions so that each comes before those that build on it, and give each one practice in that order, as the generator then meets no question with nothing to go by.

### Q9

Reading the example, does the generator see what the template's slots become in one deliverable, so that it fills its own to the same intent?

**Thinking**

Make the product's own deliverable of the kind from its design tree by the template and the practices, pass it by the questions, and name its file in `example`, as one finished deliverable shows what the comments alone don't.

**Steps**

1. Where the deliverable lies elsewhere for its own reader, such as a product vision in the developers' folder, name its path in `source`. Copy it with its figures beside the best practice by a script, such as ccpm's `dev/scripts/practices.py example`. A copy made by hand drifts from the deliverable, and a symbolic link shows as a line of text on GitHub and on Windows.

### Q10

Using a deliverable made by the best practice and passed, does its role achieve its purpose?

**Thinking**

Read the best practice whole and judge two things: that each question asks what its user essentially intends, and that a maker follows each practice without hesitation. Judge by reading, not by a method or a count, as a method of judging adds work and shows nothing that the reading doesn't. No best practice covers every case at first. Once the product vision trial shows the deliverables closer to the goal, ship it and better it in use, as Q6 says.

**Steps**

1. Where a deliverable in use falls short of its role, trace the cause to the goal, the template, a question or a practice, and mend it there.
