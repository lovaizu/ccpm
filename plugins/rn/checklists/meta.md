# Meta-checklist

This checklist is used by whoever makes or judges a checklist. A checklist is used by whoever judges
a deliverable of one kind, a person or an AI, answering its questions one by one while using the
deliverable as its user would, and by whoever makes the deliverable with it open. Each deliverable a
checklist passes is one its user achieves their purpose with.

## Format

```markdown
# <Kind of deliverable>

<Who uses the deliverable, and what they achieve with it, in one to three sentences>

## Format

<The template the deliverable follows>

## Questions

### Q-1: <What the user gets>

<A question answered yes or no by using the deliverable as its user would>

Why: <What holds for the user where the answer is yes, and what goes wrong for them where it is no>

Fails: <A deliverable's part that meets the question's words and misses its aim>

Passes: <The same part made to meet the aim>
```

A kind whose deliverable has no set shape, such as a fix, has no Format section. Each question's ID
is `Q-` and a number counted up from 1, in the order the questions stand; the tools that read a
checklist find each question by it. Fails and Passes stand under a question only where it has them.

## Questions

### Q-1: Who uses it, and for what

From the opening, can whoever makes or judges a deliverable tell who uses it and what they achieve
with it?

Why: each question asks what that user gets, so a judge who knows the user and their purpose judges
by them. The opening holds them alone, so a judge who goes straight to the questions loses nothing
the questions need.

### Q-2: The format the purpose needs

Does the format hold every part the purpose needs, and no part it does not?

Why: a missing part leaves the user unable to achieve the purpose, and a part with no use adds work
to every deliverable of the kind. The format is the least a deliverable holds, not a mould: a part
beyond it that its user uses is kept, as doc.md's "Every part used" asks.

### Q-3: The purpose and every element of the format, asked

Does every element the format holds, and every part of the purpose, have a question that asks what
the user gets from it, and does no question ask what neither needs?

Why: the questions are drawn from the purpose and the format, so each rests on what its user
achieves. An element no question asks passes unmet. A part asked of only one of its elements lets
the rest through, however many questions look at the part. A question beyond the purpose and the
format costs whoever makes and whoever judges each deliverable.

Fails: a UX checklist whose scenarios question asks whether the developer can point to a scenario,
so a document with two objectives and one scenario passes, and whose participants' kinds are said
only in a Why.

Passes: the same question asking, for each objective, what the user does first and who takes each
step, a person, an AI or a script, until they reach it.

### Q-4: One thing, answered yes or no

Does each question ask one thing, answered yes or no?

Why: a question asking two things has no answer for a deliverable that meets one of them.

### Q-5: A scene of use, the same answer from any judge

Does each question put the user in a concrete scene of using the deliverable, so that whoever
judges it gives the same answer?

Why: a judge given a scene takes the user's place in it and tries whether the deliverable answers
there. A question with no scene leaves each judge to choose the measure, so one deliverable passes
for one judge and fails for another. The scene names what the user does with the deliverable and
what that holds, so whether they succeed shows to anyone. A question about a state of mind, such as
whether the user grasps or pictures something, leaves each judge their own measure. A question about
the text, such as whether a part is there or a word is used, is met by the words while the user gets
nothing; a checkpoint names a criterion, not a mere indicator of it (Scriven, "The Logic and
Methodology of Checklists", 2007). A question that opens by narrowing where it holds, such as "where
the document tells of several that act in turn", passes whatever a judge calls outside it.

Fails: "Before reading any text, can the reader grasp the point of each section from a glance at its
figure?", whose "grasp" no one sees, so each judge measures it their own way.

Passes: "When a colleague asks 'What is it?', can the reader answer in one sentence?"

### Q-6: The aim, in each Why

Does each Why say what holds for the user where the answer is yes, and what goes wrong for them
where it is no?

Why: a judge who knows only a question's words passes a part that meets them and misses its aim. One
who knows the aim judges a case the words did not foresee, as a rule given with its reason is
followed where it was not foreseen (Anthropic, "Prompting best practices").

### Q-7: A case the words let through, shown

Where a part could meet a question's words and miss its aim, does the question show such a part as
Fails, and the same made right as Passes?

Why: judges are kept to one standard by examples of it more than by its words (NAEP, "Scoring
calibration"). A person learns the cases in training, and an AI judge has only the checklist. An
example comes from a case a judge let through, and is added once one is seen.

### Q-8: In the order the judge meets them

Do the questions stand in the order the judge meets what they ask in the deliverable, those on the
whole of it last?

Why: a judge reads the deliverable from the start, and questions in another order send them back and
forth, as a checklist follows the flow of the work it is used in (Barshi, Mauro, Degani and
Loukopoulou, "Designing Flightdeck Procedures", NASA/TM-2016-219421).

### Q-9: Every condition a question

Is each condition the deliverable must meet asked by a question, and said nowhere else in the
checklist?

Why: the judge answers the questions one by one, so a condition said only in the opening or under
the Format is checked by no one. One said in two places is changed in one of them and comes to say
two things.

Fails: an opening that says "how a part behaves in each case is decided where the part is built",
which no question asks.

Passes: the same said as a question's Why, the question asking whether each line is a decision the
approval rests on.
