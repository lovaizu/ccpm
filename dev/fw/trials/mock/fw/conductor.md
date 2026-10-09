# What mock makes

The user wants two questions answered for their friend Sam. Each answer is one task; the two do not
depend on each other, so run their tasks at the same time.

Each work goes at the root of the repository.

| Task | Question | Work |
|---|---|---|
| sum | What is 1+1? | `sum.txt` |
| colour | What colour is the opposite of red? | `colour.txt` |

- Receiver: Sam, who asked the question and reads the answer once.
- Acceptance: Sam can read each answer and use it without asking anything.
- Language: English.

This file, and `make.md` for each answer, settle everything the steering and the maker need, as
their sources; agree to what the maker says it will do. Judge a work only from the first user's
report, never from the maker's reply or from reading the work yourself. Ask the user nothing but
the approval of the steering.
