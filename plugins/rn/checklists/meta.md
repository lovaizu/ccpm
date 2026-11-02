# Meta-checklist

This checklist is used by whoever makes or judges a checklist. A checklist is used by whoever judges
a deliverable of one kind, a person or an AI, answering its questions one by one while using the
deliverable as its user would, and by whoever makes the deliverable with it open. Each deliverable a
checklist passes is one its user achieves their purpose with.

## Think from the purpose

Every checklist, and every deliverable made with one, is thought out this way (Descartes, Discourse
on the Method, 1637, rules two to four; Simon, "The Architecture of Complexity", 1962).

1. Divide and give meaning. Split the purpose into what must hold for it, and each of those again,
   until a fact or the user settles it. Name each part by what it serves. A part that reaches no
   purpose serves nothing and is cut.
2. Build in order. Put the parts together, each after those it rests on, and check each as it is
   put in.
3. See across the branches. One part serves several others, and one rests on another in a different
   branch. Once it is whole, judge the whole by its purpose.

## Format

```markdown
# <Kind of deliverable>

<Who uses the deliverable, and what they achieve with it, in one to three sentences>

## Format

<The template the deliverable follows>

## Questions

### Q-1: <The part of the format it asks about, or The whole>

<A question answered yes or no by using the deliverable as its user would>

Why: <What holds for the user where the answer is yes, and what goes wrong for them where it is no>

Fails: <A deliverable's part that meets the question's words and misses its aim>

Passes: <The same part made to meet the aim>
```

A kind whose deliverable has no set shape, such as a fix, has no Format section. Each question's ID
is `Q-` and a number counted up from 1, in the order the questions stand; the tools that read a
checklist find each question by it. Fails and Passes stand under a question only where it has them.

## Questions

### Q-1: The opening

From the opening, can whoever makes or judges a deliverable tell who uses it and what they achieve
with it?

Why: each question asks what that user gets, so a judge who knows the user and their purpose judges
by them. The opening holds them alone, so a judge who goes straight to the questions loses nothing
the questions need.

### Q-2: The Format

Is the format a tree drawn from the purpose, each element under the element it serves, and does
every element reach the purpose?

Why: a missing element leaves the user unable to achieve the purpose, and an element that reaches
no purpose adds work to every deliverable of the kind and serves nothing. An element no branch joins
to the purpose is the sign of one to cut. The format is the least a deliverable holds, not a mould:
a part beyond it that its user uses is kept, as doc.md's "Every part used" asks.

### Q-3: The questions, one on each element

Does each element of the format's tree, and its root, the purpose, have one question that asks
whether the user gets from it what it serves, and does each question ask of one of them?

Why: the questions are drawn from the purpose through the format, so each rests on what its user
achieves. An element no question asks passes unmet, and a question asked only of an element's
children lets the element itself through: objectives can each be good while two of them say the
same, so a developer cannot tell which one a change serves. The question on the root judges the whole by its purpose. A question
that asks of no element shows an element the format lacks, or a question the purpose does not need.

Fails: a UX checklist with questions on the objectives, the key results and the scenarios, but none
on the OKRs or the Scenarios as a whole, and the participants' kinds said only in a Why.

Passes: the same checklist with a question on each of the OKRs, an objective, a key result, the
Scenarios, the participants and a scenario, and one on the whole document.

### Q-4: Each question, one thing

Does each question ask one thing, answered yes or no?

Why: a question asking two things has no answer for a deliverable that meets one of them.

### Q-5: Each question, a scene of use

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

### Q-6: Each Why

Does each Why say what holds for the user where the answer is yes, and what goes wrong for them
where it is no?

Why: a judge who knows only a question's words passes a part that meets them and misses its aim. One
who knows the aim judges a case the words did not foresee, as a rule given with its reason is
followed where it was not foreseen (Anthropic, "Prompting best practices").

### Q-7: Fails and Passes

Where a part could meet a question's words and miss its aim, does the question show such a part as
Fails, and the same made right as Passes?

Why: judges are kept to one standard by examples of it more than by its words (NAEP, "Scoring
calibration"). A person learns the cases in training, and an AI judge has only the checklist. An
example comes from a case a judge let through, and is added once one is seen.

### Q-8: The questions, in order

Do the questions stand in the order the judge meets what they ask in the deliverable, those on the
whole of it last?

Why: a judge reads the deliverable from the start, and questions in another order send them back and
forth, as a checklist follows the flow of the work it is used in (Barshi, Mauro, Degani and
Loukopoulou, "Designing Flightdeck Procedures", NASA/TM-2016-219421).

### Q-9: The whole, every condition a question

Is each condition the deliverable must meet asked by a question, and said nowhere else in the
checklist?

Why: the judge answers the questions one by one, so a condition said only in the opening or under
the Format is checked by no one. One said in two places is changed in one of them and comes to say
two things.

Fails: an opening that says "how a part behaves in each case is decided where the part is built",
which no question asks.

Passes: the same said as a question's Why, the question asking whether each line is a decision the
approval rests on.
