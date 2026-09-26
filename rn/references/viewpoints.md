# Viewpoints

What each thing a session makes must reach. The implementer reads a section as what to reach and
checks their work against it; the evaluator reads the same section as what to evaluate, so both look
at the same thing. Each section asks first whether it reaches its Goal or Purpose, then splits that
down, then guards what it must not break.

## Plan

`steering.md`, as first written or as revised since. Past the start, the work done so far is its
ground.

- **Would it reach the Goal?** Carried out, it leads to the Goal the user agreed, as far as their next
  decision.
- **Does "Goal reached when" cover the Goal?** If every line held, the Goal would be reached.
- **Do the tasks cover "Goal reached when"?** Every line is served by a task's Purpose, or is plainly
  left to the tasks written after the decision that ends the plan.
- **Does each "Purpose reached when" cover its Purpose?** If every line held, the Purpose would be
  reached.
- **Can each line be told on the real thing?** Each line of both is a state checked on the real
  thing, not an artifact or a step, so it holds if the means change.
- **Do the tasks end at the user's decision?** They reach the sign-off that ends them, none goes past
  it, and that sign-off is the user's: a design, where the work changes what the product should be
  or a decision of taste, scope, or cost against benefit comes up, or the finished work.
- **Is what it rests on true?** Each Fact was checked; no Assumption hides work or an open decision.
- **Are the conventions recorded?** The Rules hold what the tasks must follow and an implementer could
  not know from the Goal.

## Design

The README and the design document the `design` field names, against the Goal and the work so far.
Both say what the product should be once built: the work is built toward them, and they are changed
first when it must change, never to match the work.

| Document | Read by | Tells | After reading, the reader can |
|---|---|---|---|
| README | a user new to the product | the benefit, and how to use it | tell what it does for them, decide to use it, and start |
| design document | those who build or fix it, people and AI | how the product reaches what the README says | tell how, and whether a change fits the design, and why not when it does not |

They hold what the product should be, and the reasons, costs, and assumptions behind it; not what
the implementation may choose freely while both hold (how the code is split, names of files and
functions, the shape of internal data), except what a user sees: what they install, where it runs,
the words on the screen. Headings follow the order the reader asks in, each a question or its
answer. Detailed steps of use may sit in a file the README links, held to README 2–6 and to both.

Both:

- **Can its reader do what it is for?** Read top to bottom as its reader, they can do what the table
  says, without stumbling, and nothing in it is for someone else.
- **Nothing the implementation may choose freely?** Rebuilding the implementation leaves them as they
  are.
- **Do the headings alone carry the thread?** No "Overview" or "Other".
- **Is a table only for comparing?** A line of reasoning is not cut into table cells.
- **Only how it stands, no history?** No "used to" or "changed to".

README:

1. **Does the benefit come first?** The opening says what gets easier and what stops happening, not a
   list of features or how it is made.
2. **Is it written as the finished product?** Use as it will be, with no "for now", "not yet", or
   "planned".
3. **Is the flow seen at a glance?** The stages from start to result, and what each does and gives,
   not buried under detailed steps.
4. **Are the reasons left to the design document?** Why it takes this shape is a link, not an
   explanation.
5. **Can it be read with no prior knowledge?** Each word is clear where it first appears.
6. **Can the reader start?** How to get it and start, and on what terms (License).

Design document:

1. **Does it say what it is?** The opening says it is how the README is reached, and that where the
   implementation differs, it is right.
2. **Does it state its principles?** A few principles of how it is built, each one sentence, followed
   at once by what goes wrong without it, traced to the README or to a condition the design cannot
   change, such as where it runs or who uses it. A rule of one feature is not among them.
3. **Does it have a frame?** In the order a fixer asks: roles and their bounds (who does and decides
   what), states and operations (what states there are, and how operations move them), the grounds of
   each decision (what is looked at to go one way or another), and what is kept (what stays, who writes
   it, who reads it). A decision is its grounds, not a list of outcomes by case.
4. **Are the conditions that always hold named?** What must hold after every operation, where it can
   be seen as such.
5. **Are the costs, and the ways not taken, there?** What was given up, and why another way is not
   taken, as a comparison that holds now.
6. **Are only names seen from outside used?** Names a user sees, and what is agreed with the outside
   (the form of what is saved or handed on); no code file or function names.
7. **Are facts, assumptions, and decisions apart?** What was checked is stated, what was not is an
   assumption, and what was decided is a decision.

A More is how it is written (fixed in the document), where it sits (moved to the document whose role
fits, or removed when neither fits), or what it says (the design itself must change: two claims
disagree, or a rule has a gap). A More of what it says is the user's; name it as such, not worded
around.

## Task result

One task's commits, and the files they touch as they stand now, against that task.

- **Is the Purpose reached?** On the real thing, run where it runs, every line of Purpose reached when
  holds, and the Purpose holds beyond their letter.
- **Is nothing added?** Nothing beyond what reaching the Purpose needs.
- **Does it follow the design?** Where the `design` field names documents, the work is what they say.
- **Are the Rules followed?**
- **Does what worked still work?**

## Finished work

Everything the session changed apart from its directory under `.rn/`, against the Goal.

- **Is the Goal reached?** Beyond the letter of Goal reached when; a gap in those lines the work has
  since exposed is named.
- **Does every line of Goal reached when hold?** On the real thing, run where it runs.
- **Do the README and the design document say what was built?** Where the `design` field names them.
- **Are the Rules followed?** Across the whole change.
- **Is only the work left behind?** Besides the work, only the session's directory under `.rn/`.
