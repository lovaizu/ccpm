# Design tree: meta

Made by hand from [meta.json](meta.json), the original; a script will make it once the view is
settled. `you` is decided by the user, `reasoned` by the purpose and best practice, `fact` by
research.

**Goal:** A builder makes a deliverable of a kind by its best practice's Practice, and an evaluator
judges it against the Standard alone; every deliverable that passes is fit for its user's purpose.

## Yours to decide

- **D16** How is the root question judged? → _open_

## Tree

- **Q1 standard** Given only the deliverable and the standard, can an evaluator decide whether the
  deliverable is done?
  - **D3** How is a best practice kept? `you`<br>
    One file for each kind, best-practices/<kind>.json, holding standard and practice.
  - **D4** What are its keys named? `you` · after D3<br>
    The README's words: standard (goal, template, checklist, includes) and practice (methods).
  - **D12** What is the evaluator given? `you` · after D4<br>
    The standard alone, taken out of the file by a script.
- **Q2 goal** When asked "Who uses such a deliverable, and for what?", can the builder answer from
  the goal alone?
  - **D1** Who uses a best practice? `reasoned`<br>
    The builder, who makes a deliverable by the Practice, and the evaluator, who judges it by the
    Standard; both AIs. Planner makes it, and the user approves its goal and checklist.
  - **D2** The goal as written `reasoned` · after D1<br>
    The goal above.
- **Q3 template** Does every part of the template reach the goal through the part it serves, and
  does the goal need no part the template lacks?
  - **D15** What way of thinking does the whole rest on? `you`<br>
    Think from the purpose: divide and give meaning, build in order, see across the branches.
  - **D5** What shape does the template take? `you` · after D4, D15<br>
    A tree drawn from the goal: each part has id, what, why (what it serves) and parts, its
    children.
- **Q4 checklist** Does every part of the template, and the goal at its root, have one question
  asking of it?
  - **D6** How do the questions meet the template? `you` · after D5<br>
    One question on each part and one on the root; each question's about names that one part.
- **Q5 question** Placed in a question's scene, do two evaluators give the same yes or no for the
  same deliverable?
  - **D7** What form does a question take? `reasoned`<br>
    A scene of use, "When <the user> <does>, can they <result>?", answered yes or no, asking one
    thing.
- **Q6 why** Faced with a case the question's words did not foresee, can the evaluator judge it
  from the why?
  - **D8** What does a why say? `reasoned` · after D7<br>
    What holds for the user where the answer is yes, and what goes wrong for them where it is no.
- **Q7 examples** Shown a part that meets a question's words and misses its aim, can the evaluator
  tell from the examples that it fails?
  - **D9** When does a question carry examples? `reasoned` · after D7<br>
    Where a part can meet its words and miss its aim: fails from a case a judge let through, passes
    the same made right.
- **Q8 grounds** Can a reader find, in the source each ground names, the words it quotes?
  - **D10** What form does a ground take? `reasoned`<br>
    Author, "Title", venue, year: the words quoted that the claim rests on.
- **Q9 includes** When a question shared by several kinds changes, is it changed in one file only?
  - **D11** Where do questions shared by kinds live? `you` · after D3<br>
    In refactor-doc and refactor-code, named in includes; meta includes refactor-doc.
- **Q10 practice** Following the practice alone, can a builder make every question yes without
  guessing?
  - D3, D4 _(under Q1)_
  - **D13** How are methods kept? `you` · after D4<br>
    One for each question: question, steps and grounds.
- **Q11 method steps** Following a method's steps, do two builders make the same kind of result?
  - D13 _(under Q10)_
  - **D14** What form does a step take? `reasoned` · after D13<br>
    In order, one imperative action each, naming the part of the template it writes.
- **Q12 method grounds** Can a reader find, in each source a method names, that its way has worked?
  - D10 _(under Q8)_
- **Q13 the whole** Is a deliverable built by this best practice's Practice, and passed by its
  Standard, fit for its user's purpose?
  - D15 _(under Q3)_
  - **D16** How is the root question judged? `you` · after D15<br>
    _open_
