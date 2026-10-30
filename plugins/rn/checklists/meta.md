# Meta-checklist

A checklist is made for one kind of deliverable. Whoever makes the checklist decides the format and
the conditions of a deliverable with which its user achieves their purpose, and the essential
questions that tell whether a deliverable meets them. Whoever judges a deliverable uses it as its
user would and answers the questions.

A checklist is drawn in this order: the user's purpose and the deliverable, then the deliverable's
format and conditions, then the questions that judge them. Each step comes from the one before it.
A condition is written as a question, so it is said once.

## Format

```markdown
# <Kind of deliverable>

<Who uses the deliverable, and what they achieve with it>

<How the format and the questions were drawn from that purpose>

## Format

<The template the deliverable follows>

## Questions

### Q-1: <What is judged>

<A question answered yes or no>

Why: <What goes wrong for the user without it>
```

A kind whose deliverable has no set shape, such as code, has no Format section. Each question's ID
is `Q-` and a number counted up from 1; the tools that read a checklist find each question by it.

## Questions

### Q-1: Purpose

From the opening, can whoever makes or judges a deliverable tell who uses it and what they achieve
with it?

Why: the format and the questions are drawn from the purpose; where it is not told, they have
nothing to be drawn from.

### Q-2: Format

Does the format hold every part the purpose needs, and no part it does not?

Why: a missing part leaves the user unable to achieve the purpose, and a part with no use adds work
to every deliverable of the kind.

### Q-3: Conditions

Do the questions ask every condition the purpose needs, and no condition it does not?

Why: a condition no question asks passes unmet, and a question beyond the purpose costs whoever
makes and whoever judges each deliverable.

### Q-4: Each question

Does each question ask one thing, answered yes or no by using the deliverable as its user would?

Why: a question asking two things has no answer for a deliverable that meets one of them, and a
question that using the deliverable cannot answer is judged by whether something is written.
