# What turn/scripts/questions.py does

## code

### B-1: Tests hold what the code must do
- The module holds the questions only the user can decide, kept by a run in `questions.json` in the
  run's work folder, a list of questions, each a JSON object.
- `asked(work)` gives that list, read with `read_json` from `state`.
- `asked_numbers(work)` gives the numbers, counted from 1, of the questions left open: those whose
  `ask` is true.
- `left_open(work)` gives the words of each question left open, which the run asks the user at its
  end.
- `question_faults(work, decided)` gives, in order, one line for each fault, and none when there is
  none:
  - the questions not a list: `the questions are not a list`, and nothing else;
  - a question that is not an object or has no words: `question <k>: the question is not given`;
  - a question naming an item of the run's list (`list.json` in the work folder, items with `id`
    such as `doc B-2`) by the item's ID: `question <k>: names <id>; say in plain words what the work
    leaves out`, since the user would have to learn the checklist;
  - once `decided` is true, a question whose `ask` is not true or false: `question <k>: not
    decided`;
  - once `decided` is true, a question not left open (`ask` false) with no `answered`, where it is
    answered: `question <k>: where it is answered is not given`.
- Its tests are in `dev/turn/tests/test_questions.py`, run with
  `python3 -m unittest discover -s dev/turn/tests`.
